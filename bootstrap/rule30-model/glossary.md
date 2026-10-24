# Glossary: the Rule 30 problem

Shadle step 3. Every term in `vocabulary.txt`, grouped by area, one or two sentences each.

## 1. The automaton

- **Cellular automaton**: a line of cells, each in one of finitely many states, all updated at once from their neighbors by one fixed rule.
- **Cell state**: the value a cell holds, 0 or 1.
- **Color**: the name of a cell state: **white** is 0, **black** is 1.
- **Neighborhood**: the three cells a new cell is computed from: its **left neighbor**, itself (the center), and its **right neighbor**, together its **immediate neighbors**. There are 8 neighborhoods, written as three bits (111 … 000).
- **Rule**: the function from the 8 neighborhoods to a new state.
- **Rule table**: the 8 transitions of one rule, one per neighborhood, each with its **output value**.
- **Rule number**: Wolfram's name for a rule: the output for neighborhood n (left·4 + center·2 + right) is bit n of the rule number.
- **Rule 30**: the rule with rule number 30: new = left XOR (center OR right).
- **XOR** / **OR**: exclusive-or and inclusive-or on bits; Rule 30 is one XOR of the left neighbor with the OR of the other two.
- **Polynomial**: Wolfram's algebraic form of Rule 30 over 0/1 values, Mod[p + q + r + q·r, 2] with p, q, r the left, center and right cells.
- **Mirror rule**: the rule obtained by swapping left and right; Rule 30's mirror is Rule 86.
- **Complement rule**: the rule obtained by swapping black and white in inputs and output; Rule 30's complement is Rule 135 (and the mirror of that is 149).
- **Equivalence class**: the rules reachable from one rule by mirroring and complementing; {30, 86, 135, 149} behave identically up to reflection and color swap.
- **Quiescent**: a rule is quiescent when the all-white neighborhood 000 outputs white, so an all-white background stays white.

## 2. Initial condition and evolution

- **Initial condition**: the states of all cells at time 0.
- **Single seed**: the initial condition of the prize problems: one **nonzero cell** (black) at position 0, every other cell white.
- **Background**: the state of every cell the initial condition does not list explicitly (white for the single seed).
- **Infinite lattice**: the cells at every integer position and every time step; the problems are about this unbounded object.
- **Position**: a cell's integer coordinate i on the line; 0 is the seed.
- **Time step**: the integer t ≥ 0 counting updates; one time step is one **line** (row) of the picture.
- **Evolution**: the sequence of lines produced by applying the rule to the initial condition again and again.
- **Run**: one evolution, fixed by a rule, an initial condition and a **depth** (the last time step computed).
- **Light cone**: the cells with |i| ≤ t; under a quiescent rule from a single seed every cell outside it stays white, so only the cone needs computing.
- **Width**: the number of cells in the light cone at a time step, 2t + 1.
- **Cell updates**: the number of cells computed; simulating the cone up to time n costs (n+1)² − 1 of them.

## 3. The center column

- **Column**: the cells at one position over all time steps, read as a sequence in t.
- **Center column**: the column at position 0, c(t) = x(0, t): the **sequence** of **center-cell values** all three problems are about.
- **Term**: one value c(t) of the sequence.
- **Prefix**: the first N terms c(0), …, c(N−1).
- **Horizon**: the last time step a finite computation sees; the model's horizon is the run's depth.

## 4. Problem 1: periodicity

- **Period**: a positive integer p.
- **Periodic** (from onset T with period p): c(t + p) = c(t) for every t ≥ T.
- **Onset**: the time T (Wolfram's i) from which a periodicity is claimed to hold.
- **Eventually periodic**: periodic from some onset with some period; **non-periodic** means not eventually periodic, which is Problem 1.
- **Comparison**: one test of c(t) against c(t + p) for a fixed period.
- **Mismatch**: a comparison with c(t + p) ≠ c(t); one mismatch at t ≥ T refutes periodicity with period p from onset T.
- **Agreement streak**: the number of consecutive matching comparisons ending at t for one period.
- **Constant run**: a maximal stretch of equal consecutive terms.
- **Eventually constant**: periodic with period 1; known to be false for the center column.
- **Center-run bounds**: Theorem D: a run of black starting at T ends by 2T + 1, a run of white by 4T + 5.

## 5. Problem 2: frequency

- **Frequency** (of a color): how often that color occurs in a prefix, as a count or a share.
- **Equally often**: both colors have limiting frequency 1/2.
- **Average** / **density**: the share of black in the prefix, (number of 1s) / N.
- **Discrepancy**: ones minus zeros in the prefix, 2·(ones) − N; density 1/2 in the limit means discrepancy o(N).
- **Limit**: the value the density tends to as N grows without bound; Problem 2 says it is 1/2.
- **Tolerance**: a margin ε around 1/2.
- **Excursion**: a prefix whose density is more than ε away from 1/2.

## 6. Problem 3: computational effort

- **Computational effort**: the cost t a machine spends to output c(n), counted in its own steps.
- **Machine**: a finite program m with machine[m][n] = {v, t}: the output value and the effort.
- **Machine model**: what a step is: a **Turing machine** move, a cellular-automaton cell update, a RAM instruction. The **cost model** and the **encoding** of n (binary) must be fixed for a claim to be precise.
- **Algorithm**: one concrete way of computing c(n) on a machine model.
- **Store the answer**: a machine whose rule contains the sequence itself; it is ruled out.
- **Admissible**: an algorithm that does not store the answer.
- **Effort ratio**: effort / n.
- **Limsup**: the eventual upper bound of the effort ratio; finite limsup means effort O(n).
- **O(n)** / **sublinear**: linear effort; less than linear. **O(n²)** is the cost of direct simulation; beating it is a stated **partial result**.

## 7. Predicates and the logic of the problem

- **Predicate**: a property stated about the model, such as "the center column is not periodic with period p from onset T".
- **Quantifier**: one **for all**, **exists** or **not exists** binding a **variable** over a **domain** (time steps, periods, onsets, machines).
- **Unbounded**: a quantifier whose domain is infinite in the problem; no finite run can decide it.
- **Instance**: one bounded case of a predicate inside the model (one period, one cell, one tolerance).
- **Holds**: the instance is true when computed from the model's own cells.
- **Witness**: the row that decides an instance, such as the mismatch that refutes a periodicity.
- **Finite verification**: a predicate that holds on every instance within the horizon; evidence, not proof, for an unbounded statement.
- **Theorem**: a statement with a proof covering every instance, bounded or not.
- **Claim**: a value or statement reported by something outside the model.
- **Accelerator**: a program outside the rulebook that computes values faster; its claims are checked against the model's own cells.
- **Prize problem**: one of the three statements above, all of which quantify over unbounded domains.
