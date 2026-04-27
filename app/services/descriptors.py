from dataclasses import dataclass
from typing import Any

from rdkit import Chem
from rdkit.Chem import (
    AllChem,
    Crippen,
    Descriptors,
    Lipinski,
    rdFingerprintGenerator,
    rdMolDescriptors,
    rdPartialCharges,
)


class InvalidStructureError(ValueError):
    """Raised when a SMILES string cannot be parsed into a molecule."""


@dataclass(frozen=True)
class DescriptorCalculator:
    """Compute reusable RDKit descriptors for small-molecule LC-MS/MS modeling."""

    fingerprint_bits: int = 2048
    fingerprint_radius: int = 2

    def canonicalize(self, smiles: str) -> tuple[str, str | None]:
        mol = self._mol_from_smiles(smiles)
        canonical = Chem.MolToSmiles(mol, canonical=True)
        inchikey = Chem.MolToInchiKey(mol) if hasattr(Chem, "MolToInchiKey") else None
        return canonical, inchikey

    def from_smiles(self, smiles: str) -> dict[str, Any]:
        mol = self._mol_from_smiles(smiles)
        canonical = Chem.MolToSmiles(mol, canonical=True)
        generator = rdFingerprintGenerator.GetMorganGenerator(
            radius=self.fingerprint_radius, fpSize=self.fingerprint_bits
        )
        fingerprint = generator.GetFingerprint(mol)
        fp_list = [int(bit) for bit in fingerprint.ToBitString()]
        functional_groups = _functional_group_counts(mol)
        charge_features = _gasteiger_charge_features(mol)
        ionization_features = _ionization_proxy_features(functional_groups, float(Crippen.MolLogP(mol)))
        vsa_features = _vsa_features(mol)
        ring_features = _ring_shape_features(mol)

        return {
            "canonical_smiles": canonical,
            "molecular_weight": float(Descriptors.MolWt(mol)),
            "exact_mol_wt": float(Descriptors.ExactMolWt(mol)),
            "logp": float(Crippen.MolLogP(mol)),
            "molar_refractivity": float(Crippen.MolMR(mol)),
            "tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
            "labute_asa": float(rdMolDescriptors.CalcLabuteASA(mol)),
            "hbond_donors": int(Lipinski.NumHDonors(mol)),
            "hbond_acceptors": int(Lipinski.NumHAcceptors(mol)),
            "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
            "aromatic_ring_count": int(rdMolDescriptors.CalcNumAromaticRings(mol)),
            "formal_charge": int(Chem.GetFormalCharge(mol)),
            "heavy_atom_count": int(mol.GetNumHeavyAtoms()),
            "hetero_atom_count": int(rdMolDescriptors.CalcNumHeteroatoms(mol)),
            "halogen_count": int(sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() in {9, 17, 35, 53})),
            "valence_electron_count": int(Descriptors.NumValenceElectrons(mol)),
            "fraction_csp3": float(rdMolDescriptors.CalcFractionCSP3(mol)),
            **ring_features,
            **functional_groups,
            **ionization_features,
            **vsa_features,
            **charge_features,
            "morgan_fp": fp_list,
        }

    def model_features(self, smiles: str, include_fingerprint: bool = True) -> dict[str, float]:
        descriptors = self.from_smiles(smiles)
        features = {
            key: float(value)
            for key, value in descriptors.items()
            if key not in {"canonical_smiles", "morgan_fp"}
        }
        if include_fingerprint:
            features.update({f"morgan_{idx}": float(bit) for idx, bit in enumerate(descriptors["morgan_fp"])})
        return features

    @staticmethod
    def _mol_from_smiles(smiles: str):
        if not smiles or not smiles.strip():
            raise InvalidStructureError("SMILES is required for descriptor calculation")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise InvalidStructureError(f"Invalid SMILES: {smiles}")
        return mol


FUNCTIONAL_GROUP_SMARTS = {
    "carboxylic_acid_count": "[CX3](=O)[OX2H1]",
    "phenol_count": "c[OX2H]",
    "alcohol_count": "[CX4][OX2H]",
    "primary_amine_count": "[NX3;H2;!$(NC=O)]",
    "secondary_amine_count": "[NX3;H1;!$(NC=O)]",
    "tertiary_amine_count": "[NX3;H0;!$(NC=O);!$([N+])]",
    "amide_count": "[NX3][CX3](=O)[#6,#7,#8]",
    "sulfonamide_count": "S(=O)(=O)N",
    "phosphate_count": "P(=O)(O)(O)",
    "nitrile_count": "[CX2]#N",
}


def _functional_group_counts(mol: Chem.Mol) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name, smarts in FUNCTIONAL_GROUP_SMARTS.items():
        pattern = Chem.MolFromSmarts(smarts)
        counts[name] = int(len(mol.GetSubstructMatches(pattern, uniquify=True))) if pattern is not None else 0
    counts["amine_count"] = (
        counts["primary_amine_count"]
        + counts["secondary_amine_count"]
        + counts["tertiary_amine_count"]
    )
    counts["acidic_group_count"] = (
        counts["carboxylic_acid_count"]
        + counts["phenol_count"]
        + counts["sulfonamide_count"]
        + counts["phosphate_count"]
    )
    counts["basic_group_count"] = counts["amine_count"]
    return counts


def _ionization_proxy_features(functional_groups: dict[str, int], logp: float) -> dict[str, float]:
    acid_pkas: list[float] = []
    acid_pkas.extend([4.5] * functional_groups["carboxylic_acid_count"])
    acid_pkas.extend([10.0] * functional_groups["phenol_count"])
    acid_pkas.extend([7.0] * functional_groups["sulfonamide_count"])
    acid_pkas.extend([2.1] * functional_groups["phosphate_count"])
    base_pkas: list[float] = []
    base_pkas.extend([9.8] * functional_groups["primary_amine_count"])
    base_pkas.extend([9.6] * functional_groups["secondary_amine_count"])
    base_pkas.extend([9.2] * functional_groups["tertiary_amine_count"])
    strongest_acid = min(acid_pkas) if acid_pkas else 99.0
    strongest_base = max(base_pkas) if base_pkas else -99.0

    features: dict[str, float] = {
        "strongest_acid_pka_proxy": float(strongest_acid),
        "strongest_base_pka_proxy": float(strongest_base),
    }
    for ph in (3.0, 7.0):
        acid_charge = -sum(_acid_ionized_fraction(pka, ph) for pka in acid_pkas)
        base_charge = sum(_base_ionized_fraction(pka, ph) for pka in base_pkas)
        net_charge = acid_charge + base_charge
        acid_fraction = abs(acid_charge) / max(len(acid_pkas), 1)
        base_fraction = base_charge / max(len(base_pkas), 1)
        suffix = f"ph{int(ph)}"
        features[f"acid_ionized_fraction_{suffix}"] = float(acid_fraction)
        features[f"base_ionized_fraction_{suffix}"] = float(base_fraction)
        features[f"estimated_net_charge_{suffix}"] = float(net_charge)
        features[f"estimated_logd_{suffix}"] = float(logp - 0.75 * abs(net_charge))
    return features


def _acid_ionized_fraction(pka: float, ph: float) -> float:
    return 1.0 / (1.0 + 10.0 ** (pka - ph))


def _base_ionized_fraction(pka: float, ph: float) -> float:
    return 1.0 / (1.0 + 10.0 ** (ph - pka))


def _vsa_features(mol: Chem.Mol) -> dict[str, float]:
    slogp = {idx: float(getattr(Descriptors, f"SlogP_VSA{idx}")(mol)) for idx in range(1, 13)}
    peoe = {idx: float(getattr(Descriptors, f"PEOE_VSA{idx}")(mol)) for idx in range(1, 15)}
    smr = {idx: float(getattr(Descriptors, f"SMR_VSA{idx}")(mol)) for idx in range(1, 11)}
    return {
        "slogp_vsa_hydrophobic": float(sum(slogp[idx] for idx in range(6, 13))),
        "slogp_vsa_polar": float(sum(slogp[idx] for idx in range(1, 4))),
        "peoe_vsa_positive": float(sum(peoe[idx] for idx in range(11, 15))),
        "peoe_vsa_negative": float(sum(peoe[idx] for idx in range(1, 4))),
        "smr_vsa_total": float(sum(smr.values())),
    }


def _ring_shape_features(mol: Chem.Mol) -> dict[str, float]:
    aromatic_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
    heavy_atoms = max(mol.GetNumHeavyAtoms(), 1)
    return {
        "ring_count": int(rdMolDescriptors.CalcNumRings(mol)),
        "aliphatic_ring_count": int(rdMolDescriptors.CalcNumAliphaticRings(mol)),
        "saturated_ring_count": int(rdMolDescriptors.CalcNumSaturatedRings(mol)),
        "bridgehead_atom_count": int(rdMolDescriptors.CalcNumBridgeheadAtoms(mol)),
        "spiro_atom_count": int(rdMolDescriptors.CalcNumSpiroAtoms(mol)),
        "aromatic_atom_fraction": float(aromatic_atoms / heavy_atoms),
        "bertz_complexity": float(Descriptors.BertzCT(mol)),
    }


def _gasteiger_charge_features(mol: Chem.Mol) -> dict[str, float]:
    work = Chem.Mol(mol)
    try:
        rdPartialCharges.ComputeGasteigerCharges(work)
        AllChem.Compute2DCoords(work)
    except Exception:
        return {
            "gasteiger_charge_min": 0.0,
            "gasteiger_charge_max": 0.0,
            "gasteiger_abs_charge_mean": 0.0,
            "gasteiger_dipole_moment_proxy": 0.0,
        }
    charges: list[float] = []
    dipole_x = 0.0
    dipole_y = 0.0
    conformer = work.GetConformer() if work.GetNumConformers() else None
    for atom in work.GetAtoms():
        raw = atom.GetProp("_GasteigerCharge") if atom.HasProp("_GasteigerCharge") else "0"
        try:
            charge = float(raw)
        except ValueError:
            charge = 0.0
        if not np_is_finite(charge):
            charge = 0.0
        charges.append(charge)
        if conformer is not None:
            pos = conformer.GetAtomPosition(atom.GetIdx())
            dipole_x += charge * float(pos.x)
            dipole_y += charge * float(pos.y)
    if not charges:
        charges = [0.0]
    return {
        "gasteiger_charge_min": float(min(charges)),
        "gasteiger_charge_max": float(max(charges)),
        "gasteiger_abs_charge_mean": float(sum(abs(charge) for charge in charges) / len(charges)),
        "gasteiger_dipole_moment_proxy": float((dipole_x**2 + dipole_y**2) ** 0.5),
    }


def np_is_finite(value: float) -> bool:
    return value == value and value not in {float("inf"), float("-inf")}
