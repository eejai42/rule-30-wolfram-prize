# CMCC × Rule 30 — research v0.5

**No prize conjecture is solved.** Start with `REPORT.md` for complete partial proofs, results, failed hypotheses and unresolved obligations. `SOURCES.md` describes exactly what was read and verified.

## Reproduce

Python 3.10+ standard library; SQLite is included in Python. No network or paid service is needed to run experiments. Keep the input directory unchanged.

```bash
python rerun/experiment.py
python rerun/experiment_v02.py
python rerun/experiment_v03.py
python rerun/experiment_v04.py
python research.py
python structural.py
python adversarial.py
python verify_periods.py
python periodic_center_probe.py
python ledger.py
python verify_bundle.py
```

Run from this directory. Original scripts and new scripts locate inputs relative to their own path. Typical runtime is a few minutes, dominated by original list/sparse evolution and complete orbit verification. `verify_periods.py` uses about 32 MB for its orbit array; Python overhead adds memory. `research.py` has an explicit diagonal-cycle cap of 2^21 and a center horizon of 100,000. Reproduction updates environment timings and hashes of those generated metadata files; scientific counts and witnesses should remain unchanged.

## Contents

- `input/`: untouched supplied package.
- `rerun/`: executed copy and regenerated original results.
- `REPORT.md`: human-readable research derivations and audit.
- `research.py`: audit, exact diagonal periods, independent center computation, periodic-pair graphs.
- `structural.py`: adjacent-window and run tests; executable CMCC cell database.
- `adversarial.py`: countermodel, full forcing-word enumeration, input-balance tests and foundational counterexamples.
- `verify_periods.py`: independent whole-state period replay.
- `periodic_center_probe.py`: periodic-center relaxed-neighbor exploration with explicit approximation warning.
- `rulebook.json`, `ledger.py`: structured claims, evidence, dependencies, revisions and database projection.
- `data/`: sequences, JSON witnesses, period certificates, receipts and SQLite model.
- `rule30_checked.wl`: prepared but unexecuted independent Wolfram reproduction.
- `sources/`: foundational source PDFs and text extractions.
- `MANIFEST.json`: SHA-256 and byte sizes for all other deliverable files at packaging time.

## Trust

Human-readable proofs use elementary induction and Boolean algebra. Finite computation trusts Python/SQLite. No Lean verification or Wolfram execution is claimed. A status ledger checks its own consistency; it is not a general-purpose proof checker. Repository examples supplied methodology, not mathematical axioms.
