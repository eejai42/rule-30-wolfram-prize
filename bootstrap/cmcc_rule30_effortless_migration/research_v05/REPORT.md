# Rule 30 through CMCC: audited results and structural obstructions

Research continuation v0.5 — 22 October 2026

**Outcome: none of the three prize conjectures is proved or disproved here.**
The deliverable contains complete elementary proofs of partial results, reproducible finite computations, counterexamples to proposed shortcuts, and an explicit ledger of unresolved obligations. The partial proofs are human-readable mathematical arguments, not Lean-kernel-checked proofs. No submission was made. Novelty relative to the full literature is not claimed.

## 1. Problem and source discipline

Let x(i,0)=[i=0], with i an integer, and

    x(i,t+1) = x(i-1,t) XOR (x(i,t) OR x(i+1,t)).

Write c(t)=x(0,t), t≥0. Problem 1 asks whether

    for every T≥0 and p≥1 there exists t≥T with c(t+p)≠c(t).

Problem 2 asks whether the limit of N⁻¹∑_{t=0}^{N-1} c(t) is 1/2.
The distinction between N values and an inclusive horizon T matters for finite counts.

The official prize page and 2019 detailed announcement were read. The public Rule30PrizeKit README and Rule30Prize.lean were also inspected. Their definitions match the two statements above. The kit identifies the constant-column exclusion as an existing partial result. It supplies no official Lean statement of Problem 3 because a computation model is needed.

Problem 3 has a real wording issue: the announcement's prose discusses no sublinear algorithm, whereas its displayed limsup(time(n)/n)<∞ predicate excludes O(n) algorithms. These are different assertions; neither is silently substituted for the other here. Universality of two runtimes does not imply constant-factor simulation and therefore does not remove a sharp time-bound ambiguity. Any future claim needs a fixed uniform machine, a binary encoding of n, finite program description, an explicit cost model, and the selected asymptotic quantifiers. Big-integer operations below are not unit-cost bit computations.

Primary sources and exact repository revisions are listed in SOURCES.md. The foundational CMCC paper and BRCC proof sketch were downloaded and read in full. The Ruliad essay was consulted for the proposed relation to multiway computation. The user-directed Simpson's Paradox and Fermat examples were inspected at commit `afe180c67cd8b0247c9b82ec72aa87e3654efd9a`. Those projects guide the claim ledger, not assumptions about Rule 30.

## 2. Audit of the entire supplied package

All 15 files in the supplied archive were inspected: the prose and code were read, all JSON records and all sequence bytes were parsed, and every supplied experiment was rerun in a separate directory. The originals are preserved under `input/`. The rerun outputs are under `rerun/`. `data/audit.json` records per-file hashes and comparisons.

- All stored numerical results reproduce. The only ignored comparison field is the Python version. All 1,000 original period witnesses reproduce exactly.
- An additional growing-coordinate integer implementation reproduces all three supplied center sequences. A truth-table set implementation checks diagonal values independently.
- The cone boundary invariant, finite-prefix obstruction, and Theorem 004 are correct. Their proofs do not depend on CMCC completeness.
- The original 8,999 number is a lower bound on a possible onset, whereas 8,998 is the last uniformly excluded onset. These are consistent, not an off-by-one error.
- The stored SHA-256 values hash the digit string **without its newline**, not the complete `.txt` file bytes. The earlier “matches the file exactly” wording should be understood as digit-string equality. The new audit also supplies actual file-byte hashes.
- The finite-horizon `observed_minimal_period` wording in v04 is appropriately empirical. This continuation replaces inference from a long prefix with a full-period certificate and proof of the exact-period algorithm.
- The fixed-width auxiliary implementation sets end cells to zero. This does not change the tested center before the horizon because boundary errors cannot arrive early enough; it is not a full-row verifier. The new set implementation avoids that ambiguity.
- No Wolfram executable or Lean executable was found. The supplied Wolfram code was not executed; its expected count is checked by Python. `rule30_checked.wl` provides explicit center-coordinate extraction rather than relying on an inferred array column.

For T=10,000 the supplied sequence has 10,001 bits, 5,033 ones and 4,968 zeros. The official illustration counts the first 10,000 bits and gives 5,032 ones. Both are correct.

## 3. Exact diagonal periods: a stronger theorem and two falsifications

Define y_k(t)=x(t-k,t), k,t≥0, y_{-1}=0. Finite propagation gives y_0=1 and y_k(0)=0 for k≥1. Direct substitution gives

    y_k(t+1) XOR y_k(t) = q_k(t),
    q_k(t) = y_{k-1}(t) OR y_{k-2}(t).                 (1)

The original theorem proves that y_k has period dividing 2^k. Its induction is valid: if q_k has period P=2^{k-1}, the XOR of 2P consecutive values cancels in pairs.

### Theorem A: exact period of a binary discrete antiderivative

Suppose q is purely periodic with least positive period Q, and y(0) is any bit. Define y(t+1)=y(t) XOR q(t). Put

    ε = XOR_{j=0}^{Q-1} q(j).

Then the least positive period of y is Q if ε=0 and 2Q if ε=1.

**Proof.** Summing the recurrence over Q consecutive steps gives y(t+Q)=y(t) XOR ε. Thus Q or 2Q, respectively, is a period. If R is a period of y, it is a period of q, since q(t)=y(t+1) XOR y(t). Every period of a purely periodic sequence is a multiple of its least period: division of R by Q and periodicity gives a smaller positive remainder period unless the remainder is zero. Hence Q divides R. If ε=0 the least possible R is Q and Q works. If ε=1, Q fails and 2Q works; the only positive multiple of Q smaller than 2Q is Q. This proves the claim, including the constant q=0 and q=1 cases. ∎

**Corollary.** For each k, take a common period P of the previous two diagonals, form their OR over one full cycle, reduce that word to its least period Q, and apply Theorem A. This computes the exact least period of y_k. All periods are powers of two by the original theorem; repeated half-word comparisons suffice to find Q.

When ε=1, y_k(t+Q)=1-y_k(t), so y_k is exactly balanced over its full 2Q-cycle. When ε=0, no such conclusion follows.

**Failed hypothesis H1:** every nonboundary diagonal is balanced. Exact counterexample: y_5 has period word `00010101`, with three ones out of eight.

**Failed hypothesis H2:** periods double at every offset k≥3. At k=4 the least period is 8; at k=5 it is still 8. The correct replacement is Theorem A, which records forcing period and forcing parity separately. These counterexamples already occur within the supplied v04 values; they are new tests of stronger hypotheses, not errors in v04.

Selected exact results:

| k | Least period | Ones in one period |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 2 | 1 |
| 2 | 2 | 1 |
| 3 | 4 | 2 |
| 4 | 8 | 4 |
| 5 | 8 | 3 |
| 12 | 64 | 31 |
| 23 | 256 | 125 |
| 26 | 1,024 | 516 |
| 32 | 4,096 | 2,062 |
| 40 | 65,536 | 32,708 |
| 50 | 1,048,576 | 523,884 |
| 51 | 2,097,152 | 1,048,576 |

The complete table is `data/diagonal_periods.json`. The adaptive computation stopped before k=52 because its conservative candidate allocation exceeded the preset 2^21-word cap, not because a mathematical obstruction was reached.

`verify_periods.py` independently evolves the entire finite triangular system as one integer. It checks each claimed period over a full joint orbit and rejects the half-period, which proves minimality among powers of two. A separate exhaustive check verifies Theorem A's algorithm on all 1,966 primitive binary forcing words with lengths at most ten. These checks support the proofs but do not replace them.

### Theorem B: diagonal periods are unbounded

For k≥1 the first nonzero value of y_k occurs at a_k=ceil(k/2). Consequently its least period P_k satisfies

    P_k > ceil(k/2),  P_k divides 2^k.

**Proof.** If t<ceil(k/2), then t-k<-t, outside the cone, so y_k(t)=0. For k=2m, at t=m the point is the left boundary (-m,m), whose bit is 1. For k=2m+1, at t=m+1 it is the first cell inside that boundary. This cell is also 1: for any t≥1, its predecessor triple at position -t+1 is (0,1,b), so the result is 1, regardless of b. Thus the asserted first nonzero time is exact. If a positive period P≤a_k existed, repeated subtraction of P would give a nonzero value at an earlier nonnegative time, a contradiction. Divisibility follows from the original period theorem. ∎

This proves unbounded periods across offsets, not nonperiodicity in the center.

### A concrete obstruction to the diagonal shortcut

The center is c(t)=y_t(t), so its offset changes with t. To show that this distinction is substantive, define an auxiliary array

    z_0(t)=1,
    z_k(t)=[t ≡ ceil(k/2) (mod 2^k)]  for k≥1.

Every fixed z_k has period 2^k; it vanishes before ceil(k/2), becomes 1 exactly then, and respects the same cone-support condition k>2t ⇒ z_k(t)=0. Both outer cone boundaries are 1. Yet z_t(t) is `1,1,0,0,0,...`, hence eventually periodic.

This array is **not Rule 30**. Its first detected recurrence failure is k=2, t=2: the next value is 0 while (1) requires 1. It proves that cone boundaries, first-arrival times and unbounded diagonal periods, even together, do not imply the desired center conclusion. Any successful argument must additionally exploit the cross-offset recurrence.

## 4. A finite-window strengthening of the adjacent-column obstruction

Let d_i(t)=x(i,t) XOR x(i,t+p), for fixed p≥1. Reversing the local rule gives

    x(i-1,t)=x(i,t+1) XOR (x(i,t) OR x(i+1,t)).       (2)

Thus if d_i(t)=d_i(t+1)=d_{i+1}(t)=0, then d_{i-1}(t)=0.

### Theorem C: an explicit mismatch window

For every T≥0 and p≥1, there are i∈{0,1} and t∈[T,2T+p] such that x(i,t)≠x(i,t+p).

**Proof.** Suppose both discrepancy columns vanish throughout [T,U], where U=2T+p. Inductively (2) implies d_{-s}(t)=0 throughout [T,U-s] for 0≤s≤T+p. For s=T+p, this includes t=T. But

    x(-T-p,T)=0,     x(-T-p,T+p)=1,

by cone support and the left-boundary invariant. Hence d_{-T-p}(T)=1, contradiction. ∎

The same induction beginning with columns -1 and 0 needs only the window [T,2T+p-1]: its distance to column -T-p is T+p-1. This is nonnegative for T≥0,p≥1, including the zero-distance base case.

For arbitrary fixed adjacent columns j,j+1, eventual common periodicity also propagates left without changing its onset. Choose a sufficiently large multiple mp so that -T-mp<j and mp>0. The column at -T-mp would have equal values at T and T+mp, contradicting its zero value before the boundary arrives and its value 1 at boundary arrival. Different candidate periods for the two columns can first be replaced by their least common multiple. Thus no adjacent pair is eventually periodic. This qualitative result belongs to the established Jen obstruction; it is not a new prize solution.

The finite test checks 6,464 (T,p) windows, T=0..100 and p=1..64, with explicit witnesses. The proof covers all T,p.

**Remaining gap:** Theorem C allows every witness to lie in column 1. It does not force a witness in column 0. Replacing “at least one of two columns” with “the center” would be an invalid quantifier change.

## 5. Constant runs and the known period-one case

### Theorem D: center-run endpoint bounds

If c(t)=1 for every t∈[T,V], then V≤2T+1. If c(t)=0 throughout that interval, then V≤4T+5.

**Proof for ones.** For t=T..V-1, (2) gives x(-1,t)=0 because c(t)=c(t+1)=1. Hence columns -1 and 0 are both constant through V-1. Their period-one discrepancies vanish through V-2. If V≥2T+2, this includes [T,2T], contradicting the -1,0 version of Theorem C. Thus V≤2T+1.

**Proof for zeros.** Let r(t)=x(1,t). While c(t)=0,

    r(t+1)=r(t) OR x(2,t).

Therefore r is nondecreasing on [T,V], with at most one switch. Any subinterval [A,B] on which both c and r are constant must have B≤2A+1: otherwise their period-one discrepancies vanish throughout [A,2A+1], contrary to Theorem C. If r never switches, V≤2T+1 already. If it switches at S, with T<S≤V, the first segment ends S-1≤2T+1, so S≤2T+2; the second gives V≤2S+1≤4T+5. If r is already 1 at T it is the no-switch case. ∎

**Corollaries.** Neither constant tail is possible; both colors occur infinitely often. If a_r is the starting time of the r-th transition, with a_0=0, then a_{r+1}≤4a_r+6 and hence a_r≤2(4^r-1) by induction. Thus at least r transitions have occurred by time 2(4^r-1). This is a logarithmic lower bound on transition count, far short of density 1/2.

The qualitative period-one exclusion was independently derived here and then matched against the existing proof in the official kit. It must be labeled **rederived known result**, not a new solution. The finite run bounds are explicit refinements of the same argument; their novelty has not been established.

The test verifies every completed center run through t=2,048. Unfinished terminal runs are deliberately excluded from that finite test. The theorem does not depend on this horizon.

## 6. Frequency and computational-complexity investigations

Two independently indexed integer implementations agree on all 100,001 center bits through t=100,000. The result is 50,098 ones and 49,903 zeros, frequency 0.5009749902500975. The first 100,000 bits contain 50,098 ones, matching the count in the official illustration. The digit-string SHA-256 is

    c0779618745db107645822860374918e066895f5b2266e3fdc80a61b0cec67c3

For every p=1..10,000, the last observed mismatch is stored. Together these exclude every onset T≤90,000 for every tested p. They do not exclude later onsets or larger periods. The new horizon is for independent reproducibility, not a computation record; much larger prefixes were already described by Wolfram.

Overlapping block counts and counts in time-residue classes modulo 2,4,8,16,32,64 are preserved. They are exact deterministic counts, not independent samples. No statistical confidence interval or asymptotic rate is inferred from them.

### Theorem E: input balance does not supply temporal balance

For n steps with arbitrary initial bits b_{-n},...,b_n, the center output has the form

    b_{-n} XOR G(b_{-n+1},...,b_n).

**Proof.** Induct on n. The left predecessor's n-step output contains the extreme-left input with coefficient one in XOR form by induction. The center and right predecessors have cones that exclude that input. Substitution in the local rule preserves the asserted form. The n=0 case is immediate. ∎

Thus for each assignment of the other inputs, flipping b_{-n} flips the result, and exactly half of all initial words produce a 1. Exhaustive truth tables verify this for n=1..6. However, the prize fixes one seed and varies time. Uniformity over initial conditions does not imply equidistribution along that exceptional orbit. A measure-preservation or ensemble argument must bridge this change of quantifiers; none was found.

Theorem E also gives a limited input-sensitivity statement for arbitrary initial conditions. It does not establish an Ω(n) runtime bound for the fixed-seed function n↦c(n). An algorithm for that function is not obliged to read an arbitrary initial configuration. Likewise, Python performs O(n) **large-integer updates**, each involving O(n) bits; this is not an O(n) bit-operation algorithm. Direct evolution remains quadratic in elementary bit operations up to ordinary implementation factors. No sublinear center-bit algorithm or lower bound was obtained.

## 7. What CMCC contributes and what must be corrected

A concrete CMCC representation is implemented, not merely proposed:

| Primitive | Representation and use |
|---|---|
| Schema | Cells(time,position,bit), Transition(left,center,right,bit), claims, revisions, evidence and dependencies |
| Data | Initial seed, eight transition-table rows, experiment settings, period records and witnesses |
| Lookups | Three predecessor joins and claim-to-evidence/dependency links |
| Aggregations | Counts, XOR parity, witness minima and unresolved-obligation counts |
| Calculated Fields | Next-cell transition, exact-period update, bounds and validation predicates |

`structural.py` materializes 33,411 SQLite cells through t=128 and compares every cell with independent integer evolution. All agree. Immutable time rows ensure each transition reads the previous snapshot, and a transaction commits the completed finite dataset. Missing spatial neighbors are interpreted as zero only beyond a window padded outside the entire tested light cone.

**Semantic equivalence theorem.** For any horizon, the time-indexed CMCC equations with the specified initial data have a unique solution, equal to Rule 30. Proof: time zero is prescribed; if the time-t rows agree, the three lookups and deterministic transition prescribe every time-(t+1) row uniquely. Induction proves existence and uniqueness on every finite cone. Compatible finite cones define the infinite history. No global completeness conjecture is required.

The diagonal schema makes the triangular dependency on smaller offsets explicit. This is useful mathematically: it exposes the forcing parity needed by Theorem A. The structure is equally expressible in conventional recurrences. The tested benefit is transparent dependencies, reusable aggregates and auditable revisions, not greater mathematical expressive power or an established asymptotic speedup.

Two foundational-source claims require qualification before using them as proof steps:

1. **ACID does not imply causal invariance or order independence.** Start a stored integer at 0. Let transaction A add 1 and transaction B double it. Both serial schedules can be ACID-compliant, yet A then B yields 2 and B then A yields 1. Therefore the general guarantee asserted in CMCC §4.2 cannot follow from ACID alone. Additional commutation/confluence hypotheses are needed. This is a counterexample to that implication, not to CMCC representability.
2. **Aggregations cannot universally be nested without changing results.** The average of group averages for [0] and [10,10,10] is 5, but the pooled average is 7.5. Preserve `(sum,count)` to merge averages correctly. Re-evaluation on an unchanged snapshot is deterministic; that differs from algebraic idempotence or arbitrary regrouping. The general properties in §2.4 need an operator-specific statement.

The foundational Turing-machine mapping is a plausible constructive simulation under explicit unbounded storage and iteration assumptions. It is not a proof of Rule 30 universality, single-seed randomness, or a runtime lower bound. A terminating-field restriction also needs a distinction between each finite transition terminating and the overall simulated computation halting. The supplied BRCC text explicitly calls its argument a sketch and leaves a complete syntax/semantics formalization for further work.

The Ruliad provides a setting in which many rule systems can be represented. Membership in such a broad space does not single out a statistical law or resource bound for this fixed orbit. The present single-seed synchronous Rule 30 system has one forward successor at each step. Genuine branching appears when exploring alternative rules, initial states, or hypotheses, and must be represented as such rather than inferred from deterministic conditional expressions.

## 8. Revision history and trust boundary

The Simpson example's `conc-17` and `conc-32` preserve a zero-economics-flips observation and its later supersession after ten economics flips appeared. The Fermat example expressly distinguishes replacing parent proof edges from eliminating the imported theorem content underneath them. Here the corresponding rule is: finite verification never upgrades a universal claim; a decomposition never discharges its unproved child obligation.

| Cycle | Hypothesis / obligation | Test or deduction | Result and revision |
|---|---|---|---|
| 0 | Supplied numerical outputs are correct | All original scripts rerun; independent indexing | Confirmed; clarify hash and horizon conventions |
| 1 | Every fixed diagonal is balanced | Exact full periods | Falsified at k=5; replace by forcing-parity condition |
| 2 | Period doubles at every k≥3 | Exact period recurrence | Falsified at k=5; retain Q and parity separately |
| 3 | Unbounded diagonal periods force aperiodic center | Explicit z-array with cone support and first arrivals | Falsified as an implication; recurrence coupling remains essential |
| 4 | Periodic adjacent columns are compatible with the seed | Inverse rule plus finite cone boundary | Impossible; explicit finite mismatch window proved |
| 5 | A constant center tail might survive the two-column obstruction | One-tail forces a fixed left neighbor; zero-tail forces monotone right neighbor | Excluded for all onsets; identified as known qualitative result |
| 6 | Local periodic spacetime constraints alone refute candidate center periods | Exhaustive pair-word graphs for p≤8 | Local periodic solutions exist; seed compatibility cannot be dropped |
| 7 | Input ensemble balance proves time balance | Sensitivity theorem and exact truth tables | Ensemble theorem proved; transfer to the fixed orbit remains unsupported |
| 8 | CMCC and ordinary evolution agree | SQLite lookups/formulas versus independent rows | All 33,411 cells agree; representation theorem proved |
| 9 | ACID / arbitrary aggregation nesting supply additional invariants | Explicit serial-order and unequal-group counterexamples | General implications rejected; narrow their hypotheses |
| 10 | The finite center exclusions persist at a larger horizon | Two implementations through t=100,000 | Stronger finite certificates; no infinite-time promotion |
| 11 | Period calculations survive a different implementation | Whole triangular-state orbit replay | See `data/period_verification.json` |

The pair-word graph experiment exhausts 2^(2p) periodic pairs for each p≤8, using (a,b)↦(shift(a) XOR (a OR b),a). Such graphs have periodic local extensions, including the all-zero spacetime. They omit the seed and cannot alone resolve Problem 1. The model distinguishes an existentially possible local pattern from the actual uniquely specified evolution.

Trusted components: ordinary integer arithmetic and induction for the proofs; Python, SQLite and the host for finite calculations; source authentication and the named revisions for imported descriptions. No existing deep theorem is a load-bearing unproved child of Theorems A–E. Their generalization to a prize statement has explicit **OPEN** obligations. No mathematical claim in the inspected Simpson or Fermat projects was independently certified here; those projects were read as methodological examples, not adopted as proved providers.

## 9. Unresolved frontier and next discriminating experiments

**Problem 1.** The missing step is to force infinitely many mismatches in the center itself for every p≥2 and every onset. A promising targeted formulation is to assume c is a p-periodic word, express the resulting constraints on the right-neighbor trace, and determine which words force that neighbor eventually periodic. The constant words do; the argument above establishes why. For nonconstant words the right trace retains input from farther-right cells. An exhaustive finite-width test must not silently replace this input with zeros or periodic boundary conditions.

**Problem 2.** Neither exact balance on some fixed diagonals, nor input ensemble balance, nor the 100,001-bit frequency controls the moving-diagonal average. A sufficient result would be a sublinear bound on |2∑_{t<N}c(t)-N|. No such bound was proved. Nonconstant behavior and logarithmically many transitions allow densities different from 1/2, or no density at all.

**Problem 3.** A proof must quantify over all algorithms in a fixed model, not just the evolution algorithm or the CMCC query plan. A computation graph with many nodes certifies an implementation's work, not a lower bound on all implementations. The word-size cost and nonuniform precomputation must be explicit.

**Diagonal frontier.** Least periods were nondecreasing through k=51. This remains a finite observation, not a theorem. Theorem B proves unboundedness without requiring monotonicity. A worthwhile next lemma would characterize when the OR forcing can have a period smaller than both inputs; this could explain period plateaus. Even a complete period-growth classification would still need a moving-diagonal argument.

This execution produced a reproducible research increment with multiple falsification/revision cycles. It did not reach the requested success criterion. Nothing in the package should be represented as a prize submission or a proof of any full prize conjecture.

## 10. Follow-up attack on nonconstant center periods

After the initial structural results, a further experiment tested the next attack rather than assuming it would work. If the center is a proposed periodic word a(t), its right neighbor r obeys

    r(t+1)=a(t) XOR (r(t) OR s(t)),

where s(t)=x(2,t). Treating s as a free bit gives a finite directed graph on (time phase,r). This is a relaxation of Rule 30, not the full lattice.

`periodic_center_probe.py` checks every primitive word of length 1..10, 1,966 words in total. The only word whose graph lacks recurrent branching is the all-zero word. Every tested nonconstant word admits recurrent branching in the relaxed right-neighbor graph. Thus the monotonicity argument used for a constant zero center does not generalize directly to these patterns. A strongly connected component with two outgoing edges inside it allows aperiodic choices between recurrent paths; the two next states differ in the observed right bit.

This is a failed proof strategy, not evidence of an actual periodic Rule 30 center: the free input sequence s may violate its own evolution or the single-seed initial state. The next necessary ingredient is precisely compatibility with additional columns and the seed. It must be added without silently imposing finite-width boundary assumptions. The detailed graph results are retained in `data/periodic_center_probe.json`.
