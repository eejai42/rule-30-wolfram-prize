# Rule 30 Explorer

A phone-first web app over the rulebook editor's generated API. It shows where the
Rule 30 research stands, what each loop did, and why every claim has the status it has.
Every status, count and flag on screen is a rulebook field read from a `vw_*` view.
The app computes none of them.

## Persona

| key | Name | Who they are |
|---|---|---|
| `researcher` | Researcher | Runs Rule 30 loops and reviews the proofs. Opens the explorer to see where the prize problems stand, watch a loop while it runs, and trace any claim back to its premises and evidence. |

One persona, so the app has no persona picker. A second persona (for example an outside
reviewer who only reads proofs) would add one.

## Stories

1. As a researcher I see how many claims are proved, checked, falsified and open, so I know where the work stands. *(Dashboards.ProvedCount, CheckedCount, FalsifiedCount, OpenCount)*
2. As a researcher I see each prize problem and the open obligations it waits on, so I know what to attack next. *(Assessments.CurrentStatus, AncestorBlockedCount; Prerequisites.IsBlockingAncestor)*
3. As a researcher I see a loop the moment it starts and the moment it verifies, so I can monitor it without a terminal. *(Loops.State, Dashboards.RunningLoopCount)*
4. As a researcher I see what each loop changed: claims added, proofs, falsifications, and its build receipt and hashes, so the history is auditable. *(Loops.ClaimsAdded, ProofsMade, FalsificationsMade, RevisionsMade)*
5. As a researcher I am warned when an established claim rests on something not established, or a finite check has no evidence. *(Dashboards.AtRiskCount, EvidenceGapCount; Assessments.IsAtRisk)*
6. As a researcher I filter and search every claim by kind and status. *(Assessments.Kind, StatusGroup)*
7. As a researcher I open one claim and see its statement, proof, premises, dependents, evidence files, revision history, and which ancestors block it. *(Assertions.PremiseCount, DependentCount, EvidenceCount; EvidenceLinks.EvidencePath)*
8. As a researcher I explore the dependency graph and click into any claim. *(Dependencies, Assessments.StatusGroup)*
9. As a researcher I read proof and evidence files in the app. *(Assertions.ProofSection, Evidence.Path)*
10. As a researcher I hover any derived value to see the rule that produced it. *(explainer DAG on every derived value)*
11. As a researcher I open the app and see, first, the most promising path from where the research stands to P1: the route of claims, which are established, which are open and which block the goal, and what has been ruled out. *(Strategies.Headline, EstablishedStepCount, OpenStepCount, BlockingStepCount, RuledOutCount; StrategySteps.Role, StatusGroup, BlocksGoal)*
12. As a researcher I see where the next loop is aiming and why, with an honest estimate. *(Strategies.NextTarget, NextHypothesis, Approach, Missing, Estimate)*
13. As a researcher I open any claim and see what the model says about it: its formal statement, its quantifiers, whether the model can decide it, its bounded instances and their verdicts, and whether the ledger's status comes from the build or from a report. *(Predicates.Formal, FiniteVerdict, IsComputable, IsFinitelyDecidable, InstanceCount, FailingCount; PredicateInstances.Holds, Witness; Assertions.EffectiveStatus, IsModelDecided)*
14. As a researcher I see in the dependency graph which claims are on the current path, and double-click any claim to open its page. *(Assertions.OnCurrentPath)*

## Routes

| Path | Shows | Stories |
|---|---|---|
| `/` | The path to P1 (route, blockers, ruled out, next loop's aim), then status tiles, prize problems, alarms, running and recent loops | 1, 2, 3, 5, 11, 12 |
| `/loops` | Every loop, newest first, legacy and native | 3, 4 |
| `/loops/:id` | One loop: hypothesis, summary, counts, claims added, revisions, receipt and hashes | 4 |
| `/claims` | Every claim, filter by kind and status, search | 6 |
| `/claims/:id` | One claim: statement, statuses, proof, its place on the current path, what the model says (formal statement, instances, verdict), premises, dependents, blockers, evidence, revisions | 7, 9, 13 |
| `/graph` | The dependency graph, coloured by status, current path outlined; tap to focus, double-click to open the claim | 8, 14 |
| `/files?path=` | A proof or evidence file, rendered (Markdown) or shown (JSON, text) | 9 |
| `/dag`, `/dag/:table/:field` | The explainer's field pages | 10 |

`/` is the page the researcher opens every morning.

## How it is wired

- `explorer/` is a Vite + React + TypeScript app on port 7431.
- `/api/*` is proxied to the rulebook editor API on port 42441 (`effortless-rulebook/ports.env`).
- `/repo-files/*` serves repo files read-only, limited to `research/`, `bootstrap/` and `docs/`.
- The explainer assets are generated into `explorer/public/rulebook-explainer-dag/` by `rulebook-to-explainer-dag` on every `effortless build`.
- The app polls the API every 5 seconds. While the editor container rebuilds after a rulebook change, the header shows "Syncing" and the last good data stays on screen.
