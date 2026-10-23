# Toolchain gaps found while moving Rule 30 into the rulebook

| Gap | Status |
|---|---|
| 1. compile-rulebook and self-referencing tables | **Fixed** in compile-rulebook v2026.10.23.1627 |
| 2. rulebook-to-postgres exponential self-lookups | **Fixed** in rulebook-to-postgres v2026.10.23.1648 |
| 3. closure view cannot be filtered by the target row | Open |
| 4. the CLI does not print a remote tool's failure | Open |
| 5. field names that are Python keywords or reserved (`R`, `Class`) fail compile-rulebook | Open (rename the field) |

Goal (project rule): everything is in the rulebook, and running the full rulebook gives the right
answer. Python is allowed only as an optimizer for large pieces, checked against the rulebook.
The Rule 30 lattice is SDLAF: rule number as Data, each cell a Formula over three Lookups to its
parents. Three toolchain behaviours block that today. Reproduce with
`research/toolchain-repro/make_lattice_rulebook.py`.

## 1. compile-rulebook and self-referencing tables (fixed)

The first diagnosis was wrong in its cause. The empty compile came from the field name `R`
(gap 5), and the CLI hid the error (gap 4). The real limit was the engine's settle loop: it
recomputes the whole dataset until nothing changes and gives up after a bound derived from the
field count (10 passes here), so a self-referencing chain deeper than ~8 rows failed with
"field dependencies are cyclic".

Fix (v2026.10.23.1627, `erb_runtime._compute_in_row_order`): a table whose lookups read its own
rows is computed row by row in dependency order inside each pass, so a whole chain settles in
one pass; a genuine row cycle still reports as before. The surgical patcher also became linear
(it rebuilt the file once per edit). Results: a depth-256 lattice (66,050 cells) compiles in
5.9 s, exact against Rule 30; all 12 example rulebooks that compiled before produce
byte-identical output.

## 2. rulebook-to-postgres evaluates it correctly, but in exponential time

The generated `calc_cells_value` calls `calc_cells_l/c/r`, which call `calc_cells_value` of the
parents, with no memoisation. The lattice matches Rule 30 exactly, but one center cell costs:

| depth | seconds |
|---|---|
| 8 | 0.06 |
| 10 | 0.14 |
| 12 | 1.09 |
| 14 | 5.23 |

About x2.2 per step; depth 30 was out of reach.

Fix (v2026.10.23.1648, `ApplySelfLookupMemo`): for each computed field a self-referencing lookup
returns, the generated function becomes `<name>__compute`, an UNLOGGED memo table and a wrapper
with the original name are added, a statement-level trigger empties the memo on any write
(never stale), and `06-refresh-memos.sql` refills it in row-dependency order after the seed
data. Rulebooks without a self-referencing lookup generate byte-identical SQL (15 of 17
examples plus this hub). traffic-ticket-contest has one (Jurisdictions -> parent) and all 53 of
its views return identical contents. A depth-128 lattice loads in 1.1 s, refreshes in 2.8 s and
reads all 16,641 cells in 1.2 s.

## 3. Closure works, but its view cannot be filtered by the target row

compile-rulebook supports `"type": "closure"` and `COUNTIFS(vw_<edge_table>_closure!{{FromId}}, {{Id}})`
(TK's ancestor count over Dependencies = 7, matching the Prerequisites rows). The ledger needs
"ancestors that are not usable", a condition on the closure's target row. The closure view
exposes only from/to/hop columns, so that count is not expressible, and `research/loop_tools.py`
still generates the Prerequisites rows in Python. Wanted: closure rows that can carry lookups of
the target (or a filtered closure on a target-row condition). The runtime already supports an
edge filter (a boolean field on the edge table); whether that is enough is untested.

## 4. The CLI does not print a remote tool's failure

compile-rulebook's hub throws with the script's stdout/stderr, but a normal `effortless
compile-rulebook` run printed nothing and wrote nothing; only `-debug` showed "Remote server did
not return expected output files". A failed build looks like a no-op.

## 5. Reserved field names

A field named `R` (Python parameter `r`) or `Class` (`class`) makes compile-rulebook's Python
generator refuse the rulebook. Rename the field (here: `LeftValue`, `CenterValue`, `RightValue`).
