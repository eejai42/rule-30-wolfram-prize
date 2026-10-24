# Scenarios

Shadle step 5. The data is the real Rule 30 evolution to depth 64, so each scenario is a
business rule of the model and the value it must produce. `oracle.py` computes the expected
values without the rulebook (`scenarios.json`); `research/hub/check_model.py` compares the
built rulebook against them.

| # | Rule exercised | Expected |
|---|---|---|
| S01 | Rule table from the rule number | 111→0, 110→0, 101→0, 100→1, 011→1, 010→1, 001→1, 000→0 |
| S02 | Wolfram's polynomial Mod[p+q+r+qr, 2] | 0 mismatches for rule 30; nonzero for 86, 135, 149 |
| S03 | Mirror and complement from the table | 30→86 / 135; 86→30 / 149; table number reads back as the rule number |
| S04 | Quiescence and permutivity | 30 and 86 quiescent, 135 and 149 not; 30 left-permutive, not right-permutive |
| S05 | Single seed and the first lines | t0: 1; t1: 111; t2: 11001; t3: 1101111 |
| S06 | The center column | 65 terms, 11011100110001011001001110101110011101010110000110010101101010111 |
| S07 | Which transition made each cell | use counts per neighborhood (000 counts cone-edge cells with white parents) |
| S08 | Black cells per line | per-line counts |
| S09 | Problem 1: period tests p ≤ 24 | last mismatch (61 for p = 1..3), longest agreement streak, bounded refutation holds for every p |
| S10 | Theorem D run bounds | 0 violations; longest center run |
| S11 | Problem 2: prefix density | 36 ones of 65, discrepancy 7, last excursion 6 / 10 / 64 for ε = 0.2 / 0.1 / 0.05 |
| S12 | Each color in the center column | white 29, black 36 |
| S13 | Problem 3: light-cone effort | (n+1)² − 1 cell updates |
| S14 | Accelerator claims (E17, 2²⁰-bit run) | the 65 claimed center bits all match the model |
