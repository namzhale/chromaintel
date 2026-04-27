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


def test_calculates_extended_lcms_descriptors_for_acid_base_and_surface():
    calc = DescriptorCalculator()

    aspirin = calc.from_smiles("CC(=O)Oc1ccccc1C(=O)O")
    labetalol = calc.from_smiles("CC(CCc1ccccc1)NCC(O)c1ccc(O)c(NC=O)c1")

    assert aspirin["exact_mol_wt"] > 180
    assert aspirin["labute_asa"] > 0
    assert aspirin["molar_refractivity"] > 0
    assert aspirin["carboxylic_acid_count"] == 1
    assert aspirin["acidic_group_count"] >= 1
    assert aspirin["strongest_acid_pka_proxy"] < 5
    assert aspirin["acid_ionized_fraction_ph7"] > aspirin["acid_ionized_fraction_ph3"]
    assert aspirin["estimated_net_charge_ph7"] < aspirin["estimated_net_charge_ph3"]
    assert aspirin["slogp_vsa_hydrophobic"] >= 0
    assert aspirin["peoe_vsa_positive"] >= 0
    assert aspirin["gasteiger_abs_charge_mean"] >= 0
    assert aspirin["gasteiger_dipole_moment_proxy"] >= 0
    assert aspirin["halogen_count"] == 0

    assert labetalol["basic_group_count"] >= 1
    assert labetalol["amine_count"] >= 1
    assert labetalol["base_ionized_fraction_ph3"] > labetalol["base_ionized_fraction_ph7"]
    assert labetalol["estimated_net_charge_ph3"] > labetalol["estimated_net_charge_ph7"]


def test_invalid_smiles_raises_domain_error():
    calc = DescriptorCalculator()

    with pytest.raises(InvalidStructureError):
        calc.from_smiles("not-a-smiles")
