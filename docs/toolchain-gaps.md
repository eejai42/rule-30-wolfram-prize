# Toolchain gaps found while moving Rule 30 into the rulebook

| Gap | Status |
|---|---|
| 1. compile-rulebook and self-referencing tables | **Fixed** in compile-rulebook v2026.10.23.1627 |
| 2. rulebook-to-postgres exponential self-lookups | **Fixed** in rulebook-to-postgres v2026.10.23.1648 |
| 3. closure view cannot be filtered by the target row | Open |
| 4. the CLI does not print a remote tool's failure | Open |
| 5. field names that are Python keywords or reserved (`R`, `Class`) fail compile-rulebook | Open (rename the field) |
| 6. a bare `COUNT(Table!{{CalculatedField}})` aggregation breaks the generated Postgres view | Open (use COUNTIFS) |
| 7. `{{A}} = {{B}}` between two fields inside a self-referencing chain fails in Postgres (text vs integer) | Open (write `{{A}}-{{B}}=0`) |
| 8. rulebook-to-postgres groups `a-b-c` as `a-(b-c)` | Open (parenthesize) |
| 9. compile-rulebook uses floats, Postgres NUMERIC: they disagree at exact boundaries | Open (compare in integers) |
| 10. a lookup through an empty reference: compile-rulebook evaluates the target formula on a blank row, Postgres returns NULL | Open (do not read such values) |
| 11. a row-level cycle in a self-referencing table (A points at B, B at A) leaves every chained field NULL in Postgres | Open (keep self-references one-directional) |
| 12. MAXIFS/MINIFS over an empty set: blank in compile-rulebook, 0 in Postgres | Open (guard with a COUNTIFS) |
| 13. minimize-rulebook runs out of memory on a ~16 MB rulebook; rulebook-to-xlsx fails in the editor at ~11 MB; rulebook-to-rulespeak runs out of memory in the editor at 14.6 MB | minimize-rulebook **fixed** in v2026.10.24.1121 (2 CPU / 4 GiB; 24 MB in 6 s); xlsx and rulespeak open |
| 14. rulebook-to-postgres drops every COUNTIFS criterion after the first pair when the COUNTIFS is an argument of IF (the `IF({{IsCached}}=1, cache, formula)` cache wrapper) | **Fixed** in rulebook-to-postgres v2026.10.25.1350 (11 regression tests; the transpiler-server runs a tool's tests before every deploy); `check_postgres.py --db … --fresh` checks it here |
| 15. any write to a memoised table empties its memos (`erb_memo_invalidate`), and a fresh compute without them is exponential along a self-referencing chain | Open (workaround in `research/ingest/ingest.py`: trigger held off, memos refreshed per sweep) |

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

## 6. Bare COUNT over another table's calculated field breaks the Postgres view

`Dashboards.PredicateCount = COUNT(Predicates!{{QuantifierCount}})` compiles correctly in
compile-rulebook (7), but rulebook-to-postgres emits
`SELECT COUNT(calc_predicates_quantifier_count(p_predicate_id))` inside
`calc_dashboards_predicate_count`, where `p_predicate_id` is not in scope, so `vw_dashboards`
fails to plan (`column "p_predicate_id" does not exist`, seen in the editor's `/api/view-health`).
The two substrates disagree on the same formula. Workaround: count with a COUNTIFS on a field
whose value is known, or leave the count out; the model no longer uses bare COUNT.

## 7. Field-to-field equality inside a self-referencing chain is mistyped in Postgres

rulebook-to-postgres computes a self-referencing table (Cells reads its parents' Value) in a
recursive `settled` jsonb CTE and inlines each chained formula there. An `IF` inlines as a
`CASE ... THEN (1)::text ... END`, and a comparison of two such fields is emitted as
`COALESCE(<text CASE>, 0) = COALESCE(<other>, 0)` without the `::NUMERIC` cast it uses when one
side is a literal. `Cells.RunStart = IF({{Value}}={{CenterValue}}, ...)` therefore made
`vw_cells` fail with `COALESCE types text and integer cannot be matched`, and every view built on
it (15 of 33) was missing. compile-rulebook computed the same formula correctly. Workaround:
write the equality as arithmetic, `IF({{Value}}-{{CenterValue}}=0, ...)`, which goes through the
generator's safe numeric path.

## 8. Chained subtraction is right-associative in Postgres

`PeriodTests.FinalAgreementLength = {{Depth}}-{{PeriodLength}}-{{LastMismatchTime}}` is
64 - 1 - 61 = 2 in compile-rulebook, but `calc_period_tests_final_agreement_length` computes
`depth - (period_length - last_mismatch_time)` = 124. Mixed `a-b+1` is grouped correctly.
Found by `research/hub/check_postgres.py`. Workaround: `{{Depth}}-({{PeriodLength}}+{{LastMismatchTime}})`.

## 9. Floats against NUMERIC at an exact boundary

compile-rulebook evaluates in Python floats; Postgres uses NUMERIC. At t = 19 the center prefix has
density exactly 11/20, so |density - 1/2| = 0.05 exactly: Postgres says it is not more than
epsilon = 0.05, compile-rulebook computes 0.050000000000000044 and says it is. Postgres is right.
Workaround: the model stores epsilon as an integer fraction and compares
`|ones - zeros| * denominator > 2 * numerator * N` in integers.

## 10. Lookups through an empty reference

For a row whose foreign key is empty, compile-rulebook gives a lookup the target formula evaluated
on an all-blank row (often 0), and Postgres gives NULL. Neither is a value of anything; the
model only reads such fields on rows where the reference is set. `check_postgres.py` skips them.

## 11. Row-level cycles in a self-referencing table

`RuleTableEntries.LeftPartner` first pointed both ways (n000 -> n100 and n100 -> n000). Postgres
settles a self-referencing table in a recursive CTE that starts from rows with no self-reference,
so with every row in a 2-cycle nothing settled and `OutputValue` (which does not even depend on the
partner) came back NULL on all 32 rows. compile-rulebook computed them. Workaround: partners point
one way only (white left cell -> black left cell), so the row graph is a DAG, as the conventions
require.

## 12. Empty MAXIFS / MINIFS

`PeriodicWords.MaxKillExcess = MAXIFS(TailCandidates!{{KillExcess}}, ..., IsKilled, 1)` has no
matching rows for the words 00, 11, 000, 111 (their tails are spelled 0 and 1). compile-rulebook
leaves it blank, Postgres returns 0. Workaround: aggregate into a raw field and read it through
`IF(<count> > 0, <aggregate>, <sentinel>)`.

## 13. Size limits

With the B9 tail lattices at 14 words x 12 onsets x margin 14 the rulebook reached 17.7 MB after
compile, and the remote minimize-rulebook failed with `System.OutOfMemoryException`. At 10 tails x
10 onsets x margin 12 it is 11.5 MB and builds, but the editor's rulebook-to-xlsx step fails (the
rest of the editor build succeeds). Generated lattices are the bulk; keep their keys short and their
instance sets to one candidate per distinct object.

Fix (minimize-rulebook v2026.10.24.1121): the workload ran with `cpu: 200m, memory: 512Mi`
(`tools/effortless/minimize-rulebook/cpln/workload.yaml` in Versioned-Stable-SSoTme-Tools), against
compile-rulebook's 2Gi. Now 2000m / 4Gi; a 24 MB rulebook minimizes in about 6 seconds. The
editor's rulebook-to-xlsx step still fails at this size (the rest of the editor build succeeds).

Since loop 26 (rulebook 14.6 MB) the editor's rulebook-to-rulespeak step also fails, with
`System.OutOfMemoryException` (from `GET localhost:42442/__boot/errors`). Postgres, the API and the
portal are unaffected; only the RuleSpeak docs are missing. Likely the same fix as minimize-rulebook:
raise the workload's memory in Versioned-Stable-SSoTme-Tools.

Since loop 27 (rulebook about 25 MB compiled) both editor steps are switched off rather than left
failing: `loop_tools.EDITOR_DISABLED_STEPS` sets `IsDisabled` on `rulebooktorulespeak` and
`rulebooktoxlsx` in the regenerated `effortless-rulebook/docker/effortless.editor.json` after every
build, and in the running editor through `POST /__boot/pipeline-toggle`. Turn them back on (remove
them from that list) once the two workloads get the memory minimize-rulebook got.


## 14. COUNTIFS inside IF loses its later criteria (rulebook-to-postgres)

Found 2026-10-24 while building the analysis database. `Predicates.QuantifierCount` is
`=IF({{IsCached}}=1,{{QuantifierCountCache}},COUNTIFS(Terms!{{PredicateKey}},{{PredicateId}},Terms!{{IsBinder}},1))`,
and the generated `calc_predicates_quantifier_count` is `SELECT COUNT(*) FROM terms WHERE predicate_key = …`:
the `IsBinder = 1` criterion is gone. A COUNTIFS that is not inside IF keeps every criterion
(`calc_assertions_on_current_path`). With the flags cleared, Postgres gives 19 for pr-p1-non-periodic where
compile-rulebook gives 3, and `PeriodTests.WindowFailureCount` counts every window (32) instead of the
failing ones (0). 540 computed values differ, in 15 fields, in the editor's database and the analysis database alike.

It has been invisible since the caches were introduced (commit 78e1a41): with `IsCached = 1` Postgres
returns the cache, which `loop_tools.build()` fills from compile-rulebook, so the plain
`check_postgres.py` compares compile-rulebook with a copy of itself on every cached field. It
matters as soon as Postgres computes a cached field itself, which is what the analysis database does
for bulk rows. `check_postgres.py --db <url> --fresh` clears the flags in a rolled-back transaction and
shows it.

Fix (rulebook-to-postgres v2026.10.25.1350, 2026-10-25): a nested COUNTIFS / SUMIFS / MINIFS /
MAXIFS / AVERAGEIFS is translated from its raw arguments, like a whole-formula one, and spliced back
into the surrounding expression. `NestedIfsTranslationTests` (11 cases) fail on the old translator.
The transpiler-server's deploy stream now runs every tool's .NET test projects before it creates a
version or builds, so a failing suite cannot be published. After the fix: `--fresh` 0 differences,
and `ingest.py load` passes its witness check.

## 15. Memo invalidation and the exponential fallback (rulebook-to-postgres)

Self-referencing lookups (Cells, TailCells, PeriodicityCandidates, ...) are memoised in
`erb_memo_*` tables, filled by `erb_refresh_memos()` in row-dependency order. A statement-level
trigger, `erb_memo_invalidate`, empties them on any INSERT, UPDATE or DELETE of the table, including
an UPDATE that only touches cache columns. Until the next refresh, `calc_*` falls back to
`__compute`, which re-derives all three parents recursively: `calc_cells_column_ones` over t <= 10 takes
22 s, growing about 3x per step. `ingest.py` holds the trigger off while it fills the caches and
refreshes the memos at the start of every sweep; the result is identical, since writing a cache
never changes a computed value once the caches are fresh.
