# Loop 27: the challenge's own shape

**Serves:** P1, P2, P3 directly. This loop changes what the ledger is measured against: from our own
claims to the official challenge.

## Why

The Rule 30 Prize now has an AI track ([skill.md](https://www.wolframcloud.com/obj/rule-30-prize/Agents/skill.md),
v1.17.2), and it is graded in Lean. A submission is one Lean module whose headline theorem has the
official type (`Ruliology.CellularAutomata.Rule30Prize.Problem1`, ...) and uses only standard
axioms, checked by the kit's `Check.lean` at the commit the verifier names. Around it there is a
large body of work this ledger did not know about:

- **The kit** ([WolframInstitute/Rule30PrizeKit](https://github.com/WolframInstitute/Rule30PrizeKit)):
  the official statements, a catalog of proved partial results (`lean/`, namespace
  `Ruliology.CellularAutomata`) and 160+ equivalent forms of Problem 1 (`equivalents/`).
- **The verifier's environment** (`api/environment`): the kit commit, Lean and Mathlib versions it
  checks against, and the modules a submission may import there.
- **The public submissions list** (`submissions.json`): every submission's abstract, headline
  theorems, verifier status and reviewer tags (Human Verified, Kit Contribution, Prize Claimed).

Our diagonal results (T004, TB, TK, TL, TM, TN) are already Lean theorems in the kit. Our ledger
counts them as "proved" in English. Measured against the challenge, that is the wrong yardstick.

## Hypothesis

H42: the whole public record of the challenge fits in this one model, and the model can then
decide, for each of our claims, whether Lean proves it: every kit module and submission becomes
rows the build reads; every one of our claims whose formal statement uses only operators with a Lean
meaning gets a Lean statement written by the build from its term tree; and a claim is
LEAN_VERIFIED exactly when the kernel accepts a proof of that statement with standard axioms only.
Nothing of the kit's contradicts a claim we hold proved.

## What gets built

### 1. Sources, synced from the live challenge (`research/sources/sync.py`)

| Source | Where | What is kept |
|---|---|---|
| `kit` | the kit's git repository | the commit synced (latest `main`), every module's hash |
| `verifier` | `api/environment` | the kit commit the verifier checks against, Lean/Mathlib versions, the modules it allows |
| `submissions` | `submissions.json` | every submission, its headlines, status, tags, kit modules |
| `skill` | `skill.md` | the official agent instructions (version) |

Each sync writes dated snapshots under `research/sources/snapshots/` (pinned by sha256 as Evidence),
runs the Lean exporter over the kit, and loads everything into the rulebook. `./start.sh sync` runs
it; the admin portal shows every table it fills.

### 2. The kit's Lean environment as data (`lean/ExportKit.lean`)

A Lean metaprogram run in the kit's environment. For every kit module: its imports and docstring.
For every named declaration: kind, statement as Lean prints it, docstring, line, the named kit
declarations it uses, and the non-standard axioms it depends on (followed through Mathlib). This is
the authoritative record: it comes from the compiled environment, not from reading files.

### 3. New tables (`research/hub/build_challenge.py`, rerunnable)

| Table | Holds |
|---|---|
| `ChallengeSources`, `SourceSyncs` | the four sources and every sync of them |
| `LeanModules`, `LeanImports` | the kit's modules and their imports |
| `LeanDeclarations`, `LeanUses` | every named declaration and what it uses |
| `Submissions`, `SubmissionTags`, `SubmissionHeadlines`, `SubmissionModules` | the public submissions |
| `ClaimLinks` | our claims mapped to kit declarations (same, stronger, weaker, related) |
| `LeanProofs` | a Lean proof of a claim's Lean statement (often one line citing the kit) |
| `LeanChecks` | what the kernel said about each claim's Lean statement, and the statement it checked |

### 4. The kit's results become claims in the ledger

- Every catalog and equivalents module is an Assertion (`L-<Module>`, Kind `Lean result`), its
  statement the module's title. Its dependencies are its imports. Its status is computed from the
  export: LEAN_VERIFIED when no declaration of the module uses a non-standard axiom.
- The kit's case split of Problem 1 (period 1; small periods; any period; period 2; least periods 3
  and 4; longer) becomes claims `KC1`..`KC7`, with the kit's open statements (Q01 and the absorption
  statements) as OPEN claims under them. A new route node `B10` ("P1 by the least period, the kit's
  split") collects them. The ledger's own route (B1 -> B9 -> ...) stays as a second route.
- P1 and P2 are linked to the official Lean constants.

### 5. Lean statements written by the build, checked by the kernel

- `Operators.LeanSymbol` and `Variables.LeanType` give the model's vocabulary a Lean meaning, over a
  small prelude that defines `c`, `x`, `y`, `w` from the kit's `cell`, `R`, `D`.
- `Terms.LeanRendered` writes each term tree in Lean, the way `Terms.Rendered` writes it in Wolfram
  Language. `Assertions.LeanStatement` is the root's rendering; a claim using an operator with no Lean
  meaning has none yet (`IsLeanExpressible` = 0), as an unmodeled operator makes a claim uncomputable.
- `research/lean/ledger.py` (run inside every build when the toolchain is present) writes
  `lean/Rule30Ledger.lean` from the compiled rulebook: one theorem per expressible claim, with its
  `LeanProofs` proof or `sorry`; compiles it against the kit; runs the kit's own `Check.lean` on every
  theorem; and loads the verdicts into `LeanChecks`.
- `EffectiveStatus` gains LEAN_VERIFIED (usable, proof-eligible): the claim's current Lean statement
  passed the check. A check of an older statement does not count. A claim the model refutes and Lean
  verifies is a conflict (`Dashboards.LeanModelConflictCount`, must be 0); a kit module reported
  proved whose export shows a non-standard axiom is a contradiction too.
- For P1 and P2 the file also states that our formal statement is equivalent to the official one.

### 6. The explorer and the docs

- `/challenge`: the official problems with their Lean statements, the sources and when they were
  synced, the kit's case split, the catalog, the submissions. The landing page leads with it.
- Claim pages show the Lean statement, the check, and the kit declarations linked to the claim.
- `CLAUDE.md`, `docs/p1-frontier.md`, `docs/app.md` and the plan (`research/strategy.py`) move to the
  challenge's shape.

## Decided by

The kernel (LeanChecks) and the export (axioms per declaration), read through the build's formulas.
No script types a status.

## Not in this loop

- The Wolfram Language computational essay and the submission itself (`Rule30Submission.lean`, the
  API call): a later loop, once a claim of ours is LEAN_VERIFIED and is new against the catalog and
  the submissions list.
- Lean proofs for every expressible claim: this loop proves what the kit gives in a few lines, and
  leaves the rest as Lean statements with `sorry`, visible as open Lean obligations.
