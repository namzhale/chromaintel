from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class PubChemClient:
    """Small PubChem PUG REST client with offline-safe failure behavior."""

    timeout_seconds: int = 10

    def lookup_by_name(self, name: str) -> dict[str, Any]:
        url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
            f"{name}/property/CanonicalSMILES,MolecularFormula,MolecularWeight/JSON"
        )
        response = requests.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        props = response.json()["PropertyTable"]["Properties"][0]
        return {
            "pubchem_cid": props.get("CID"),
            "smiles": props.get("CanonicalSMILES"),
            "formula": props.get("MolecularFormula"),
            "molecular_weight": props.get("MolecularWeight"),
        }

    def lookup_by_cid(self, cid: int) -> dict[str, Any]:
        url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
            f"{cid}/property/CanonicalSMILES,MolecularFormula,MolecularWeight/JSON"
        )
        response = requests.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        props = response.json()["PropertyTable"]["Properties"][0]
        return {
            "pubchem_cid": props.get("CID"),
            "smiles": props.get("CanonicalSMILES"),
            "formula": props.get("MolecularFormula"),
            "molecular_weight": props.get("MolecularWeight"),
        }
