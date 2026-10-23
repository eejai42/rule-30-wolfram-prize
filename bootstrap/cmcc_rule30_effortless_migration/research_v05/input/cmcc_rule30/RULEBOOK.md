# CMCC × Rule 30 — Research Rulebook v0.1
Date: 2026-10-22

## Objective
Investigate the three Wolfram Rule 30 Prize questions using CMCC's Schema, Data, Lookups, Aggregations, and Calculated Fields as a declarative research layer. No claim of proof is made.

## Ground truth
The official problems concern the center column generated from one active cell: (1) nonperiodicity, (2) limiting equal frequencies, (3) an at-least-linear computation lower bound. The exact complexity model and interpretation of the third problem must be resolved from official detailed guidelines before asserting a result.

## Rule 30 specification
Cells are binary, indexed by integer i and time t>=0. Initial state x(i,0)=1 if i=0, else 0. Evolution x(i,t+1)=x(i-1,t) XOR (x(i,t) OR x(i+1,t)). Center c(t)=x(0,t). Each finite experiment computes c(0)...c(T), inclusive.

## CMCC decomposition
- S: CellState(time, position, bit), TransitionRule, Experiment, Observation, Claim.
- D: initial state, exact sequences, horizon, program version, hashes.
- L: predecessor at i-1, i, i+1.
- A: finite counts, densities, period-screening, checksums.
- F: local transition and derived predicates.

## Evidence policy
- Mark each assertion as Definition, Exact identity, Finite computation, Conjecture, or Theorem.
- Never promote finite numerical results to an infinite-time proof.
- Never infer time lower bounds from dependency cone size.
- A prize claim needs a general proof with clearly stated computational model and independently checkable derivations.
- Retain code, inputs, output hashes, environment details, and independent implementations.

## Experiments
E001: exact center-column generation for T=100,1000,10000; frequency and full-prefix period screen for p<=100. Run: `python experiment.py`. Results in `results.json`, sequences in `center_T.txt`.

## Next experiments
E002: compare two independent implementations, including Wolfram Language if available.
E003: calculate block frequencies and autocorrelation, with confidence intervals treated only as descriptive summaries (not random-sampling inferential guarantees).
E004: search for symbolic invariants using algebraic normal forms and left-permutivity.
E005: study eventual periodicity constraints for fixed periods, and attempt general symbolic lemmas.
E006: benchmark alternative center-bit algorithms with explicit computational models; do not confuse benchmark performance with lower bounds.

## Source references
https://rule30prize.org/
https://github.com/eejai42/conceptual-model-completeness-conjecture-toe-meta-model

## Session 002 — independently checked results (2026-10-22)
E002: `experiment_v02.py` computes 10,001 center bits with a bit-parallel integer recurrence, independently of the v0.1 list-based shrinking-row implementation. The SHA-256 matches the original `center_10000.txt` exactly. A separate fixed-width local-array implementation matches the first 257 values. Wolfram Language was not available in this runtime; no Wolfram execution is claimed.

E003: Exact empirical overlapping block counts (lengths 2,3,4) and signed lag correlations are recorded in `results_v02.json`. These are deterministic finite-prefix statistics, not independent random samples or convergence proofs.

E005: For each p=1,...,1000, compute the last t<=10000-p with c(t)!=c(t+p). Any hypothetical eventual period p must begin strictly after that t. The minimum such bound over p=1,...,1000 is 8999. This does NOT rule out eventual periodicity with a sufficiently late onset, nor periods greater than 1000.

### Exact invariant I-001 (proved): outer cone boundaries
For the single-seed initial condition, x(-t,t)=x(t,t)=1 for all t>=0. Proof: finite propagation gives x(i,t)=0 for |i|>t. At the left boundary at t+1, predecessor triple is (0,0,1), hence f(0,0,1)=1. At the right boundary, predecessor triple is (1,0,0), hence f(1,0,0)=1. The base case t=0 is the initial seed. Induction completes the proof. This is a modest exact invariant, not a prize solution.

### Reproducibility
`python experiment.py` and `python experiment_v02.py`. Exact records are in `results.json` and `results_v02.json`. No proof of any prize problem is claimed.

## Session 003: Exact finite-period exclusion certificate

Run `python experiment_v03.py`. For every integer period `p` from 1 to 1000,
`period_witnesses_v03.json` records an explicit index `t` where the center
column differs at `t` and `t+p`. This is an independently checkable finite
certificate. `results_v03.json` reports the largest *uniform* onset cutoff
excluded for all these candidate periods. The certificate is not a proof of
non-eventual-periodicity: periods above 1000 or sufficiently late onset remain
untouched.

### Logical obstruction (proved)

No finite prefix of an otherwise unconstrained binary sequence can prove that
sequence is not eventually periodic: for any finite prefix, append infinitely
many zeros. Thus a Rule 30 nonperiodicity proof must use the evolution law in
an essential way, not merely finite center-column observations. This does not
show such a proof is impossible; it specifies what the proof must exploit.

### Formal model warning

The complexity prize requires a specified machine model and uniformity/input
representation. A declarative dependency graph alone does not establish a
runtime lower bound. CMCC universality, even if proved, would not by itself
settle any of the three prizes.

## Session 004 — proved right-edge diagonal periodicity
See `THEOREM_004.md` for complete proof: for y_k(t)=x(t-k,t), y_k(t+2^k)=y_k(t) for all k,t>=0. The proof uses a triangular recurrence and XOR cancellation. This is a genuine infinite-time theorem, **not a prize solution**. `experiment_v04.py` checks the identity against an independent full-state simulation for k<=12, t<=4096; results in `results_v04.json`.
