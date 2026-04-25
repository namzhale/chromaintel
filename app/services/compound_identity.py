from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from app.adapters.base import load_table
from app.services.descriptors import DescriptorCalculator, InvalidStructureError


CONFIDENCE_ORDER = {
    "exact_inchikey": 100,
    "inchikey_first_block": 90,
    "pubchem_cid": 80,
    "chembl_id": 70,
    "name_low": 20,
}

REPORT_COLUMNS = [
    "status",
    "confidence",
    "reason",
    "query_name",
    "query_smiles",
    "query_inchikey",
    "query_pubchem_cid",
    "query_chembl_id",
    "candidate_count",
    "candidate_names",
    "candidate_pubchem_cids",
    "candidate_chembl_ids",
]


@dataclass(frozen=True)
class IdentityResolution:
    status: str
    confidence: str
    query: dict[str, Any]
    candidate: dict[str, Any] | None = None
    candidates: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""

    def report_record(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "confidence": self.confidence,
            "reason": self.reason,
            "query_name": self.query.get("name"),
            "query_smiles": self.query.get("smiles"),
            "query_inchikey": self.query.get("inchikey"),
            "query_pubchem_cid": self.query.get("pubchem_cid"),
            "query_chembl_id": self.query.get("chembl_id"),
            "candidate_count": len(self.candidates),
            "candidate_names": "|".join(str(candidate.get("name", "")) for candidate in self.candidates),
            "candidate_pubchem_cids": "|".join(
                str(candidate.get("pubchem_cid", "")) for candidate in self.candidates
            ),
            "candidate_chembl_ids": "|".join(str(candidate.get("chembl_id", "")) for candidate in self.candidates),
        }


def load_identity_cache(path: str | Path) -> tuple[dict[str, Any], ...]:
    """Load an offline identity fixture or cache table once per path."""

    return _load_identity_cache(str(Path(path).resolve()))


def clear_identity_cache() -> None:
    _load_identity_cache.cache_clear()


@lru_cache(maxsize=16)
def _load_identity_cache(resolved_path: str) -> tuple[dict[str, Any], ...]:
    frame = load_table(resolved_path)
    return tuple(_normalize_cache_row(row) for row in frame.to_dict("records"))


class CompoundIdentityResolver:
    """Resolve compound identity from local PubChem/ChEMBL-style cache rows."""

    def __init__(
        self,
        cache_path: str | Path,
        *,
        allow_ambiguous_name: bool = False,
        descriptor_calculator: DescriptorCalculator | None = None,
    ) -> None:
        self.rows = load_identity_cache(cache_path)
        self.allow_ambiguous_name = allow_ambiguous_name
        self.descriptor_calculator = descriptor_calculator or DescriptorCalculator()

    def resolve(self, query: dict[str, Any]) -> IdentityResolution:
        normalized_query = self._normalize_query(query)
        for confidence, matcher in (
            ("exact_inchikey", self._match_exact_inchikey),
            ("inchikey_first_block", self._match_inchikey_first_block),
            ("pubchem_cid", self._match_pubchem_cid),
            ("chembl_id", self._match_chembl_id),
            ("name_low", self._match_name),
        ):
            matches = matcher(normalized_query)
            if not matches:
                continue
            if confidence == "name_low" and len(matches) > 1 and not self.allow_ambiguous_name:
                return IdentityResolution(
                    status="ambiguous",
                    confidence="ambiguous_name",
                    query=normalized_query,
                    candidates=list(matches),
                    reason="multiple cache rows matched name or alias",
                )
            if len(matches) > 1 and confidence != "name_low":
                return IdentityResolution(
                    status="ambiguous",
                    confidence=f"ambiguous_{confidence}",
                    query=normalized_query,
                    candidates=list(matches),
                    reason=f"multiple cache rows matched {confidence}",
                )
            return IdentityResolution(
                status="resolved",
                confidence=confidence,
                query=normalized_query,
                candidate=matches[0],
                candidates=list(matches),
                reason=f"matched by {confidence}",
            )

        return IdentityResolution(
            status="unresolved",
            confidence="unresolved",
            query=normalized_query,
            reason="no cache row matched supplied identifiers",
        )

    def _normalize_query(self, query: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(query)
        normalized["normalized_name"] = _normalize_text(query.get("name"))
        normalized["chembl_id"] = _normalize_chembl(query.get("chembl_id"))
        normalized["pubchem_cid"] = _normalize_int(query.get("pubchem_cid"))
        normalized["inchikey"] = _normalize_inchikey(query.get("inchikey"))
        smiles = _clean_optional(query.get("smiles"))
        if smiles:
            try:
                canonical_smiles, inchikey = self.descriptor_calculator.canonicalize(smiles)
            except InvalidStructureError:
                normalized["canonical_smiles"] = smiles
            else:
                normalized["canonical_smiles"] = canonical_smiles
                normalized["inchikey"] = normalized["inchikey"] or inchikey
        return normalized

    def _match_exact_inchikey(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        inchikey = query.get("inchikey")
        if not inchikey:
            return []
        return [row for row in self.rows if row.get("inchikey") == inchikey]

    def _match_inchikey_first_block(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        first_block = _inchikey_first_block(query.get("inchikey"))
        if not first_block:
            return []
        return [row for row in self.rows if _inchikey_first_block(row.get("inchikey")) == first_block]

    def _match_pubchem_cid(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        pubchem_cid = query.get("pubchem_cid")
        if pubchem_cid is None:
            return []
        return [row for row in self.rows if row.get("pubchem_cid") == pubchem_cid]

    def _match_chembl_id(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        chembl_id = query.get("chembl_id")
        if not chembl_id:
            return []
        return [row for row in self.rows if row.get("chembl_id") == chembl_id]

    def _match_name(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        normalized_name = query.get("normalized_name")
        if not normalized_name:
            return []
        return [row for row in self.rows if normalized_name in row["normalized_names"]]


def write_identity_resolution_report(
    results: list[IdentityResolution] | tuple[IdentityResolution, ...],
    output_dir: str | Path,
    *,
    stem: str = "compound_identity",
) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    unresolved = [result.report_record() for result in results if result.status == "unresolved"]
    ambiguous = [result.report_record() for result in results if result.status == "ambiguous"]
    unresolved_csv = output_path / f"{stem}_unresolved.csv"
    ambiguous_csv = output_path / f"{stem}_ambiguous.csv"
    summary_md = output_path / f"{stem}_summary.md"

    pd.DataFrame(unresolved, columns=REPORT_COLUMNS).to_csv(unresolved_csv, index=False)
    pd.DataFrame(ambiguous, columns=REPORT_COLUMNS).to_csv(ambiguous_csv, index=False)
    counts = pd.Series([result.status for result in results]).value_counts().to_dict()
    summary_md.write_text(
        "\n".join(
            [
                "# Compound identity resolution report",
                "",
                f"total: {len(results)}",
                f"resolved: {counts.get('resolved', 0)}",
                f"ambiguous: {counts.get('ambiguous', 0)}",
                f"unresolved: {counts.get('unresolved', 0)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "unresolved_csv": unresolved_csv,
        "ambiguous_csv": ambiguous_csv,
        "summary_md": summary_md,
    }


def _normalize_cache_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "name": _clean_optional(row.get("name")),
        "canonical_smiles": _clean_optional(row.get("canonical_smiles") or row.get("smiles")),
        "inchikey": _normalize_inchikey(row.get("inchikey")),
        "pubchem_cid": _normalize_int(row.get("pubchem_cid")),
        "chembl_id": _normalize_chembl(row.get("chembl_id")),
        "formula": _clean_optional(row.get("formula")),
        "molecular_weight": _normalize_float(row.get("molecular_weight")),
        "source": _clean_optional(row.get("source")),
    }
    names = {_normalize_text(normalized["name"])}
    aliases = _clean_optional(row.get("aliases"))
    if aliases:
        names.update(_normalize_text(alias) for alias in aliases.split("|"))
    normalized["normalized_names"] = {name for name in names if name}
    return normalized


def _clean_optional(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _normalize_text(value: Any) -> str | None:
    text = _clean_optional(value)
    return text.casefold() if text else None


def _normalize_inchikey(value: Any) -> str | None:
    text = _clean_optional(value)
    return text.upper() if text else None


def _normalize_chembl(value: Any) -> str | None:
    text = _clean_optional(value)
    return text.upper() if text else None


def _normalize_int(value: Any) -> int | None:
    if value is None or pd.isna(value) or value == "":
        return None
    return int(value)


def _normalize_float(value: Any) -> float | None:
    if value is None or pd.isna(value) or value == "":
        return None
    return float(value)


def _inchikey_first_block(inchikey: Any) -> str | None:
    text = _normalize_inchikey(inchikey)
    if not text or "-" not in text:
        return None
    return text.split("-", maxsplit=1)[0]
