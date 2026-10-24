# Narrative: a running instance of Rule 30

Shadle step 4. One pass through the whole problem, using every vocabulary word.

A **cellular automaton** is a line of **cells**. Each cell has a **cell state**, 0 or 1, and
each state has a **color**: **white** for 0, **black** for 1. At every **time step** each cell
looks at its **neighborhood**, its **left neighbor**, itself and its **right neighbor** (its
**immediate neighbors**), and the **rule** gives its new state. Because a neighborhood is three
bits there are 8 of them, so a rule is fully written down by its **rule table**: 8 transitions,
each with one **output value**. Wolfram names a rule by its **rule number**, the 8 output values
read as a binary number. **Rule 30** is rule number 30. Its table says the new cell is the left
neighbor **XOR** (center **OR** right), which over 0/1 values is the **polynomial**
Mod[p + q + r + q·r, 2]. Swapping left and right gives its **mirror rule**, 86; swapping black
and white gives its **complement rule**, 135; together with 149 they form one **equivalence
class**. Rule 30 is **quiescent**: the all-white neighborhood stays white.

A **run** starts from an **initial condition**. The prize problems use the **single seed**: one
**nonzero cell** at **position** 0 on a white **background**, on an **infinite lattice** of
positions. The **evolution** produces one **line** per time step. Because the rule is quiescent,
nothing outside the **light cone** |i| ≤ t ever turns black, so a run only computes the cone up
to its **depth**: at time t the cone's **width** is 2t + 1, and reaching time n costs
(n + 1)² − 1 **cell updates**.

Every position defines a **column**, the cells at that position over time. The **center
column**, position 0, is the **sequence** of **center-cell values** c(0), c(1), c(2), …; each
c(t) is a **term**, the first N terms are a **prefix**, and a run's depth is its **horizon**:
the last term it can see.

**Problem 1** asks whether the center column is **non-periodic**. A **period** p and an
**onset** T make it **periodic** if c(t + p) = c(t) for every t ≥ T; it is **eventually
periodic** if some p and T do. The model tests each period with one **comparison** per t: c(t)
against c(t + p). A single **mismatch** at or after T refutes the pair (p, T), so the last
mismatch for a period tells exactly which onsets the horizon refutes. Between mismatches the
comparisons build an **agreement streak**. Period 1 is the **eventually constant** case, already
known false, and its finer form is about **constant runs**: the **center-run bounds** (Theorem D)
say a black run that starts at T ends by 2T + 1 and a white one by 4T + 5.

**Problem 2** asks whether each color occurs **equally often** on **average**. The model counts
the **frequency** of each color in every prefix, divides to get the **density**, and tracks the
**discrepancy**, ones minus zeros. The **limit** of the density should be 1/2. For each
**tolerance** ε the model finds the last **excursion**, the last prefix whose density is more than
ε from 1/2.

**Problem 3** asks about **computational effort**. A **machine** runs an **algorithm** under a
**machine model**: a **Turing machine**, a cellular automaton counting cell updates, or a RAM,
each with its own **cost model** and **encoding** of n. The machine may not **store the answer**;
an algorithm that does not is **admissible**. For every n the model records the effort and the
**effort ratio** effort / n. Effort **O(n)** means the ratio's **limsup** is finite; direct
simulation is **O(n²)**, and anything **sublinear** in n² would already be a **partial result**.

Each of these properties is a **predicate**: a statement built from **quantifiers** (**for all**,
**exists**, **not exists**), each binding a **variable** over a **domain**. In the problems the
domains of t, p, T, n and m are **unbounded**, which is why no run decides them. Inside the model
each predicate has bounded **instances**: one period test, one center cell, one tolerance, one
algorithm. An instance **holds** or fails by computation over the model's own cells, and the
row that decides it is its **witness**. A predicate that holds on every instance is a **finite
verification**; only a **theorem** reaches past the horizon. Values computed outside the model
by an **accelerator** enter as **claims**, and the model decides whether each claim matches its
own cell. The three **prize problems** sit at the top: each is a predicate with unbounded
quantifiers whose bounded instances the model computes.
