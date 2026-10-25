"""Lean proofs of the ledger's claims (loaded into LeanProofs by build_challenge.py).

The statement of each theorem is NOT here: research/lean/ledger.py writes it from the claim's term tree
(Assertions.LeanStatement, computed by the build). A proof here is only the part after `:=`. When a claim's
statement changes, the proof is checked against the new statement on the next build; if it no longer fits,
the check fails and the claim drops back to its reported status. Nothing here can make a claim verified
that the kernel does not accept.

kind 'claim'      proves the claim's Lean statement.
kind 'alignment'  proves the claim's Lean statement equivalent to an official constant (target).
kit               the kit declarations the proof cites; a proof that only restates them (kit_glue) marks
                  the claim as known in the kit.

The vocabulary (c, x, y, w, rule30, P, bit, ...) is the prelude in research/lean/ledger.py.
"""
PROOFS = [
    {'claim': 'P1', 'kind': 'alignment', 'target': 'Ruliology.CellularAutomata.Rule30Prize.Problem1', 'kit_glue': False,
     'kit': ['Rule30Prize.Problem1', 'Rule30Jen.EventuallyPeriodic'],
     'note': "Our formal P1 says exactly what the official Problem1 says: c is a 0/1 copy of the kit's center.",
     'proof': '''by
  unfold Rule30Prize.Problem1 Rule30Jen.EventuallyPeriodic
  constructor
  · rintro h ⟨T, p, hp, hper⟩
    exact h ⟨p, hp, T, Nat.zero_le _, fun t ht => by simp only [c]; rw [hper t ht]⟩
  · rintro h ⟨p, hp, T, -, hper⟩
    exact h ⟨T, p, hp, fun t ht => bit_inj.mp (hper t ht)⟩'''},
    {'claim': 'K1', 'kind': 'claim', 'kit_glue': True, 'kit': ['Rule30Prize.center_not_eventually_period_one'],
     'note': 'Period 1 of Problem 1 is the kit theorem, with 0/1 cells.',
     'proof': '''by
  rintro ⟨T, -, h⟩
  exact Rule30Prize.center_not_eventually_period_one ⟨T, fun t ht => bit_inj.mp (h t ht)⟩'''},
    {'claim': 'T0', 'kind': 'claim', 'kit_glue': True, 'kit': ['Rule30Jen.cell_left_edge', 'Rule30Diagonals.R_zero'],
     'note': 'Both boundary cells are black: the left edge from the kit, the right edge as the zeroth right diagonal.',
     'proof': '''by
  intro t _
  refine ⟨?_, ?_⟩
  · simp [x, bit, Rule30Jen.cell_left_edge]
  · have h := Rule30Diagonals.R_zero t
    simp only [Rule30Diagonals.R, Nat.cast_zero, Int.sub_zero] at h
    simp [x, bit, h]'''},
    {'claim': 'TX', 'kind': 'claim', 'kit_glue': True, 'kit': ['Rule30MaskedJen.left_of_black'],
     'note': 'Left-consistency: after a black center cell the rule forces the next center cell to the complement of x(-1, t).',
     'proof': '''by
  intro t _ h
  have h' := Rule30MaskedJen.left_of_black t 0 (bit_eq_one.mp h)
  simp only [Int.zero_sub] at h'
  show bit (Rule30Jen.cell (t + 1) 0) = 1 - bit (Rule30Jen.cell t (-1))
  rw [h']
  cases Rule30Jen.cell (t + 1) 0 <;> rfl'''},
    {'claim': 'D0', 'kind': 'claim', 'kit_glue': True, 'kit': ['Rule30Jen.cell'],
     'note': "The prize setup is the kit's definition of the evolution.",
     'proof': '''by
  refine ⟨⟨by simp [x, bit, Rule30Jen.cell], fun i hi => by simp [x, bit, Rule30Jen.cell, hi]⟩, fun t _ i _ => ?_⟩
  show bit (Rule30Jen.cell (t + 1) i) = rule30 (bit (Rule30Jen.cell t (i - 1))) (bit (Rule30Jen.cell t i)) (bit (Rule30Jen.cell t (i + 1)))
  rw [Rule30Jen.cell]
  simp only [rule30, bit_beq_one]'''},
    {'claim': 'TS', 'kind': 'claim', 'kit_glue': False, 'kit': ['Rule30Jen.cell', 'Rule30Jen.rule'],
     'note': "Column transfer, proved here from the rule at times t and t + p (ours; the kit has the one-step facts left_of_black and left_of_white).",
     'proof': '''by
  intro p _ t _ hyp
  obtain ⟨h0, h1⟩ := hyp
  have e1 : Rule30Jen.cell (t + 1) 0 = Rule30Jen.rule (Rule30Jen.cell t (-1)) (Rule30Jen.cell t 0) (Rule30Jen.cell t 1) := by
    rw [Rule30Jen.cell]; rfl
  have e2 : Rule30Jen.cell (t + 1 + p) 0 = Rule30Jen.rule (Rule30Jen.cell (t + p) (-1)) (Rule30Jen.cell (t + p) 0) (Rule30Jen.cell (t + p) 1) := by
    rw [show t + 1 + p = (t + p) + 1 by omega, Rule30Jen.cell]; rfl
  simp only [x, c, Rule30Prize.center, bit_inj] at h0 h1 ⊢
  rw [e1, e2] at h1
  revert h0 h1
  generalize Rule30Jen.cell t (-1) = a, Rule30Jen.cell t 0 = b, Rule30Jen.cell t 1 = r,
    Rule30Jen.cell (t + p) (-1) = a', Rule30Jen.cell (t + p) 0 = b', Rule30Jen.cell (t + p) 1 = r'
  cases a <;> cases b <;> cases r <;> cases a' <;> cases b' <;> cases r' <;> simp [Rule30Jen.rule, bit]'''},
    {'claim': 'T004', 'kind': 'claim', 'kit_glue': True, 'kit': ['Rule30Diagonals.R_periodic'],
     'note': "The least period of y_k divides 2^k, because 2^k is a period (the kit's R_periodic).",
     'proof': '''by
  intro k _
  show Function.minimalPeriod shift (y k) ∣ 2 ^ k
  apply Function.IsPeriodicPt.minimalPeriod_dvd
  show shift^[2 ^ k] (y k) = y k
  rw [iterate_shift]
  funext t
  simp only [y, Rule30Diagonals.R_periodic]'''},
]
