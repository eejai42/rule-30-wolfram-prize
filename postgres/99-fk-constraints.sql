-- ============================================================================
-- 99-fk-constraints.sql — FK CONSTRAINTS (off by default)
-- ============================================================================
-- Demos must never fail on FK violations, so init-db.sh SKIPS this file
-- unless EFFORTLESS_ENFORCE_FKS=true is set in the environment.
--
--   EFFORTLESS_ENFORCE_FKS=true bash init-db.sh    # apply constraints
--   bash init-db.sh                                # leave them documented but unenforced
--
-- The rulebook always documents the FK relationships, and 01-drop-and-create-tables.sql
-- always installs the supporting indexes inline. This file just declares the actual
-- enforcement. Idempotent: every constraint is dropped if present, then added.
-- ============================================================================

-- Assertions
ALTER TABLE assertions DROP CONSTRAINT IF EXISTS fk_assertions_introduced_in_loop;
ALTER TABLE assertions ADD CONSTRAINT fk_assertions_introduced_in_loop
  FOREIGN KEY (introduced_in_loop) REFERENCES loops (loop_id);
ALTER TABLE assertions DROP CONSTRAINT IF EXISTS fk_assertions_predicate;
ALTER TABLE assertions ADD CONSTRAINT fk_assertions_predicate
  FOREIGN KEY (predicate) REFERENCES predicates (predicate_id);

-- Dependencies
ALTER TABLE dependencies DROP CONSTRAINT IF EXISTS fk_dependencies_conclusion;
ALTER TABLE dependencies ADD CONSTRAINT fk_dependencies_conclusion
  FOREIGN KEY (conclusion) REFERENCES assertions (assertion_id);
ALTER TABLE dependencies DROP CONSTRAINT IF EXISTS fk_dependencies_premise;
ALTER TABLE dependencies ADD CONSTRAINT fk_dependencies_premise
  FOREIGN KEY (premise) REFERENCES assertions (assertion_id);

-- Prerequisites
ALTER TABLE prerequisites DROP CONSTRAINT IF EXISTS fk_prerequisites_conclusion_key;
ALTER TABLE prerequisites ADD CONSTRAINT fk_prerequisites_conclusion_key
  FOREIGN KEY (conclusion_key) REFERENCES assessments (assessment_id);
ALTER TABLE prerequisites DROP CONSTRAINT IF EXISTS fk_prerequisites_premise;
ALTER TABLE prerequisites ADD CONSTRAINT fk_prerequisites_premise
  FOREIGN KEY (premise) REFERENCES assertions (assertion_id);

-- Assessments
ALTER TABLE assessments DROP CONSTRAINT IF EXISTS fk_assessments_assertion;
ALTER TABLE assessments ADD CONSTRAINT fk_assessments_assertion
  FOREIGN KEY (assertion) REFERENCES assertions (assertion_id);
ALTER TABLE assessments DROP CONSTRAINT IF EXISTS fk_assessments_project_key;
ALTER TABLE assessments ADD CONSTRAINT fk_assessments_project_key
  FOREIGN KEY (project_key) REFERENCES dashboards (dashboard_id);

-- Revisions
ALTER TABLE revisions DROP CONSTRAINT IF EXISTS fk_revisions_assertion;
ALTER TABLE revisions ADD CONSTRAINT fk_revisions_assertion
  FOREIGN KEY (assertion) REFERENCES assertions (assertion_id);
ALTER TABLE revisions DROP CONSTRAINT IF EXISTS fk_revisions_replacement;
ALTER TABLE revisions ADD CONSTRAINT fk_revisions_replacement
  FOREIGN KEY (replacement) REFERENCES assertions (assertion_id);
ALTER TABLE revisions DROP CONSTRAINT IF EXISTS fk_revisions_loop;
ALTER TABLE revisions ADD CONSTRAINT fk_revisions_loop
  FOREIGN KEY (loop) REFERENCES loops (loop_id);

-- Loops
ALTER TABLE loops DROP CONSTRAINT IF EXISTS fk_loops_project_key;
ALTER TABLE loops ADD CONSTRAINT fk_loops_project_key
  FOREIGN KEY (project_key) REFERENCES dashboards (dashboard_id);

-- EvidenceLinks
ALTER TABLE evidence_links DROP CONSTRAINT IF EXISTS fk_evidence_links_evidence;
ALTER TABLE evidence_links ADD CONSTRAINT fk_evidence_links_evidence
  FOREIGN KEY (evidence) REFERENCES evidence (evidence_id);
ALTER TABLE evidence_links DROP CONSTRAINT IF EXISTS fk_evidence_links_assertion;
ALTER TABLE evidence_links ADD CONSTRAINT fk_evidence_links_assertion
  FOREIGN KEY (assertion) REFERENCES assertions (assertion_id);

-- Strategies
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS fk_strategies_goal;
ALTER TABLE strategies ADD CONSTRAINT fk_strategies_goal
  FOREIGN KEY (goal) REFERENCES assertions (assertion_id);
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS fk_strategies_next_target;
ALTER TABLE strategies ADD CONSTRAINT fk_strategies_next_target
  FOREIGN KEY (next_target) REFERENCES assertions (assertion_id);
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS fk_strategies_updated_in_loop;
ALTER TABLE strategies ADD CONSTRAINT fk_strategies_updated_in_loop
  FOREIGN KEY (updated_in_loop) REFERENCES loops (loop_id);
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS fk_strategies_next_loop;
ALTER TABLE strategies ADD CONSTRAINT fk_strategies_next_loop
  FOREIGN KEY (next_loop) REFERENCES loops (loop_id);
ALTER TABLE strategies DROP CONSTRAINT IF EXISTS fk_strategies_project_key;
ALTER TABLE strategies ADD CONSTRAINT fk_strategies_project_key
  FOREIGN KEY (project_key) REFERENCES dashboards (dashboard_id);

-- StrategySteps
ALTER TABLE strategy_steps DROP CONSTRAINT IF EXISTS fk_strategy_steps_strategy;
ALTER TABLE strategy_steps ADD CONSTRAINT fk_strategy_steps_strategy
  FOREIGN KEY (strategy) REFERENCES strategies (strategy_id);
ALTER TABLE strategy_steps DROP CONSTRAINT IF EXISTS fk_strategy_steps_assertion;
ALTER TABLE strategy_steps ADD CONSTRAINT fk_strategy_steps_assertion
  FOREIGN KEY (assertion) REFERENCES assertions (assertion_id);

-- LoopTargets
ALTER TABLE loop_targets DROP CONSTRAINT IF EXISTS fk_loop_targets_loop;
ALTER TABLE loop_targets ADD CONSTRAINT fk_loop_targets_loop
  FOREIGN KEY (loop) REFERENCES loops (loop_id);
ALTER TABLE loop_targets DROP CONSTRAINT IF EXISTS fk_loop_targets_assertion;
ALTER TABLE loop_targets ADD CONSTRAINT fk_loop_targets_assertion
  FOREIGN KEY (assertion) REFERENCES assertions (assertion_id);

-- RuleTableEntries
ALTER TABLE rule_table_entries DROP CONSTRAINT IF EXISTS fk_rule_table_entries_rule;
ALTER TABLE rule_table_entries ADD CONSTRAINT fk_rule_table_entries_rule
  FOREIGN KEY (rule) REFERENCES rules (rule_id);
ALTER TABLE rule_table_entries DROP CONSTRAINT IF EXISTS fk_rule_table_entries_neighborhood;
ALTER TABLE rule_table_entries ADD CONSTRAINT fk_rule_table_entries_neighborhood
  FOREIGN KEY (neighborhood) REFERENCES neighborhoods (neighborhood_id);
ALTER TABLE rule_table_entries DROP CONSTRAINT IF EXISTS fk_rule_table_entries_left_partner;
ALTER TABLE rule_table_entries ADD CONSTRAINT fk_rule_table_entries_left_partner
  FOREIGN KEY (left_partner) REFERENCES rule_table_entries (rule_table_entry_id);
ALTER TABLE rule_table_entries DROP CONSTRAINT IF EXISTS fk_rule_table_entries_right_partner;
ALTER TABLE rule_table_entries ADD CONSTRAINT fk_rule_table_entries_right_partner
  FOREIGN KEY (right_partner) REFERENCES rule_table_entries (rule_table_entry_id);

-- InitialConditions
ALTER TABLE initial_conditions DROP CONSTRAINT IF EXISTS fk_initial_conditions_background;
ALTER TABLE initial_conditions ADD CONSTRAINT fk_initial_conditions_background
  FOREIGN KEY (background) REFERENCES cell_states (cell_state_id);

-- SeedCells
ALTER TABLE seed_cells DROP CONSTRAINT IF EXISTS fk_seed_cells_initial_condition;
ALTER TABLE seed_cells ADD CONSTRAINT fk_seed_cells_initial_condition
  FOREIGN KEY (initial_condition) REFERENCES initial_conditions (initial_condition_id);
ALTER TABLE seed_cells DROP CONSTRAINT IF EXISTS fk_seed_cells_state;
ALTER TABLE seed_cells ADD CONSTRAINT fk_seed_cells_state
  FOREIGN KEY (state) REFERENCES cell_states (cell_state_id);

-- Runs
ALTER TABLE runs DROP CONSTRAINT IF EXISTS fk_runs_rule;
ALTER TABLE runs ADD CONSTRAINT fk_runs_rule
  FOREIGN KEY (rule) REFERENCES rules (rule_id);
ALTER TABLE runs DROP CONSTRAINT IF EXISTS fk_runs_initial_condition;
ALTER TABLE runs ADD CONSTRAINT fk_runs_initial_condition
  FOREIGN KEY (initial_condition) REFERENCES initial_conditions (initial_condition_id);

-- TimeSteps
ALTER TABLE time_steps DROP CONSTRAINT IF EXISTS fk_time_steps_run;
ALTER TABLE time_steps ADD CONSTRAINT fk_time_steps_run
  FOREIGN KEY (run) REFERENCES runs (run_id);
ALTER TABLE time_steps DROP CONSTRAINT IF EXISTS fk_time_steps_previous_step;
ALTER TABLE time_steps ADD CONSTRAINT fk_time_steps_previous_step
  FOREIGN KEY (previous_step) REFERENCES time_steps (time_step_id);

-- Columns
ALTER TABLE columns DROP CONSTRAINT IF EXISTS fk_columns_run;
ALTER TABLE columns ADD CONSTRAINT fk_columns_run
  FOREIGN KEY (run) REFERENCES runs (run_id);

-- Cells
ALTER TABLE cells DROP CONSTRAINT IF EXISTS fk_cells_run;
ALTER TABLE cells ADD CONSTRAINT fk_cells_run
  FOREIGN KEY (run) REFERENCES runs (run_id);
ALTER TABLE cells DROP CONSTRAINT IF EXISTS fk_cells_time_step;
ALTER TABLE cells ADD CONSTRAINT fk_cells_time_step
  FOREIGN KEY (time_step) REFERENCES time_steps (time_step_id);
ALTER TABLE cells DROP CONSTRAINT IF EXISTS fk_cells_column;
ALTER TABLE cells ADD CONSTRAINT fk_cells_column
  FOREIGN KEY ("column") REFERENCES columns (column_id);
ALTER TABLE cells DROP CONSTRAINT IF EXISTS fk_cells_seed_cell;
ALTER TABLE cells ADD CONSTRAINT fk_cells_seed_cell
  FOREIGN KEY (seed_cell) REFERENCES seed_cells (seed_cell_id);
ALTER TABLE cells DROP CONSTRAINT IF EXISTS fk_cells_left_parent;
ALTER TABLE cells ADD CONSTRAINT fk_cells_left_parent
  FOREIGN KEY (left_parent) REFERENCES cells (cell_id);
ALTER TABLE cells DROP CONSTRAINT IF EXISTS fk_cells_center_parent;
ALTER TABLE cells ADD CONSTRAINT fk_cells_center_parent
  FOREIGN KEY (center_parent) REFERENCES cells (cell_id);
ALTER TABLE cells DROP CONSTRAINT IF EXISTS fk_cells_right_parent;
ALTER TABLE cells ADD CONSTRAINT fk_cells_right_parent
  FOREIGN KEY (right_parent) REFERENCES cells (cell_id);

-- PeriodTests
ALTER TABLE period_tests DROP CONSTRAINT IF EXISTS fk_period_tests_column;
ALTER TABLE period_tests ADD CONSTRAINT fk_period_tests_column
  FOREIGN KEY ("column") REFERENCES columns (column_id);
ALTER TABLE period_tests DROP CONSTRAINT IF EXISTS fk_period_tests_period;
ALTER TABLE period_tests ADD CONSTRAINT fk_period_tests_period
  FOREIGN KEY (period) REFERENCES periods (period_id);

-- PeriodicityCandidates
ALTER TABLE periodicity_candidates DROP CONSTRAINT IF EXISTS fk_periodicity_candidates_period_test;
ALTER TABLE periodicity_candidates ADD CONSTRAINT fk_periodicity_candidates_period_test
  FOREIGN KEY (period_test) REFERENCES period_tests (period_test_id);
ALTER TABLE periodicity_candidates DROP CONSTRAINT IF EXISTS fk_periodicity_candidates_earlier_cell;
ALTER TABLE periodicity_candidates ADD CONSTRAINT fk_periodicity_candidates_earlier_cell
  FOREIGN KEY (earlier_cell) REFERENCES cells (cell_id);
ALTER TABLE periodicity_candidates DROP CONSTRAINT IF EXISTS fk_periodicity_candidates_later_cell;
ALTER TABLE periodicity_candidates ADD CONSTRAINT fk_periodicity_candidates_later_cell
  FOREIGN KEY (later_cell) REFERENCES cells (cell_id);
ALTER TABLE periodicity_candidates DROP CONSTRAINT IF EXISTS fk_periodicity_candidates_next_candidate;
ALTER TABLE periodicity_candidates ADD CONSTRAINT fk_periodicity_candidates_next_candidate
  FOREIGN KEY (next_candidate) REFERENCES periodicity_candidates (periodicity_candidate_id);

-- MismatchWindows
ALTER TABLE mismatch_windows DROP CONSTRAINT IF EXISTS fk_mismatch_windows_period;
ALTER TABLE mismatch_windows ADD CONSTRAINT fk_mismatch_windows_period
  FOREIGN KEY (period) REFERENCES periods (period_id);
ALTER TABLE mismatch_windows DROP CONSTRAINT IF EXISTS fk_mismatch_windows_center_test;
ALTER TABLE mismatch_windows ADD CONSTRAINT fk_mismatch_windows_center_test
  FOREIGN KEY (center_test) REFERENCES period_tests (period_test_id);
ALTER TABLE mismatch_windows DROP CONSTRAINT IF EXISTS fk_mismatch_windows_center_candidate;
ALTER TABLE mismatch_windows ADD CONSTRAINT fk_mismatch_windows_center_candidate
  FOREIGN KEY (center_candidate) REFERENCES periodicity_candidates (periodicity_candidate_id);
ALTER TABLE mismatch_windows DROP CONSTRAINT IF EXISTS fk_mismatch_windows_neighbor_candidate;
ALTER TABLE mismatch_windows ADD CONSTRAINT fk_mismatch_windows_neighbor_candidate
  FOREIGN KEY (neighbor_candidate) REFERENCES periodicity_candidates (periodicity_candidate_id);

-- LeftConsistencyChecks
ALTER TABLE left_consistency_checks DROP CONSTRAINT IF EXISTS fk_left_consistency_checks_term;
ALTER TABLE left_consistency_checks ADD CONSTRAINT fk_left_consistency_checks_term
  FOREIGN KEY (term) REFERENCES cells (cell_id);
ALTER TABLE left_consistency_checks DROP CONSTRAINT IF EXISTS fk_left_consistency_checks_next_term;
ALTER TABLE left_consistency_checks ADD CONSTRAINT fk_left_consistency_checks_next_term
  FOREIGN KEY (next_term) REFERENCES cells (cell_id);
ALTER TABLE left_consistency_checks DROP CONSTRAINT IF EXISTS fk_left_consistency_checks_left_cell;
ALTER TABLE left_consistency_checks ADD CONSTRAINT fk_left_consistency_checks_left_cell
  FOREIGN KEY (left_cell) REFERENCES cells (cell_id);

-- WordLetters
ALTER TABLE word_letters DROP CONSTRAINT IF EXISTS fk_word_letters_periodic_word;
ALTER TABLE word_letters ADD CONSTRAINT fk_word_letters_periodic_word
  FOREIGN KEY (periodic_word) REFERENCES periodic_words (periodic_word_id);

-- WordShifts
ALTER TABLE word_shifts DROP CONSTRAINT IF EXISTS fk_word_shifts_periodic_word;
ALTER TABLE word_shifts ADD CONSTRAINT fk_word_shifts_periodic_word
  FOREIGN KEY (periodic_word) REFERENCES periodic_words (periodic_word_id);

-- WordShiftChecks
ALTER TABLE word_shift_checks DROP CONSTRAINT IF EXISTS fk_word_shift_checks_word_shift;
ALTER TABLE word_shift_checks ADD CONSTRAINT fk_word_shift_checks_word_shift
  FOREIGN KEY (word_shift) REFERENCES word_shifts (word_shift_id);
ALTER TABLE word_shift_checks DROP CONSTRAINT IF EXISTS fk_word_shift_checks_letter;
ALTER TABLE word_shift_checks ADD CONSTRAINT fk_word_shift_checks_letter
  FOREIGN KEY (letter) REFERENCES word_letters (word_letter_id);
ALTER TABLE word_shift_checks DROP CONSTRAINT IF EXISTS fk_word_shift_checks_partner_letter;
ALTER TABLE word_shift_checks ADD CONSTRAINT fk_word_shift_checks_partner_letter
  FOREIGN KEY (partner_letter) REFERENCES word_letters (word_letter_id);

-- TailCandidates
ALTER TABLE tail_candidates DROP CONSTRAINT IF EXISTS fk_tail_candidates_run;
ALTER TABLE tail_candidates ADD CONSTRAINT fk_tail_candidates_run
  FOREIGN KEY (run) REFERENCES runs (run_id);
ALTER TABLE tail_candidates DROP CONSTRAINT IF EXISTS fk_tail_candidates_periodic_word;
ALTER TABLE tail_candidates ADD CONSTRAINT fk_tail_candidates_periodic_word
  FOREIGN KEY (periodic_word) REFERENCES periodic_words (periodic_word_id);

-- TailCenterTerms
ALTER TABLE tail_center_terms DROP CONSTRAINT IF EXISTS fk_tail_center_terms_tail_candidate;
ALTER TABLE tail_center_terms ADD CONSTRAINT fk_tail_center_terms_tail_candidate
  FOREIGN KEY (tail_candidate) REFERENCES tail_candidates (tail_candidate_id);
ALTER TABLE tail_center_terms DROP CONSTRAINT IF EXISTS fk_tail_center_terms_real_cell;
ALTER TABLE tail_center_terms ADD CONSTRAINT fk_tail_center_terms_real_cell
  FOREIGN KEY (real_cell) REFERENCES cells (cell_id);
ALTER TABLE tail_center_terms DROP CONSTRAINT IF EXISTS fk_tail_center_terms_letter;
ALTER TABLE tail_center_terms ADD CONSTRAINT fk_tail_center_terms_letter
  FOREIGN KEY (letter) REFERENCES word_letters (word_letter_id);

-- TailCells
ALTER TABLE tail_cells DROP CONSTRAINT IF EXISTS fk_tail_cells_tail_candidate;
ALTER TABLE tail_cells ADD CONSTRAINT fk_tail_cells_tail_candidate
  FOREIGN KEY (tail_candidate) REFERENCES tail_candidates (tail_candidate_id);
ALTER TABLE tail_cells DROP CONSTRAINT IF EXISTS fk_tail_cells_real_cell;
ALTER TABLE tail_cells ADD CONSTRAINT fk_tail_cells_real_cell
  FOREIGN KEY (real_cell) REFERENCES cells (cell_id);
ALTER TABLE tail_cells DROP CONSTRAINT IF EXISTS fk_tail_cells_left_parent;
ALTER TABLE tail_cells ADD CONSTRAINT fk_tail_cells_left_parent
  FOREIGN KEY (left_parent) REFERENCES tail_cells (tail_cell_id);
ALTER TABLE tail_cells DROP CONSTRAINT IF EXISTS fk_tail_cells_center_parent;
ALTER TABLE tail_cells ADD CONSTRAINT fk_tail_cells_center_parent
  FOREIGN KEY (center_parent) REFERENCES tail_cells (tail_cell_id);
ALTER TABLE tail_cells DROP CONSTRAINT IF EXISTS fk_tail_cells_right_parent;
ALTER TABLE tail_cells ADD CONSTRAINT fk_tail_cells_right_parent
  FOREIGN KEY (right_parent) REFERENCES tail_cells (tail_cell_id);
ALTER TABLE tail_cells DROP CONSTRAINT IF EXISTS fk_tail_cells_center_term;
ALTER TABLE tail_cells ADD CONSTRAINT fk_tail_cells_center_term
  FOREIGN KEY (center_term) REFERENCES tail_center_terms (tail_center_term_id);

-- TailChecks
ALTER TABLE tail_checks DROP CONSTRAINT IF EXISTS fk_tail_checks_tail_candidate;
ALTER TABLE tail_checks ADD CONSTRAINT fk_tail_checks_tail_candidate
  FOREIGN KEY (tail_candidate) REFERENCES tail_candidates (tail_candidate_id);
ALTER TABLE tail_checks DROP CONSTRAINT IF EXISTS fk_tail_checks_term;
ALTER TABLE tail_checks ADD CONSTRAINT fk_tail_checks_term
  FOREIGN KEY (term) REFERENCES tail_center_terms (tail_center_term_id);
ALTER TABLE tail_checks DROP CONSTRAINT IF EXISTS fk_tail_checks_next_term;
ALTER TABLE tail_checks ADD CONSTRAINT fk_tail_checks_next_term
  FOREIGN KEY (next_term) REFERENCES tail_center_terms (tail_center_term_id);
ALTER TABLE tail_checks DROP CONSTRAINT IF EXISTS fk_tail_checks_real_left_cell;
ALTER TABLE tail_checks ADD CONSTRAINT fk_tail_checks_real_left_cell
  FOREIGN KEY (real_left_cell) REFERENCES cells (cell_id);
ALTER TABLE tail_checks DROP CONSTRAINT IF EXISTS fk_tail_checks_tail_left_cell;
ALTER TABLE tail_checks ADD CONSTRAINT fk_tail_checks_tail_left_cell
  FOREIGN KEY (tail_left_cell) REFERENCES tail_cells (tail_cell_id);
ALTER TABLE tail_checks DROP CONSTRAINT IF EXISTS fk_tail_checks_next_check;
ALTER TABLE tail_checks ADD CONSTRAINT fk_tail_checks_next_check
  FOREIGN KEY (next_check) REFERENCES tail_checks (tail_check_id);

-- Diagonals
ALTER TABLE diagonals DROP CONSTRAINT IF EXISTS fk_diagonals_previous_diagonal;
ALTER TABLE diagonals ADD CONSTRAINT fk_diagonals_previous_diagonal
  FOREIGN KEY (previous_diagonal) REFERENCES diagonals (diagonal_id);
ALTER TABLE diagonals DROP CONSTRAINT IF EXISTS fk_diagonals_opposite_diagonal;
ALTER TABLE diagonals ADD CONSTRAINT fk_diagonals_opposite_diagonal
  FOREIGN KEY (opposite_diagonal) REFERENCES diagonals (diagonal_id);

-- DiagonalPeriodTests
ALTER TABLE diagonal_period_tests DROP CONSTRAINT IF EXISTS fk_diagonal_period_tests_diagonal;
ALTER TABLE diagonal_period_tests ADD CONSTRAINT fk_diagonal_period_tests_diagonal
  FOREIGN KEY (diagonal) REFERENCES diagonals (diagonal_id);
ALTER TABLE diagonal_period_tests DROP CONSTRAINT IF EXISTS fk_diagonal_period_tests_half_cell;
ALTER TABLE diagonal_period_tests ADD CONSTRAINT fk_diagonal_period_tests_half_cell
  FOREIGN KEY (half_cell) REFERENCES cells (cell_id);

-- DiagonalPeriodChecks
ALTER TABLE diagonal_period_checks DROP CONSTRAINT IF EXISTS fk_diagonal_period_checks_diagonal_period_test;
ALTER TABLE diagonal_period_checks ADD CONSTRAINT fk_diagonal_period_checks_diagonal_period_test
  FOREIGN KEY (diagonal_period_test) REFERENCES diagonal_period_tests (diagonal_period_test_id);
ALTER TABLE diagonal_period_checks DROP CONSTRAINT IF EXISTS fk_diagonal_period_checks_earlier_cell;
ALTER TABLE diagonal_period_checks ADD CONSTRAINT fk_diagonal_period_checks_earlier_cell
  FOREIGN KEY (earlier_cell) REFERENCES cells (cell_id);
ALTER TABLE diagonal_period_checks DROP CONSTRAINT IF EXISTS fk_diagonal_period_checks_later_cell;
ALTER TABLE diagonal_period_checks ADD CONSTRAINT fk_diagonal_period_checks_later_cell
  FOREIGN KEY (later_cell) REFERENCES cells (cell_id);

-- DiagonalFacts
ALTER TABLE diagonal_facts DROP CONSTRAINT IF EXISTS fk_diagonal_facts_diagonal;
ALTER TABLE diagonal_facts ADD CONSTRAINT fk_diagonal_facts_diagonal
  FOREIGN KEY (diagonal) REFERENCES diagonals (diagonal_id);

-- ToleranceChecks
ALTER TABLE tolerance_checks DROP CONSTRAINT IF EXISTS fk_tolerance_checks_tolerance;
ALTER TABLE tolerance_checks ADD CONSTRAINT fk_tolerance_checks_tolerance
  FOREIGN KEY (tolerance) REFERENCES tolerances (tolerance_id);
ALTER TABLE tolerance_checks DROP CONSTRAINT IF EXISTS fk_tolerance_checks_cell;
ALTER TABLE tolerance_checks ADD CONSTRAINT fk_tolerance_checks_cell
  FOREIGN KEY (cell) REFERENCES cells (cell_id);

-- ColorCounts
ALTER TABLE color_counts DROP CONSTRAINT IF EXISTS fk_color_counts_column;
ALTER TABLE color_counts ADD CONSTRAINT fk_color_counts_column
  FOREIGN KEY ("column") REFERENCES columns (column_id);
ALTER TABLE color_counts DROP CONSTRAINT IF EXISTS fk_color_counts_cell_state;
ALTER TABLE color_counts ADD CONSTRAINT fk_color_counts_cell_state
  FOREIGN KEY (cell_state) REFERENCES cell_states (cell_state_id);

-- Algorithms
ALTER TABLE algorithms DROP CONSTRAINT IF EXISTS fk_algorithms_machine_model;
ALTER TABLE algorithms ADD CONSTRAINT fk_algorithms_machine_model
  FOREIGN KEY (machine_model) REFERENCES machine_models (machine_model_id);

-- Computations
ALTER TABLE computations DROP CONSTRAINT IF EXISTS fk_computations_algorithm;
ALTER TABLE computations ADD CONSTRAINT fk_computations_algorithm
  FOREIGN KEY (algorithm) REFERENCES algorithms (algorithm_id);
ALTER TABLE computations DROP CONSTRAINT IF EXISTS fk_computations_time_step;
ALTER TABLE computations ADD CONSTRAINT fk_computations_time_step
  FOREIGN KEY (time_step) REFERENCES time_steps (time_step_id);

-- Terms
ALTER TABLE terms DROP CONSTRAINT IF EXISTS fk_terms_term_operator;
ALTER TABLE terms ADD CONSTRAINT fk_terms_term_operator
  FOREIGN KEY (term_operator) REFERENCES operators (operator_id);
ALTER TABLE terms DROP CONSTRAINT IF EXISTS fk_terms_variable;
ALTER TABLE terms ADD CONSTRAINT fk_terms_variable
  FOREIGN KEY (variable) REFERENCES variables (variable_id);
ALTER TABLE terms DROP CONSTRAINT IF EXISTS fk_terms_arg1;
ALTER TABLE terms ADD CONSTRAINT fk_terms_arg1
  FOREIGN KEY (arg1) REFERENCES terms (term_id);
ALTER TABLE terms DROP CONSTRAINT IF EXISTS fk_terms_arg2;
ALTER TABLE terms ADD CONSTRAINT fk_terms_arg2
  FOREIGN KEY (arg2) REFERENCES terms (term_id);
ALTER TABLE terms DROP CONSTRAINT IF EXISTS fk_terms_arg3;
ALTER TABLE terms ADD CONSTRAINT fk_terms_arg3
  FOREIGN KEY (arg3) REFERENCES terms (term_id);
ALTER TABLE terms DROP CONSTRAINT IF EXISTS fk_terms_arg4;
ALTER TABLE terms ADD CONSTRAINT fk_terms_arg4
  FOREIGN KEY (arg4) REFERENCES terms (term_id);
ALTER TABLE terms DROP CONSTRAINT IF EXISTS fk_terms_introduced_in_loop;
ALTER TABLE terms ADD CONSTRAINT fk_terms_introduced_in_loop
  FOREIGN KEY (introduced_in_loop) REFERENCES loops (loop_id);

-- Predicates
ALTER TABLE predicates DROP CONSTRAINT IF EXISTS fk_predicates_root_term;
ALTER TABLE predicates ADD CONSTRAINT fk_predicates_root_term
  FOREIGN KEY (root_term) REFERENCES terms (term_id);
ALTER TABLE predicates DROP CONSTRAINT IF EXISTS fk_predicates_introduced_in_loop;
ALTER TABLE predicates ADD CONSTRAINT fk_predicates_introduced_in_loop
  FOREIGN KEY (introduced_in_loop) REFERENCES loops (loop_id);

-- PredicateInstances
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_predicate;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_predicate
  FOREIGN KEY (predicate) REFERENCES predicates (predicate_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_introduced_in_loop;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_introduced_in_loop
  FOREIGN KEY (introduced_in_loop) REFERENCES loops (loop_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_rule_table_entry;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_rule_table_entry
  FOREIGN KEY (rule_table_entry) REFERENCES rule_table_entries (rule_table_entry_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_run;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_run
  FOREIGN KEY (run) REFERENCES runs (run_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_period_test;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_period_test
  FOREIGN KEY (period_test) REFERENCES period_tests (period_test_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_periodicity_candidate;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_periodicity_candidate
  FOREIGN KEY (periodicity_candidate) REFERENCES periodicity_candidates (periodicity_candidate_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_mismatch_window;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_mismatch_window
  FOREIGN KEY (mismatch_window) REFERENCES mismatch_windows (mismatch_window_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_cell;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_cell
  FOREIGN KEY (cell) REFERENCES cells (cell_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_left_consistency_check;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_left_consistency_check
  FOREIGN KEY (left_consistency_check) REFERENCES left_consistency_checks (left_consistency_check_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_tail_candidate;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_tail_candidate
  FOREIGN KEY (tail_candidate) REFERENCES tail_candidates (tail_candidate_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_diagonal_period_test;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_diagonal_period_test
  FOREIGN KEY (diagonal_period_test) REFERENCES diagonal_period_tests (diagonal_period_test_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_diagonal_fact;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_diagonal_fact
  FOREIGN KEY (diagonal_fact) REFERENCES diagonal_facts (diagonal_fact_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_accelerator_claim;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_accelerator_claim
  FOREIGN KEY (accelerator_claim) REFERENCES accelerator_claims (accelerator_claim_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_tolerance;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_tolerance
  FOREIGN KEY (tolerance) REFERENCES tolerances (tolerance_id);
ALTER TABLE predicate_instances DROP CONSTRAINT IF EXISTS fk_predicate_instances_algorithm;
ALTER TABLE predicate_instances ADD CONSTRAINT fk_predicate_instances_algorithm
  FOREIGN KEY (algorithm) REFERENCES algorithms (algorithm_id);

-- AcceleratorClaims
ALTER TABLE accelerator_claims DROP CONSTRAINT IF EXISTS fk_accelerator_claims_cell;
ALTER TABLE accelerator_claims ADD CONSTRAINT fk_accelerator_claims_cell
  FOREIGN KEY (cell) REFERENCES cells (cell_id);
ALTER TABLE accelerator_claims DROP CONSTRAINT IF EXISTS fk_accelerator_claims_source;
ALTER TABLE accelerator_claims ADD CONSTRAINT fk_accelerator_claims_source
  FOREIGN KEY (source) REFERENCES evidence (evidence_id);

-- 118 FK constraint(s) declared (off unless EFFORTLESS_ENFORCE_FKS=true).
