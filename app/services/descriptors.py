from dataclasses import dataclass
from typing import Any

from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdFingerprintGenerator, rdMolDescriptors


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

        return {
            "canonical_smiles": canonical,
            "molecular_weight": float(Descriptors.MolWt(mol)),
            "logp": float(Crippen.MolLogP(mol)),
            "tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
            "hbond_donors": int(Lipinski.NumHDonors(mol)),
            "hbond_acceptors": int(Lipinski.NumHAcceptors(mol)),
            "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
            "aromatic_ring_count": int(rdMolDescriptors.CalcNumAromaticRings(mol)),
            "formal_charge": int(Chem.GetFormalCharge(mol)),
            "heavy_atom_count": int(mol.GetNumHeavyAtoms()),
            "morgan_fp": fp_list,
        }

    def model_features(self, smiles: str) -> dict[str, float]:
        descriptors = self.from_smiles(smiles)
        return {
            key: float(value)
            for key, value in descriptors.items()
            if key not in {"canonical_smiles", "morgan_fp"}
        }

    @staticmethod
    def _mol_from_smiles(smiles: str):
        if not smiles or not smiles.strip():
            raise InvalidStructureError("SMILES is required for descriptor calculation")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise InvalidStructureError(f"Invalid SMILES: {smiles}")
        return mol
