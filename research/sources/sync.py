"""Sync the live Rule 30 Prize challenge into the model.

  python3 research/sources/sync.py                    fetch, export, re-verify, load, build
  python3 research/sources/sync.py --commit <sha>     pin the kit to a commit (default: the latest main)
  python3 research/sources/sync.py --commit verifier  pin the kit to the commit the verifier checks against
  python3 research/sources/sync.py --no-build         stop after the snapshots and the load (no effortless build)
  python3 research/sources/sync.py --offline          reuse the snapshots on disk; only reload and build

What it does, in order:
  1. The verifier's environment (api/environment), the public submissions list (submissions.json) and the
     agent instructions (skill.md), saved as served under research/sources/snapshots/.
  2. The kit: clone or fetch external/Rule30PrizeKit, check out the commit, and build it with the kit's
     build_all.sh when the commit changed. kit.json records the commit and every .lean file's sha256;
     the kit's lean/README.md is copied (its tables of cases and contributions are read from it).
  3. lean/ExportKit.lean over the kit: every module and named declaration -> kit-export.json.gz.
  4. Every submission's Lean source -> snapshots/submissions/<id>.lean. Each is compiled against the kit as
     module Rule30Submission, checked by the kit's Check.lean on its own headlines (our re-verification),
     and exported -> submission-checks.json.
  5. One record per source appended to syncs.json (the history of what was synced when).
  6. research/hub/build_challenge.py loads it all into the rulebook; research/build.py builds.

The snapshots are evidence: build_challenge.py pins each by sha256. No status is decided here.
"""
from __future__ import annotations
import gzip, hashlib, json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'research' / 'lean'))
sys.path.insert(0, str(ROOT / 'research' / 'hub'))
import leankit as lk

SNAP = HERE / 'snapshots'
AGENTS = 'https://www.wolframcloud.com/obj/rule-30-prize/Agents'
URLS = {'environment': f'{AGENTS}/api/environment', 'submissions': f'{AGENTS}/submissions.json', 'skill': f'{AGENTS}/skill.md'}
FILES = {'environment': 'environment.json', 'submissions': 'submissions.json', 'skill': 'skill.md'}


def now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(url: str) -> bytes:
    """curl, not urllib: curl uses the system's certificate store (python.org builds often have none)."""
    return subprocess.run(['curl', '-sSfL', '--max-time', '120', '-A', 'rule30-research-sync', url], check=True, capture_output=True).stdout


def git(*args, cwd=lk.KIT) -> str:
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def sync_web(records: list) -> None:
    for name, url in URLS.items():
        body = fetch(url)
        (SNAP / FILES[name]).write_bytes(body)
        version = ''
        if name == 'environment':
            version = json.loads(body)['kit']['commit']
        elif name == 'submissions':
            d = json.loads(body)
            version = f"{d['updated']} ({len(d['entries'])} entries)"
        elif name == 'skill':
            version = next((ln.split(':', 1)[1].strip() for ln in body.decode().splitlines() if ln.startswith('version:')), '')
        records.append({'source': name, 'url': url, 'retrievedAt': now(), 'version': version, 'sha256': sha(body),
                        'snapshot': f'research/sources/snapshots/{FILES[name]}'})
        print(f'{name}: {version}')


def sync_kit(commit_arg: str, records: list) -> str:
    if not (lk.KIT / '.git').exists():
        lk.KIT.parent.mkdir(parents=True, exist_ok=True)
        git('clone', '-q', lk.KIT_URL, str(lk.KIT), cwd=ROOT)
    git('fetch', '-q', 'origin')
    if commit_arg == 'verifier':
        commit_arg = json.loads((SNAP / 'environment.json').read_text())['kit']['commit']
    target = git('rev-parse', commit_arg or 'origin/main')
    before = git('rev-parse', 'HEAD')
    built_marker = lk.KIT / '.lake' / 'rule30-built-commit'
    if target != before:
        git('checkout', '-q', target)
    if not built_marker.exists() or built_marker.read_text().strip() != target:
        print(f'building the kit at {target[:12]} (build_all.sh; this takes a while) ...')
        ok, tail = lk.build_kit(ROOT / '.logs' / 'kit-build.log')
        print(tail)
        if not ok:
            raise SystemExit('the kit did not build; see .logs/kit-build.log')
        built_marker.write_text(target + '\n')
    files = {}
    for p in sorted(lk.KIT.rglob('*.lean')):
        rel = p.relative_to(lk.KIT).as_posix()
        if rel.startswith('.lake/'):
            continue
        b = p.read_bytes()
        files[rel] = {'sha256': sha(b), 'lines': b.count(b'\n')}
    meta = {'repository': lk.KIT_URL.removesuffix('.git'), 'commit': target, 'date': git('show', '-s', '--format=%cI', target),
            'subject': git('show', '-s', '--format=%s', target), 'files': files}
    (SNAP / 'kit.json').write_text(json.dumps(meta, indent=1, sort_keys=True) + '\n')
    (SNAP / 'kit-lean-README.md').write_bytes((lk.KIT / 'lean' / 'README.md').read_bytes())
    records.append({'source': 'kit', 'url': meta['repository'], 'retrievedAt': now(), 'version': target,
                    'sha256': sha((SNAP / 'kit.json').read_bytes()), 'snapshot': 'research/sources/snapshots/kit.json'})
    print(f'kit: {target[:12]} {meta["subject"]}')
    return target


def export_kit(records: list) -> None:
    raw = lk.OUT / 'kit-export.json'
    raw.parent.mkdir(parents=True, exist_ok=True)
    print(lk.export(raw))
    data = json.loads(raw.read_text())
    # Deterministic bytes (sorted keys, declarations by name) so the same kit gives the same snapshot hash.
    data['declarations'].sort(key=lambda d: d['name'])
    data['modules'].sort(key=lambda m: m['name'])
    body = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    (SNAP / 'kit-export.json.gz').write_bytes(gzip.compress(body, mtime=0))
    records.append({'source': 'kit-export', 'url': 'lean/ExportKit.lean', 'retrievedAt': now(),
                    'version': f"{len(data['modules'])} modules, {len(data['declarations'])} declarations", 'sha256': sha(body),
                    'snapshot': 'research/sources/snapshots/kit-export.json.gz'})


def verify_one(e: dict, sdir: Path) -> dict:
    """One submission: its Lean source compiled against the kit as Rule30Submission, checked, exported.
    The result is cached next to the build (keyed by the source's hash and the kit commit)."""
    url = (e.get('files') or {}).get('lean')
    if not url:
        return {'source': None, 'compiled': False, 'note': 'no Lean source in the submission'}
    src = sdir / f"{e['id']}.lean"
    if not src.exists():
        src.write_bytes(fetch(url))
    work = lk.OUT / 'submissions' / e['id']
    work.mkdir(parents=True, exist_ok=True)
    key = sha(src.read_bytes() + (lk.KIT / '.lake' / 'rule30-built-commit').read_bytes())
    cache = work / 'result.json'
    if cache.exists():
        cached = json.loads(cache.read_text())
        if cached.get('key') == key:
            return cached['result']
    ok, msgs = lk.compile_module(src, 'Rule30Submission', work)
    rec = {'source': f'research/sources/snapshots/submissions/{src.name}', 'sha256': sha(src.read_bytes()), 'compiled': ok}
    if not ok:
        rec['messages'] = msgs[-3000:]
    else:
        claim = {'proof': f"problem{e.get('problem', 1)}", 'disproof': f"not_problem{e.get('problem', 1)}"}.get(e.get('claim'), 'partial')
        rec['check'] = lk.check('Rule30Submission', e.get('headlines') or [], work, claim)
        ex = work / 'export.json'
        try:
            lk.export(ex, ['Rule30Submission'], ['Rule30Submission'], extra=work)
            rec['declarations'] = json.loads(ex.read_text())['declarations']
        except RuntimeError as err:
            rec['exportError'] = str(err)[-1000:]
    cache.write_text(json.dumps({'key': key, 'result': rec}))
    return rec


def verify_submissions(records: list, workers: int = 4) -> None:
    """Download each submission's Lean source; compile, check and export it against our kit checkout."""
    from concurrent.futures import ThreadPoolExecutor
    subs = json.loads((SNAP / 'submissions.json').read_text())['entries']
    sdir = SNAP / 'submissions'
    sdir.mkdir(exist_ok=True)
    out = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:   # each Lean process needs a few GB
        for e, rec in zip(subs, pool.map(lambda e: verify_one(e, sdir), subs)):
            out[e['id']] = rec
            print(f"{e['id']}: compiled={rec.get('compiled')} verdict={rec.get('check', {}).get('verdict')}", flush=True)
    body = json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False).encode()
    (SNAP / 'submission-checks.json').write_bytes(body)
    records.append({'source': 'submission-checks', 'url': 'research/lean/leankit.py', 'retrievedAt': now(),
                    'version': f"{sum(1 for r in out.values() if r.get('check', {}).get('verdict') == 'pass')} of {len(out)} pass here",
                    'sha256': sha(body), 'snapshot': 'research/sources/snapshots/submission-checks.json'})


def main(argv: list[str]) -> None:
    SNAP.mkdir(parents=True, exist_ok=True)
    commit = argv[argv.index('--commit') + 1] if '--commit' in argv else ''
    records: list = []
    if '--offline' not in argv:
        sync_web(records)
        sync_kit(commit, records)
        export_kit(records)
        verify_submissions(records)
        log = SNAP / 'syncs.json'
        history = json.loads(log.read_text()) if log.exists() else []
        history += records
        log.write_text(json.dumps(history, indent=1) + '\n')
    import build_challenge
    build_challenge.main()
    if '--no-build' not in argv:
        import loop_tools as lt
        print(json.dumps(lt.build(), indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
