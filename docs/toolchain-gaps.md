# Toolchain gaps found while moving Rule 30 into the rulebook

Goal (project rule): everything is in the rulebook, and running the full rulebook gives the right
answer. Python is allowed only as an optimizer for large pieces, checked against the rulebook.
The Rule 30 lattice is SDLAF: rule number as Data, each cell a Formula over three Lookups to its
parents. Three toolchain behaviours block that today. Reproduce with
`research/toolchain-repro/make_lattice_rulebook.py`.

## 1. compile-rulebook silently skips the whole rulebook when a table refers to its own rows

A table whose lookups point at other rows of the same table (Cells.L -> parent Cells.Value) is
acyclic row by row but cyclic field by field. compile-rulebook returns without error and fills in
**no calculated, lookup or aggregation field in any table**: adding the lattice to this hub left
P1's status, the dashboard totals and every other ledger value empty. The CLI only prints
"Transpiler processing asynchronously" and the run looks successful.

**Watch out:** never add a self-referencing table to `effortless-rulebook/effortless-rulebook.json`
until this is fixed; the build will look green while the ledger stops computing.

Wanted: evaluate the row-level DAG (topological order over rows, memoised), or at least fail loudly.

## 2. rulebook-to-postgres evaluates it correctly, but in exponential time

The generated `calc_cells_value` calls `calc_cells_l/c/r`, which call `calc_cells_value` of the
parents, with no memoisation. The lattice matches Rule 30 exactly, but one center cell costs:

| depth | seconds |
|---|---|
| 8 | 0.06 |
| 10 | 0.14 |
| 12 | 1.09 |
| 14 | 5.23 |

About x2.2 per step; depth 30 is out of reach. Wanted: memoised evaluation for self-referencing
lookups (for example a recursive CTE, or layer-by-layer materialisation in topological order).

## 3. Closure works, but its view cannot be filtered by the target row

compile-rulebook supports `"type": "closure"` and `COUNTIFS(vw_<edge_table>_closure!{{FromId}}, {{Id}})`
(TK's ancestor count over Dependencies = 7, matching the Prerequisites rows). The ledger needs
"ancestors that are not usable", a condition on the closure's target row. The closure view
exposes only from/to/hop columns, so that count is not expressible, and `research/loop_tools.py`
still generates the Prerequisites rows in Python. Wanted: closure rows that can carry lookups of
the target (or a filtered closure on a target-row condition).
