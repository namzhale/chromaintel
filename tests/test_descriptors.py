import pytest

from app.services.descriptors import DescriptorCalculator, InvalidStructureError


def test_calculates_core_rdkit_descriptors_for_caffeine():
    calc = DescriptorCalculator()

    descriptors = calc.from_smiles("Cn1cnc2c1c(=O)n(C)c(=O)n2C")

    assert descriptors["molecular_weight"] == pytest.approx(194.19, abs=0.05)
    assert descriptors["tpsa"] == pytest.approx(61.82, abs=0.05)
    assert descriptors["hbond_acceptors"] == 6
    assert descriptors["hbond_donors"] == 0
    assert descriptors["heavy_atom_count"] == 14
    assert len(descriptors["morgan_fp"]) == 2048
    assert set(descriptors["morgan_fp"]) <= {0, 1}


def test_invalid_smiles_raises_domain_error():
    calc = DescriptorCalculator()

    with pytest.raises(InvalidStructureError):
        calc.from_smiles("not-a-smiles")
