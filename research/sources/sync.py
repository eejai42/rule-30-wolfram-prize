"""Sync the live Rule 30 Prize challenge into the model.

  python3 research/sources/sync.py                    fetch, export, re-verify, load, build
  python3 research/sources/sync.py --commit <sha>     pin the kit to a commit (default: the latest main)
  python3 research/sources/sync.py --commit verifier  pin the kit to the commit the verifier checks against
  python3 research/sources/sync.py --no-build         stop after the load (no effortless build)
  python3 research/sources/sync.py --from-raw         no network: rebuild the snapshots from external/sources/ and the
                                                      cached checks, then load and build

What is kept here follows each source's license (research/sources/licenses.py). The kit, the submissions and
the agent instructions state no license, so their works (Lean sources, statements, docstrings, abstracts, the
instructions' text) are never written into the repo: they go to external/sources/ and external/Rule30PrizeKit
(both gitignored), and the snapshots under research/sources/snapshots/ keep only references and results:
names, links, versions, hashes, and what the checks said. A work whose license allows redistribution is kept in
full, with its credit and license (research/sources/included/).

In order:
  1. The verifier's environment (facts: commits, versions, module names), the submissions list and skill.md
     are fetched into external/sources/. Snapshots: environment.json as served; submissions.json reduced to
     each submission's references and statuses; skill.json (version and hash only).
  2. The kit: clone or fetch external/Rule30PrizeKit, check out the commit, build it with the kit's build_all.sh
     when the commit changed. kit.json: the commit and every .lean file's sha256. kit-facts.json: the facts of
     its README tables (the cases of Problem 1 and their modules, when each module was added and who proved it,
     the headline theorem names).
  3. lean/ExportKit.lean over the kit -> external/sources/kit-export.json (everything); the snapshot
     kit-export.json.gz keeps names, kinds, lines, imports, uses and non-standard axioms.
  4. Every submission's Lean source -> external/sources/submissions/. Each is compiled against the kit, checked
     by the kit's Check.lean on its own headlines (our re-verification) and exported; submission-checks.json
     keeps the verdicts, the headline theorems' axioms and the names of their declarations.
  5. One record per source appended to syncs.json. 6. build_challenge.py loads it; research/build.py builds.
"""
from __future__ import annotations
import gzip, hashlib, json, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'research' / 'lean'))
sys.path.insert(0, str(ROOT / 'research' / 'hub'))
sys.path.insert(0, str(HERE))
import leankit as lk
import licenses

SNAP = HERE / 'snapshots'
RAW = ROOT / 'external' / 'sources'        # downloaded works, never committed
INCLUDED = HERE / 'included'               # works whose license allows them here, with credit
AGENTS = 'https://www.wolframcloud.com/obj/rule-30-prize/Agents'
URLS = {'environment': f'{AGENTS}/api/environment', 'submissions': f'{AGENTS}/submissions.json', 'skill': f'{AGENTS}/skill.md'}
RAW_FILES = {'environment': 'environment.json', 'submissions': 'submissions.json', 'skill': 'skill.md'}
LICENSE_OF = {s[0]: s[4] for s in licenses.SOURCES}
NS = 'Ruliology.CellularAutomata.'


def now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(url: str) -> bytes:
    """curl, not urllib: curl uses the system's certificate store (python.org builds often have none)."""
    return subprocess.run(['curl', '-sSfL', '--max-time', '120', '-A', 'rule30-research-sync', url], check=True, capture_output=True).stdout


def git(*args, cwd=lk.KIT) -> str:
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def write_json(path: Path, data, gz=False) -> bytes:
    body = json.dumps(data, indent=None if gz else 1, sort_keys=True, ensure_ascii=False).encode()
    path.write_bytes(gzip.compress(body, mtime=0) if gz else body + b'\n')
    return body


# ---------- the web sources ----------
SUBMISSION_FACTS = ('id', 'title', 'problem', 'claim', 'authors', 'agent', 'status', 'tags', 'statusRank', 'submitted', 'supersedes',
                    'page', 'target', 'headlines')


def submission_facts(d: dict) -> dict:
    """The submissions list without the works themselves (abstracts, verifier messages): references and statuses."""
    out = []
    for e in d['entries']:
        f = {k: e.get(k) for k in SUBMISSION_FACTS}
        f['files'] = {k: v for k, v in (e.get('files') or {}).items()}          # links to the notebook and the Lean source
        kc = e.get('kitContribution') or {}
        f['kitContribution'] = {'modules': kc.get('modules', []), 'commit': kc.get('commit')} if kc else None
        ck = e.get('check') or {}
        f['check'] = {'state': ck.get('state'), 'verdict': ck.get('verdict'), 'kitCommit': ck.get('kitCommit'), 'checkedAt': ck.get('checkedAt'),
                      'headlines': [{'name': h.get('name'), 'ok': h.get('ok'), 'axioms': h.get('axioms', [])} for h in ck.get('headlines', [])]} if ck else None
        out.append(f)
    return {'updated': d['updated'], 'kit': d.get('kit'), 'statuses': d.get('statuses'), 'tags': d.get('tags'), 'license': LICENSE_OF['submissions'],
            'source': URLS['submissions'], 'entries': out}


def reduce_web(records: list) -> None:
    env = (RAW / 'environment.json').read_bytes()
    (SNAP / 'environment.json').write_bytes(env)          # facts only: commits, versions, module names
    subs = json.loads((RAW / 'submissions.json').read_text())
    body = write_json(SNAP / 'submissions.json', submission_facts(subs))
    skill = (RAW / 'skill.md').read_bytes()
    version = next((ln.split(':', 1)[1].strip() for ln in skill.decode().splitlines() if ln.startswith('version:')), '')
    write_json(SNAP / 'skill.json', {'url': URLS['skill'], 'version': version, 'sha256': sha(skill), 'license': LICENSE_OF['skill'],
                                     'note': 'Not copied here (no license stated); read it at the url.'})
    records += [
        {'source': 'environment', 'url': URLS['environment'], 'retrievedAt': now(), 'version': json.loads(env)['kit']['commit'], 'sha256': sha(env),
         'snapshot': 'research/sources/snapshots/environment.json'},
        {'source': 'submissions', 'url': URLS['submissions'], 'retrievedAt': now(), 'version': f"{subs['updated']} ({len(subs['entries'])} entries)",
         'sha256': sha(body), 'snapshot': 'research/sources/snapshots/submissions.json'},
        {'source': 'skill', 'url': URLS['skill'], 'retrievedAt': now(), 'version': version, 'sha256': sha(skill), 'snapshot': 'research/sources/snapshots/skill.json'}]
    print(f"web: verifier at {json.loads(env)['kit']['commit'][:12]}, {len(subs['entries'])} submissions, skill {version}")


def fetch_web() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in URLS.items():
        (RAW / RAW_FILES[name]).write_bytes(fetch(url))


# ---------- the kit ----------
def md_table(readme: str, heading: str) -> list[list[str]]:
    sec = readme.split(f'## {heading}', 1)[1]
    rows = []
    for ln in sec.splitlines():
        if ln.startswith('|'):
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            if set(''.join(cells)) <= set('-: '):
                continue
            rows.append(cells)
        elif rows:
            break
    return rows[1:]


def plain(md: str) -> str:
    return ' '.join(re.sub(r'\*\*|`', '', md).split())


def kit_facts(readme: str, commit: str) -> dict:
    """The facts of the kit README's tables, not its prose: which case is proved, reduced or open, which modules
    it names; when each module was added, who it credits, its headline theorem names."""
    cases = []
    for title, status, lean in (r[:3] for r in md_table(readme, 'Status by period')):
        word = 'proved' if status.startswith('**Proved') else 'reduced' if status.startswith('Reduced') or 'Reduced' in status[:20] else 'open'
        cases.append({'case': plain(title), 'kitStatus': word, 'lean': re.findall(r'`([^`]+)`', lean)})
    added = []
    for cells in md_table(readme, 'Added in the kit'):
        if len(cells) < 4:
            continue
        credit = ' '.join(re.findall(r'((?:Contributed by|Proof and formalization by|Proved on|The lower cycle is by)[^.]*\.)', plain(cells[2])))
        added.append({'module': NS + plain(cells[0]).replace('/', '.'), 'addedOn': plain(cells[1]), 'credit': credit,
                      'headlines': re.findall(r'`([^`]+)`', cells[3])})
    return {'readme': f'{lk.KIT_URL.removesuffix(".git")}/blob/{commit}/lean/README.md', 'license': LICENSE_OF['kit'], 'cases': cases, 'added': added}


def sync_kit(commit_arg: str, records: list) -> str:
    if not (lk.KIT / '.git').exists():
        lk.KIT.parent.mkdir(parents=True, exist_ok=True)
        git('clone', '-q', lk.KIT_URL, str(lk.KIT), cwd=ROOT)
    git('fetch', '-q', 'origin')
    if commit_arg == 'verifier':
        commit_arg = json.loads((RAW / 'environment.json').read_text())['kit']['commit']
    target = git('rev-parse', commit_arg or 'origin/main')
    if target != git('rev-parse', 'HEAD'):
        git('checkout', '-q', target)
    built_marker = lk.KIT / '.lake' / 'rule30-built-commit'
    if not built_marker.exists() or built_marker.read_text().strip() != target:
        print(f'building the kit at {target[:12]} (build_all.sh; this takes a while) ...')
        ok, tail = lk.build_kit(ROOT / '.logs' / 'kit-build.log')
        print(tail)
        if not ok:
            raise SystemExit('the kit did not build; see .logs/kit-build.log')
        built_marker.write_text(target + '\n')
    return target


def reduce_kit(records: list) -> None:
    target = git('rev-parse', 'HEAD')
    if any((lk.KIT / n).exists() for n in ('LICENSE', 'LICENSE.md', 'COPYING')) and LICENSE_OF['kit'] == 'none':
        print('NOTE: the kit now has a LICENSE file. Read it and update research/sources/licenses.py; until then only references are kept.')
    files = {}
    for p in sorted(lk.KIT.rglob('*.lean')):
        rel = p.relative_to(lk.KIT).as_posix()
        if not rel.startswith('.lake/'):
            b = p.read_bytes()
            files[rel] = {'sha256': sha(b), 'lines': b.count(b'\n')}
    meta = {'repository': lk.KIT_URL.removesuffix('.git'), 'commit': target, 'date': git('show', '-s', '--format=%cI', target),
            'license': LICENSE_OF['kit'], 'files': files}
    body = write_json(SNAP / 'kit.json', meta)
    write_json(SNAP / 'kit-facts.json', kit_facts((lk.KIT / 'lean' / 'README.md').read_text(), target))
    records.append({'source': 'kit', 'url': meta['repository'], 'retrievedAt': now(), 'version': target, 'sha256': sha(body),
                    'snapshot': 'research/sources/snapshots/kit.json'})
    print(f'kit: {target[:12]}')


def export_kit() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    print(lk.export(RAW / 'kit-export.json'))


def reduce_export(records: list) -> None:
    """The export without the work: no statements, docstrings or definitions unless the kit's license allows them."""
    data = json.loads((RAW / 'kit-export.json').read_text())
    keep_text = licenses.ALLOWS[LICENSE_OF['kit']]
    mods = [{'name': m['name'], 'imports': m['imports'], 'declarations': m['declarations'],
             'title': next((ln.lstrip('# ').strip() for ln in ((m.get('moduleDocs') or [''])[0]).splitlines() if ln.startswith('#')), '')}
            for m in sorted(data['modules'], key=lambda m: m['name'])]
    decls = [{k: d.get(k) for k in (('name', 'module', 'kind', 'line', 'uses', 'badAxioms') + (('statement', 'doc', 'definition') if keep_text else ()))}
             for d in sorted(data['declarations'], key=lambda d: d['name'])]
    body = write_json(SNAP / 'kit-export.json.gz', {'license': LICENSE_OF['kit'], 'modules': mods, 'declarations': decls}, gz=True)
    records.append({'source': 'kit-export', 'url': 'lean/ExportKit.lean', 'retrievedAt': now(), 'version': f'{len(mods)} modules, {len(decls)} declarations',
                    'sha256': sha(body), 'snapshot': 'research/sources/snapshots/kit-export.json.gz'})


# ---------- the submissions ----------
def license_of_source(text: str) -> str:
    """A submission's license, if its Lean source declares one (an SPDX line near the top); otherwise none."""
    m = re.search(r'SPDX-License-Identifier:\s*([A-Za-z0-9.+-]+)', '\n'.join(text.splitlines()[:40]))
    return m.group(1) if m and m.group(1) in licenses.LICENSES else 'none'


def verify_one(e: dict) -> dict:
    """One submission: its Lean source compiled against the kit as Rule30Submission, checked, exported. The
    result is cached next to the build (keyed by the source's hash and the kit commit)."""
    url = (e.get('files') or {}).get('lean')
    if not url:
        return {'compiled': False, 'note': 'no Lean source in the submission'}
    src = RAW / 'submissions' / f"{e['id']}.lean"
    if not src.exists():
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_bytes(fetch(url))
    work = lk.OUT / 'submissions' / e['id']
    work.mkdir(parents=True, exist_ok=True)
    key = sha(src.read_bytes() + (lk.KIT / '.lake' / 'rule30-built-commit').read_bytes())
    cache = work / 'result.json'
    if cache.exists() and json.loads(cache.read_text()).get('key') == key:
        return json.loads(cache.read_text())['result']
    ok, msgs = lk.compile_module(src, 'Rule30Submission', work)
    rec = {'sha256': sha(src.read_bytes()), 'compiled': ok}
    if ok:
        claim = {'proof': f"problem{e.get('problem', 1)}", 'disproof': f"not_problem{e.get('problem', 1)}"}.get(e.get('claim'), 'partial')
        rec['check'] = lk.check('Rule30Submission', e.get('headlines') or [], work, claim)
        try:
            lk.export(work / 'export.json', ['Rule30Submission'], ['Rule30Submission'], extra=work)
            rec['declarations'] = json.loads((work / 'export.json').read_text())['declarations']
        except RuntimeError as err:
            rec['exportError'] = str(err)[-1000:]
    cache.write_text(json.dumps({'key': key, 'result': rec}))
    return rec


def verify_submissions(workers: int = 4) -> None:
    from concurrent.futures import ThreadPoolExecutor
    subs = json.loads((RAW / 'submissions.json').read_text())['entries']
    with ThreadPoolExecutor(max_workers=workers) as pool:   # each Lean process needs a few GB
        for e, rec in zip(subs, pool.map(verify_one, subs)):
            print(f"{e['id']}: compiled={rec.get('compiled')} verdict={rec.get('check', {}).get('verdict')}", flush=True)


def reduce_submissions(records: list) -> None:
    """Our verdicts on every submission, and the names of what it declares. A source whose license allows it is
    copied to research/sources/included/ with its statements; every other one stays in external/."""
    subs = json.loads((RAW / 'submissions.json').read_text())['entries']
    out = {}
    for e in subs:
        url = (e.get('files') or {}).get('lean')
        src = RAW / 'submissions' / f"{e['id']}.lean"
        cache = lk.OUT / 'submissions' / e['id'] / 'result.json'
        if not url or not src.exists() or not cache.exists():
            out[e['id']] = {'sourceUrl': url, 'license': 'none', 'compiled': False, 'checked': False,
                            'note': 'no Lean source in the submission' if not url else 'not checked here yet'}
            continue
        rec = json.loads(cache.read_text())['result']
        lic = license_of_source(src.read_text(errors='replace'))
        keep_text = licenses.ALLOWS[lic]
        if keep_text:
            INCLUDED.joinpath('submissions').mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, INCLUDED / 'submissions' / src.name)
        ck = rec.get('check') or {}
        heads = set(e.get('headlines') or [])
        out[e['id']] = {
            'sourceUrl': url, 'sourceSha256': rec.get('sha256'), 'license': lic, 'included': f'research/sources/included/submissions/{src.name}' if keep_text else None,
            'compiled': rec.get('compiled'), 'checked': True,
            'check': {'verdict': ck.get('verdict'), 'replayOk': (ck.get('replay') or {}).get('ok'), 'reasons': ck.get('reasons', []) if ck.get('verdict') != 'pass' else [],
                      'headlines': [{'name': h.get('name'), 'ok': h.get('ok'), 'axioms': h.get('axioms', [])} for h in ck.get('headlines', [])]},
            'declarations': [{k: d.get(k) for k in (('name', 'kind', 'line', 'badAxioms') + (('statement', 'doc', 'definition') if keep_text else ()))}
                             for d in rec.get('declarations', []) if d['kind'] == 'proposition' or d['name'] in heads]}
    body = write_json(SNAP / 'submission-checks.json', out)
    n_pass = sum(1 for r in out.values() if (r.get('check') or {}).get('verdict') == 'pass')
    records.append({'source': 'submission-checks', 'url': 'research/lean/leankit.py', 'retrievedAt': now(), 'version': f'{n_pass} of {len(out)} pass here',
                    'sha256': sha(body), 'snapshot': 'research/sources/snapshots/submission-checks.json'})


def main(argv: list[str]) -> None:
    SNAP.mkdir(parents=True, exist_ok=True)
    commit = argv[argv.index('--commit') + 1] if '--commit' in argv else ''
    records: list = []
    if '--from-raw' not in argv:
        fetch_web()
        sync_kit(commit, records)
        export_kit()
        verify_submissions()
    reduce_web(records)
    reduce_kit(records)
    reduce_export(records)
    reduce_submissions(records)
    log = SNAP / 'syncs.json'
    history = json.loads(log.read_text()) if log.exists() else []
    log.write_text(json.dumps(history + records, indent=1) + '\n')
    (ROOT / 'NOTICE.md').write_text(licenses.notice())
    import build_challenge
    build_challenge.main()
    if '--no-build' not in argv:
        import loop_tools as lt
        print(json.dumps(lt.build(), indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
