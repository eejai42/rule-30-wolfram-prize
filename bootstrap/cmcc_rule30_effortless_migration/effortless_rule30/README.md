# Rule 30: native Effortless migration draft

Status: **NOT BUILT. Zero verified native Effortless loops.**

The earlier v05 project is a custom SQLite model. Its 13 research cycles must not be described as Effortless build cycles. This directory is a native-schema migration draft, not a successfully initialized Effortless project. `effortless.json` has deliberately not been fabricated: the official CLI failed before project initialization.

## Preserved model

Eight proposed tables: Assertions (26), Dependencies (18), Prerequisites (58), Assessments (26), Evidence (8), Revisions (5), Loops (13 legacy), Dashboards (1). These are JSON records, **not eight tables in an executed database**. The prior SQLite database still has six tables.

The 58 prerequisites include each claim itself and all transitive ancestors in the declared dependency graph. Lookup fields obtain the current premise flags from Assertions. SUMIFS rollups in Assessments count unusable premises and premises insufficient for a mathematical proof. The calculated status blocks conclusions with failed/open ancestors. Finite experimental evidence can be usable without being proof-eligible. Human-readable proof status is imported review metadata; these formulas do not check a mathematical proof.

ReportedStatus remains visible even when CurrentStatus is BLOCKED, retaining the difference between an open claim and a falsified one. All five original correction records remain visible. Editing an assertion's ReportedStatus is intended to flow through all existing ancestor paths after a successful build. Adding dependency edges requires regenerating and validating the transitive prerequisite rows. `migrate.py` is a one-time importer, not a runtime inference engine; rerunning it overwrites the draft from the archived v05 data.

Evidence files and their hashes are preserved. Evidence-to-claim support mappings were absent from the original ledger and are not invented here. The finite cell simulation remains in the companion v05 package and has not been converted into native Effortless cell formulas. Therefore this draft does **not** yet meet the requested full-picture workflow.

## Actual attempts and blockers

Official source: https://github.com/EffortlessAPI/cli (version 2026.1008.1747).
Official skills: https://github.com/EffortlessAPI/effortless-skills/tree/main/skills .

The older CLI skill names npm package `ssotme` and requires a separately installed .NET runtime. The current official CLI source instead names `@effortlessapi/cli` and ships a self-contained platform binary. Installed that official package locally; did not install a separate .NET SDK.

`effortless -version` and `effortless -init -projectName Rule30Research` both exited 137 with `Failed to create CoreCLR, HRESULT: 0x8007000E`. Lower heap limits, reduced processor count, disabling diagnostics, and disabling WriteXorExecute did not resolve the startup failure. No transpiler install, build, SQL generation, or database execution succeeded.

The documented remote MCP endpoint responded to health and tools/list. Its actual catalog exposed only ping/build/query/validate tools, not the documented isolated transpiler tools. Remote build takes a server-local path, so passing our inaccessible local path would not build this project.

## Completion requirements

1. Run the official CLI in an environment where its runtime starts; use `effortless -init` and install minimize-rulebook and rulebook-to-postgres via `effortless -install`, following the official skills.
2. Validate the draft using the official tooling and fix any compatibility issues it reports. Local structural checks do not establish transpiler compatibility.
3. Run `effortless build`, execute its generated PostgreSQL schema and query generated `vw_*` views. Do not substitute handcrafted SQL or Python-calculated output.
4. Run a baseline build and a controlled mutation build. Change T0 to FALSIFIED in a disposable fixture and verify that TB, TC, TD, K1 and their dependent assessments become blocked through the generated views. Restore the baseline and rebuild.
5. Add explicit evidence/check-to-claim links and apply revision events through the hub. Add a new dependency edge and verify closure completeness. Preserve all failed claims and superseded revisions.
6. Each research loop must consume the current generated assessment, revision, evidence and open-obligation views, then retain input hash, build receipt, query results and output hash. Only then record a VERIFIED EFFORTLESS loop. Merely incrementing a counter is insufficient.

No prize conjecture is proved by this migration. The mathematical conclusions and limitations remain those in the accompanying research_v05/REPORT.md.
