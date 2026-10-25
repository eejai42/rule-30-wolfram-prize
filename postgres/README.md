# Rulebook to PostgreSQL Script Generation Report

**Schema:** `public`
**Database:** `demo`
**Timestamp:** 2026-10-24 23:02:13 UTC

## Parsing Rulebook

Found **51** tables in rulebook


  - **Assertions** (36 fields, 98 records)
  - **Dependencies** (4 fields, 186 records)
  - **Prerequisites** (10 fields, 506 records)
  - **Assessments** (20 fields, 98 records)
  - **Evidence** (6 fields, 59 records)
  - **Revisions** (8 fields, 42 records)
  - **Loops** (19 fields, 40 records)
  - **Dashboards** (21 fields, 1 records)
  - **EvidenceLinks** (5 fields, 138 records)
  - **Strategies** (25 fields, 2 records)
  - **StrategySteps** (19 fields, 29 records)
  - **LoopTargets** (10 fields, 16 records)
  - **CellStates** (3 fields, 2 records)
  - **Rules** (18 fields, 4 records)
  - **Neighborhoods** (10 fields, 8 records)
  - **RuleTableEntries** (25 fields, 32 records)
  - **InitialConditions** (8 fields, 1 records)
  - **SeedCells** (6 fields, 1 records)
  - **Runs** (25 fields, 1 records)
  - **TimeSteps** (14 fields, 65 records)
  - **Columns** (10 fields, 129 records)
  - **Cells** (47 fields, 4225 records)
  - **Periods** (4 fields, 24 records)
  - **PeriodTests** (28 fields, 48 records)
  - **PeriodicityCandidates** (20 fields, 2520 records)
  - **MismatchWindows** (14 fields, 492 records)
  - **LeftConsistencyChecks** (15 fields, 64 records)
  - **PeriodicWords** (12 fields, 14 records)
  - **WordLetters** (5 fields, 34 records)
  - **WordShifts** (6 fields, 34 records)
  - **WordShiftChecks** (8 fields, 90 records)
  - **TailCandidates** (18 fields, 100 records)
  - **TailCenterTerms** (10 fields, 1500 records)
  - **TailCells** (19 fields, 7100 records)
  - **TailChecks** (20 fields, 1400 records)
  - **Diagonals** (32 fields, 20 records)
  - **DiagonalPeriodTests** (21 fields, 77 records)
  - **DiagonalPeriodChecks** (13 fields, 4565 records)
  - **DiagonalFacts** (23 fields, 80 records)
  - **Tolerances** (12 fields, 3 records)
  - **ToleranceChecks** (11 fields, 195 records)
  - **ColorCounts** (10 fields, 258 records)
  - **MachineModels** (5 fields, 3 records)
  - **Algorithms** (14 fields, 2 records)
  - **Computations** (15 fields, 128 records)
  - **Variables** (7 fields, 30 records)
  - **Operators** (7 fields, 120 records)
  - **Terms** (26 fields, 2450 records)
  - **Predicates** (40 fields, 99 records)
  - **PredicateInstances** (56 fields, 714 records)
  - **AcceleratorClaims** (9 fields, 65 records)

Generated **51** table definitions with **203** raw fields (mode=check-add)
Generated **647** calculation functions
Generated **51** views
Generated **32** fk_labels_* views
Enabled RLS on **51** tables
Generated insert statements for **27912** records
Generated **51** table definitions with **203** raw fields (mode=check-add)
Generated **647** calculation functions
Generated **51** views
Generated **32** fk_labels_* views
## Self-referencing lookups

  - **rule_table_entries** reads its own rows via left_partner, right_partner; memoised: calc_rule_table_entries_output_value
  - **time_steps** reads its own rows via previous_step; memoised: calc_time_steps_cumulative_cell_updates
  - **cells** reads its own rows via left_parent, center_parent, right_parent; memoised: calc_cells_value, calc_cells_column_ones, calc_cells_run_start
  - **periodicity_candidates** reads its own rows via next_candidate; memoised: calc_periodicity_candidates_first_mismatch_from, calc_periodicity_candidates_agreement_run_from
  - **tail_cells** reads its own rows via left_parent, center_parent, right_parent; memoised: calc_tail_cells_value
  - **tail_checks** reads its own rows via next_check; memoised: calc_tail_checks_first_violation_from
  - **diagonals** reads its own rows via previous_diagonal, opposite_diagonal; memoised: calc_diagonals_least_period, calc_diagonals_doubles, calc_diagonals_previous_doubles, calc_diagonals_ones_per_period, calc_diagonals_previous_ones_per_period
  - **terms** reads its own rows via arg1, arg2, arg3, arg4; memoised: calc_terms_rendered

## Script Generation Complete

Generated files:
- `00-bootstrap.sql` - Bootstrap (overwrite Never); includes commented-out drop-all script
- `01-drop-and-create-tables.sql` - Drop and recreate tables with raw fields and FK indexes
- `02-create-functions.sql` - Create calculation functions
- `03-create-views.sql` - Create views with calculated fields
- `04-create-policies.sql` - Create RLS policies
- `05-insert-data.sql` - Insert data from rulebook
- `06-refresh-memos.sql` - Fill the memo tables of self-referencing lookups in row-dependency order
- `99-fk-constraints.sql` - FK constraints (skipped unless EFFORTLESS_ENFORCE_FKS=true)
- `reset-rulebook-db.sh` - DESTRUCTIVE localhost reset: rebuild the dev DB from the rulebook
- `init-db.sh` - Legacy compatibility entry point that delegates to reset-rulebook-db.sh
- `update-effortless-schema.sql` - Rebuild the derived layer (views / calc_* / RLS). Safe in production.

## Where things are defined

The rulebook is the source of truth. Everything above is derived from it.
Tables and columns are **migrated** (additive, forever). Views, `calc_*`
functions and RLS policies are **derived** — they hold no data, so they are
dropped and recreated from the rulebook rather than migrated. Never
hand-write a migration that recreates a view or a calc function.


