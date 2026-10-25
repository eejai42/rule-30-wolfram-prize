"""Loop 27: the challenge's own shape. See PLAN.md.

H42 (serves P1, P2, P3): the public record of the Rule 30 Prize fits in this one model, and the model can
then decide, for each of our claims, whether Lean proves it. Run research/sources/sync.py first (the
snapshots are this loop's inputs); this loop loads them, rebuilds the domain model with its Lean
vocabulary, and lets the build decide: the export decides the kit's claims, the kernel decides ours.

Nothing here computes a value or a verdict. The edit reruns build_model.py (which loads the challenge
through build_challenge.apply), tags the claims this loop brought in, and moves the planned
reachable-row automaton loop to effortless-28. The build writes lean/Rule30Ledger.lean, the kit's
Check.lean decides it, and EffectiveStatus reads LeanChecks.
"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOOP = 'effortless-27'
HYPOTHESIS = ("H42: the public record of the Rule 30 Prize (the kit's Lean statements, catalog and equivalent forms, "
              "the verifier's environment and every public submission) fits in this one model, and the model then decides, "
              "for each of our claims, whether Lean proves it: the build writes each expressible claim in Lean from its term tree "
              "and a claim is LEAN_VERIFIED exactly when the kit's Check.lean accepts a proof of that statement. Nothing in the kit "
              "contradicts a claim we hold proved.")
CONSUME = ['P1', 'P2', 'P3', 'K1', 'T0', 'TX', 'D0', 'TS', 'T004', 'B10', 'B11', 'KC1', 'KC4', 'Q-Q01']


def replan(book):
    """The automaton loop planned as effortless-27 moves to effortless-28: this loop takes the number."""
    if lt.has(book, 'Loops', LOOP) and lt.row(book, 'Loops', LOOP)['State'] == 'PLANNED':
        r = lt.row(book, 'Loops', LOOP)
        r['LoopId'] = 'effortless-28'
        for t in lt.rows(book, 'LoopTargets'):
            if t['Loop'] == LOOP:
                t['Loop'], t['LoopTargetId'] = 'effortless-28', t['LoopTargetId'].replace(LOOP, 'effortless-28')
        for s in lt.rows(book, 'Strategies'):
            if s.get('NextLoop') == LOOP:
                s['NextLoop'] = 'effortless-28'


def edit(book):
    if lt.has(book, 'Loops', 'effortless-28'):   # keep the order: this loop, then the one it moved
        mine, planned = lt.row(book, 'Loops', LOOP), lt.row(book, 'Loops', 'effortless-28')
        mine['Sequence'], planned['Sequence'] = min(mine['Sequence'], planned['Sequence']), max(mine['Sequence'], planned['Sequence'])
    before = {a['AssertionId'] for a in lt.rows(book, 'Assertions')}
    lt.save(book)
    proc = subprocess.run([sys.executable, str(ROOT / 'research' / 'hub' / 'build_model.py')], cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-3000:]
    book.clear()
    book.update(lt.load())
    added = [a for a in lt.rows(book, 'Assertions') if a['AssertionId'] not in before]
    for a in added:
        a['IntroducedInLoop'] = LOOP
    kinds = {}
    for a in added:
        kinds[a['Kind']] = kinds.get(a['Kind'], 0) + 1
    stats = proc.stdout.strip().splitlines()
    return (f"Loaded the challenge (research/sources/snapshots): {', '.join(f'{n} {k}' for k, n in sorted(kinds.items()))} claims added; "
            f"P1's term tree corrected (its inner binder said 'no onset', which made it the shape of the negation; Lean's alignment with Problem1 now decides it). "
            f"Load: {next((s for s in stats if s.startswith('{') and 'modules' in s), '')}.")


def summarize(book):
    d = lt.rows(book, 'Dashboards')[0]
    a = {r['AssertionId']: r for r in lt.rows(book, 'Assertions')}
    own_lean = sorted(k for k, r in a.items() if r.get('IsOwnClaim') == 1 and r.get('EffectiveStatus') == 'LEAN_VERIFIED')
    known = sorted(k for k, r in a.items() if r.get('IsOwnClaim') == 1 and r.get('IsKnownInKit') == 1)
    return (f"Decided by the build: {d['KitClaimCount']} kit claims, {d['LeanVerifiedCount']} LEAN_VERIFIED in all; our claims LEAN_VERIFIED: {', '.join(own_lean)}. "
            f"P1 aligned with the official Problem1 in Lean: {a['P1'].get('IsOfficiallyAligned')}. Known in the kit: {len(known)} of our claims ({', '.join(known)}). "
            f"Our claims the build writes in Lean: {d['OwnLeanExpressibleCount']}. Submissions: {d['SubmissionCount']} ({d['SubmissionLeanVerifiedCount']} Lean Verified; "
            f"{d['SubmissionDisagreementCount']} where our check against the synced kit disagrees with the verifier). "
            f"Must-be-zero counts: KitContradiction {d['KitContradictionCount']}, LeanContradiction {d['LeanContradictionCount']}, "
            f"LeanUnconfirmed {d['LeanUnconfirmedCount']}, KitUnverifiedModule {d['KitUnverifiedModuleCount']}, ModelContradiction {d['ModelContradictionCount']}.")


if __name__ == '__main__':
    book = lt.load()
    replan(book)
    lt.save(book)
    consumed = lt.run_loop(LOOP, HYPOTHESIS, edit, CONSUME, HERE, summarize=summarize)
    print(json.dumps({k: v for k, v in consumed.items() if not k.startswith('_')}, indent=1))
