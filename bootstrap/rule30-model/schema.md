# Normalized schema: the Rule 30 model

Shadle step 6. The rulebook (`effortless-rulebook/effortless-rulebook.json`) is the source of
truth; `research/hub/build_model.py` writes these tables into it and every field there has a
description. This page is the map.

Only structure and the problem's inputs are Data: the rule numbers, the 8 neighborhoods, the
seed, the depth, the cell grid and its parent links, the periods, tolerances, machine models
and algorithms, and the predicates' formal statements. Every cell value, count, witness and
verdict is a formula. As in simpsons-paradox, where `IsSignFlip` emerges from raw case counts,
nothing here says "the center column has a mismatch at t = 61"; the model computes it.

```
CellStates ──< SeedCells >── InitialConditions ──< Runs >── Rules ──< RuleTableEntries >── Neighborhoods
                                                     │                    (self: Left/RightPartner)
                       ┌─────────────────────────────┼──────────────┐
                   TimeSteps (self: PreviousStep)  Columns        Cells (self: Left/Center/RightParent)
                       │                             │              │
                  Computations >── Algorithms   PeriodTests >── Periods
                                   >── MachineModels  │
                                                 PeriodComparisons (self; Earlier/LaterCell >── Cells)
                                             ColorCounts >── CellStates
                  Tolerances ──< ToleranceChecks >── Cells
                  AcceleratorClaims >── Cells, Evidence

Operators, Variables ──< Terms (self: Arg1..Arg4) ──< Predicates ──< PredicateInstances >── RuleTableEntries | Runs |
                                                       │          PeriodicityCandidates | MismatchWindows | Cells |
                                                       │          LeftConsistencyChecks | TailCandidates | Tolerances | Algorithms
                                                       └──< Assertions (the ledger reads EffectiveStatus)
```

| Area | Table | One row is | Key derived fields |
|---|---|---|---|
| Automaton | CellStates | a color | — |
| | Rules | a rule (30, 86, 135, 149) | TableNumber, MirrorRuleNumber, ComplementRuleNumber, IsQuiescent, IsBalanced, IsLeftPermutive, IsRule30Polynomial |
| | Neighborhoods | one of 8 input patterns | NeighborhoodIndex, MirrorIndex, ComplementIndex, PolynomialValue |
| | RuleTableEntries | one transition of one rule | OutputValue, IsLeftSensitive, MatchesPolynomial, UseCount |
| Evolution | InitialConditions | an initial condition | IsSingleSeed |
| | SeedCells | a listed cell at t = 0 | StateValue |
| | Runs | rule + initial condition + depth | IsLightConeExact, CenterOnes, CenterDiscrepancy, LongestCenterRun, CenterRunBoundViolations |
| | TimeSteps | one line t | Width, BlackCount, CenterValue, CumulativeCellUpdates |
| | Columns | one position i | BlackCount, Density |
| | Cells | x(i, t) | Value, TransitionKey, ColumnOnes, ColumnDensity, Discrepancy, RunStart, RunBound |
| Problem 1 | Periods | a period p | — |
| | PeriodTests | (column, p), columns 0 and 1 | LastMismatchTime, LongestAgreementStreak, RefutedCandidateCount |
| | PeriodicityCandidates | "column i is p-periodic from onset T" | IsMismatch, FirstMismatchFrom (the witness, via the chain to T + 1), IsRefuted, InBoundedDomain |
| | MismatchWindows | Theorem C at (T, p) | CenterInWindow, NeighborInWindow, WindowHolds |
| | LeftConsistencyChecks | TX at time t | IsOneTime, ForcedNext, IsConsistent |
| | PeriodicWords, WordLetters, WordShifts, WordShiftChecks | a tail word, its letters and rotations | LeastPeriod, IsPrimitive, IsNonconstant, IsInB9Domain, MaxKillExcess |
| | TailCandidates | real prefix to T, then a a a ... | KillTime (witness), IsKilled, KillExcess |
| | TailCenterTerms, TailCells, TailChecks | c'(t), the left half x'(i, t) it drives, the one-time check | Value, IsViolation, FirstViolationFrom |
| Problem 2 | Tolerances | a margin ε | LastExcursionTime (witness), SettledAtHorizon |
| | ToleranceChecks | (ε, prefix) | IsExcursion |
| | ColorCounts | (column, color) | OccurrenceCount, Share |
| Problem 3 | MachineModels | what a step is | — |
| | Algorithms | a way to compute c(n) | IsAdmissible, RatioAtHorizon, IsRatioGrowing |
| | Computations | machine[m][n] = {v, t} | OutputValue, Effort, EffortRatio |
| Logic | Variables | t, i, p, T, N, ε, n, m, a, … | BinderCount |
| | Operators | ForAll, ==, c, x, rule30, cTail, … | UseCount |
| | Terms | one node of a formal statement | Rendered (the statement written out), BinderCount, UnboundedBinderCount |
| | Predicates | a definition, theorem, bridge obligation, hypothesis or prize problem | Formal, IsFinitelyDecidable, InstanceCount, FailingCount, IsRefuted, IsVerified, FiniteVerdict |
| | PredicateInstances | one bounded instance | InDomain, Holds, Witness (read from the deciding row) |
| Ledger | Assertions (bridge fields) | a claim | IsModelLinked, ModelVerdict, EffectiveStatus, IsModelDecided, IsModelContradicted |
| Outside | AcceleratorClaims | an optimizer's claimed cell value | IsMatch |

Toolchain shape notes (why some things are rows): COUNTIFS-family criteria compare against a
constant or a same-row field, never a row-varying threshold, so "density more than ε from 1/2"
is a row of ToleranceChecks rather than a criterion; a formula reaches one table per hop, so
the column prefix sums and constant runs travel along the CenterParent self-link.
