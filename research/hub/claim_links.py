"""Our claims set against the kit's Lean declarations (loaded into ClaimLinks by build_challenge.py).

Each link reads two statements side by side: ours (Assertions.Statement and its term tree) and the kit's
(LeanDeclarations.Statement). The relation is the kit declaration relative to our claim:

  same         it states our claim (up to notation: Bool cells for 0/1 cells, 2^e for a least period)
  stronger     it states more, and our claim follows at once
  jointly      our claim is the conjunction of every 'jointly' declaration linked to it
  weaker       it states less (our claim is the stronger one)
  related      it is about the same thing, and neither follows from the other at once
  contradicts  it proves the negation of our claim

A link is a reading. The model counts a claim as known in the kit (IsKnownInKit) when a verified kit
theorem is linked same or stronger, or every 'jointly' one is verified. A proof is a LeanChecks pass.
Names are relative to Ruliology.CellularAutomata unless they start with Rule30Equivalents.
"""
NS = 'Ruliology.CellularAutomata.'

_LINKS = [
    # --- the prize problems: the official statements ---
    ('P1', 'Rule30Prize.Problem1', 'same', 'The official statement: the center column is not eventually periodic.'),
    ('P2', 'Rule30Prize.Problem2', 'same', 'The official statement, in integers: for every k > 0, eventually k |2 blackCount n - n| <= n.'),
    ('P3', 'Rule30Problem3.Problem3', 'related', "The kit's reference model of Problem 3 (one-tape Turing machine on the binary digits of n); the prize has no official Lean statement."),
    ('P2', 'Rule30CenterRuns.log_two_le_blackCount', 'related', 'The only unconditional density fact: at least log2 n black cells among the first n.'),
    # --- period 1 ---
    ('K1', 'Rule30Prize.center_not_eventually_period_one', 'same', 'Period 1 of Problem 1, exactly.'),
    ('K1', 'Rule30Prize.no_column_eventually_constant', 'stronger', 'Every column, not only the center.'),
    # --- the setup and local facts ---
    ('D0', 'Rule30Jen.cell', 'related', "The kit's definition of the evolution: cell 0 p = (p = 0), cell (t+1) p = rule (cell t (p-1)) (cell t p) (cell t (p+1))."),
    ('T0', 'Rule30Jen.cell_left_edge', 'jointly', 'The left boundary cell x(-t, t) is black.'),
    ('T0', 'Rule30Diagonals.R_zero', 'jointly', 'The right boundary cell x(t, t) is black (R 0 t = cell t t).'),
    ('TX', 'Rule30MaskedJen.left_of_black', 'same', 'At i = 0: if c(t) = 1 then x(-1, t) = NOT c(t + 1).'),
    ('TX', 'Rule30DrivenLeft.cell_eq_L', 'related', "TX's second half: the left half is the half driven by the center column (L with the center as boundary)."),
    ('TS', 'Rule30MaskedJen.left_of_black', 'related', 'The local step behind TS when c(t) = 1.'),
    ('TS', 'Rule30MaskedJen.left_of_white', 'related', 'The local step behind TS when c(t) = 0.'),
    ('TE', 'Rule30Jen.cell_left', 'related', 'Left permutivity: the cell to the left is determined by the cell below and its neighbours.'),
    ('TC', 'Rule30MaskedJen.finitary_jen', 'related', 'A finite-window form of Jen: a period on the center and on the or-column cannot both hold over [n - P, 2n).'),
    ('TC', 'Rule30MaskedJen.periodic_window', 'related', 'With a periodic center, every window [n, 2n) past T + P has a white time where column 1 breaks the period.'),
    ('TD', 'Rule30CenterRuns.black_run_le', 'jointly', 'A black center run starting at a >= 1 has length at most a (ours: it ends by 2T + 1).'),
    ('TD', "Rule30CenterRuns.white_run_le'", 'jointly', 'A white center run starting at a >= 1 has length at most a - 1 (ours: it ends by 4T + 5).'),
    # --- finite windows on periods ---
    ('F3', 'Rule30Window.no_small_eventual_period', 'weaker', "Kernel-checked: no eventual period P <= 4096 with transient T <= 8192. F3 (by computation, not in Lean) covers p <= 10000, T <= 90000."),
    ('F6', 'Rule30Window.no_small_eventual_period', 'weaker', 'Kernel-checked window P <= 4096, T <= 8192. F6 (by computation, not in Lean) covers p <= 2^17, T <= 917498.'),
    ('F6', 'Rule30FactorWindow.transient_add_period_ge', 'related', 'Kernel-checked: any eventual period has T + P >= 16359.'),
    ('H21', 'Rule30FactorWindow.transient_add_period_ge', 'related', 'Agreement runs and the transient-plus-period bound.'),
    # --- right diagonals ---
    ('T004', 'Rule30Diagonals.R_periodic', 'same', 'y_k = R k repeats with period 2^k from time 0, so its least period divides 2^k.'),
    ('TB', 'Rule30RightPeriods.R_half', 'jointly', 'y_k is black at ceil(k/2) (R j ((j+1)/2) = true).'),
    ('TB', 'Rule30RightPeriods.R_lt', 'jointly', 'y_k is white before ceil(k/2) (2t < j -> R j t = false).'),
    ('TB', 'Rule30RightPeriods.period_gt', 'jointly', 'Every period of y_k (k >= 1) exceeds ceil(k/2) - 1, i.e. (k+1)/2 < P.'),
    ('H4', 'Rule30RightPeriods.e_mono', 'same', 'The least dyadic exponents never decrease: e_j <= e_{j+1} (P_k = 2^{e_k}).'),
    ('TL', 'Rule30RightPeriods.e_step', 'jointly', 'e_{j+1} = e_j + [R_{j+1}(2^{e_j}) = 1]: the period repeats or doubles.'),
    ('TL', 'Rule30RightPeriods.not_per_small', 'jointly', 'The periods are unbounded, so the period doubles infinitely often.'),
    ('TN', 'Rule30RightPeriods.no_three', 'same', 'The period never doubles three times in a row.'),
    ('TM', 'Rule30RightPeriods.S_rule', 'related', 'e_{n+3} - e_{n+2} is the parity of the black input cells over one period of the input.'),
    ('H15', 'Rule30RightPeriods.S_rule', 'related', 'The doubling parity rule.'),
    ('TO', 'Rule30RightPeriods.half_black', 'related', 'After a doubling, every window of one period is exactly half black.'),
    ('H7', 'Rule30RightPeriods.inp_least_period', 'same', 'The input R_{n+1} || R_n of diagonal n+2 has least period 2^{e_{n+2}}... every period of it is a multiple of that.'),
    ('TK', 'Rule30RightPeriods.inp_least_period', 'jointly', 'Q_k = max(P_{k-1}, P_{k-2}): the least period of the forcing word.'),
    ('TK', 'Rule30RightPeriods.e_mono', 'jointly', 'And the least periods are nondecreasing.'),
    ('TI', 'Rule30RightPeriods.e_mono', 'stronger', 'Monotonicity itself, without H7.'),
    ('TF', 'Rule30RightPeriods.inp_least_period', 'related', 'The forcing word and its least period.'),
    ('TG', 'Rule30RightPeriods.antiperiod_of_black', 'related', 'A black cell at the period makes the next diagonal antiperiodic.'),
    ('TH', 'Rule30RightPeriods.inp_least_period', 'related', 'The forcing period from the parents.'),
    ('TJ', 'Rule30RightPeriods.inp_least_period', 'related', 'The cascade lemma, in the kit as the input period theorem.'),
    ('TA', 'Rule30Diagonals.xor_accum_periodic', 'related', 'An accumulated parity of a periodic input is periodic with twice the period.'),
    ('TP', 'Rule30RightPeriods.per_upper', 'related', 'An upper bound on the dyadic exponents: e_j <= (2j + 1)/3.'),
    ('H2', 'Rule30RightPeriods.per_14', 'contradicts', 'e_14 <= 6: the period does not double at every k >= 3 (H2 is falsified in the ledger too).'),
    # --- left diagonals ---
    ('TR', 'Rule30Diagonals.D_periodic', 'same', 'w_k = D k is eventually periodic with period 2^k, so its least eventual period divides 2^k.'),
    # --- the center runs (finite checks of ours) ---
    ('H13', 'Rule30CenterRuns.black_run_le', 'related', 'Uniform bounds on center runs.'),
    # --- the attack on P1: the left half ---
    ('B9', 'Rule30DrivenLeft.cell_eq_L', 'related', 'The left half as the half driven by the center: the frame of B9 and TX.'),
    ('B1', 'Rule30Coupled.problem1_of_CQ', 'related', "The kit's coupled questions: for every periodic word, no finite halves are coupled to it; together they imply Problem 1."),
    ('B7', 'Rule30PeriodTwo.Q01', 'related', "The kit's open statement for period 2, in the driven-left-half form: no finite start keeps column -1 black at every even time."),
    ('B7', 'Rule30ZeroBoundary.Q01', 'related', "The same open statement in the zero-boundary form (Q01)."),
    ('B8', 'Rule30Coupled.problem1_of_CQ', 'related', 'Every period at once, as coupled questions.'),
    ('B5', 'Rule30DrivenLeft.light_cone', 'related', 'The light cone of the driven left half: what the relaxation of B5 uses.'),
    ('TU', 'Rule30DrivenLeft.exists_prefix', 'related', 'Any finite prefix of column -1 is realized by some finite start: the free bits of TU.'),
    ('TV', 'Rule30DrivenLeft.L_left', 'related', 'The left step of the driven half, unrolled by TV along a light ray.'),
    ('TW', 'Rule30DrivenLeft.barrier_exists', 'related', 'A barrier start realizes any boundary word: the counting behind TW.'),
    ('TY', 'Rule30ZeroBoundaryBarriers.no_finite_abstract_ranking', 'related', 'Barriers to finite-state arguments for Q01, as TY is for window languages.') ,
]
LINKS = [(aid, decl if decl.startswith('Rule30Equivalents') else NS + decl, rel, note) for aid, decl, rel, note in _LINKS]
