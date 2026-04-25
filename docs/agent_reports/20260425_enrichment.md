# Agent 3 Enrichment / Identity Resolution Report

## Existing implementation audit

- `app/adapters/pubchem.py` is a small live PUG REST client that returns CID, SMILES, formula, and molecular weight by name or CID. It is useful for interactive lookup, but tests should not depend on it because it performs network requests.
- `app/adapters/chembl.py` is already offline-first: it loads user-provided CSV/JSON annotation tables through the shared adapter loader.
- `app/services/descriptors.py` provides the RDKit standardization layer needed here, including canonical SMILES and InChIKey generation through `DescriptorCalculator.canonicalize()`.

## Work completed

- Added `app/services/compound_identity.py` with an offline fixture/cache loader, identity resolver, ranked confidence labels, and unresolved/ambiguous report generation.
- Added enrichment fixtures under `tests/fixtures/enrichment/`.
- Added `tests/test_compound_identity.py` covering cached fixture loading, no-live-API resolution, confidence labels, ambiguous name rejection, SMILES/InChIKey strengthening, and report output.
- Generated fixture report outputs under `reports/enrichment/`.

## Confidence labels

- `exact_inchikey`
- `inchikey_first_block`
- `pubchem_cid`
- `chembl_id`
- `name_low`
- `ambiguous_name`
- `unresolved`

## Offline safety

The resolver only reads local cache tables and optionally uses local RDKit descriptor calculation. It does not instantiate `PubChemClient` or call `requests`; the test suite monkeypatches PubChem requests to fail if a live call is attempted.
