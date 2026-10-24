"""Hub editing helpers for the Rule 30 research ledger.

Every mutation of effortless-rulebook.json goes through here so that:
  * Prerequisites stays the exact transitive closure of Dependencies,
  * every Assertion has an Assessment row,
  * evidence hashes are computed, never typed,
  * the file keeps Single Line Leaves formatting (one line per field, one per row).

Derived values (IsUsable, Blocked, CurrentStatus, ...) are NEVER computed here.
`effortless build` computes them; `consume()` reads them back.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDITOR_API = 'http://localhost:42441'   # effortless-rulebook/ports.env
RULEBOOK = ROOT / 'effortless-rulebook' / 'effortless-rulebook.json'
CURRENT_LOOP = ''   # set by run_loop; tags new claims and revisions with the loop that made them
USABLE = {'DEFINITION', 'PROVED_HUMAN_READABLE', 'REDERIVED_KNOWN', 'FINITE_VERIFIED'}
ALLOWED = USABLE | {'FALSIFIED', 'OPEN', 'SUPERSEDED'}


# ---------- file format ----------
def load() -> dict:
    return json.loads(RULEBOOK.read_text())


def _dump_single_line_leaves(book: dict) -> str:
    out = ['{']
    keys = list(book)
    for i, k in enumerate(keys):
        v = book[k]
        comma = ',' if i < len(keys) - 1 else ''
        if isinstance(v, dict) and 'schema' in v:
            out.append(f'  {json.dumps(k)}: {{')
            inner = [kk for kk in v if kk not in ('schema', 'data')]
            for kk in inner:
                out.append(f'    {json.dumps(kk)}: {json.dumps(v[kk])},')
            out.append('    "schema": [')
            out.append(',\n'.join('      ' + json.dumps(f) for f in v['schema']))
            out.append('    ],')
            out.append('    "data": [')
            out.append(',\n'.join('      ' + json.dumps(r) for r in v.get('data', [])))
            out.append('    ]')
            out.append('  }' + comma)
        else:
            out.append(f'  {json.dumps(k)}: {json.dumps(v)}{comma}')
    out.append('}')
    return '\n'.join(out) + '\n'


# ---------- caches of load-bearing computed fields ----------
# A cached field's formula is IF({{IsCached}}=1, {{<Field>Cache}}, <its formula>). The caches hold the
# values of the last fresh compile, so Postgres (which computes every view on read) skips the chain
# behind them. They are only ever true: every save clears the flags (any edit may change what they
# depend on), and build() fills them right after a compile that ran with the flags cleared.
CACHE_FLAG = 'IsCached'
CACHED_PREFIX = '=IF({{%s}}=1,' % CACHE_FLAG


def cached_fields(book: dict) -> dict[str, list[str]]:
    return {t: [f['name'] for f in v['schema'] if str(f.get('formula', '')).startswith(CACHED_PREFIX)]
            for t, v in book.items() if isinstance(v, dict) and any(f['name'] == CACHE_FLAG for f in v.get('schema', []))}


def clear_caches(book: dict) -> None:
    for t in cached_fields(book):
        for r in rows(book, t):
            r.pop(CACHE_FLAG, None)


def fill_caches(book: dict) -> int:
    n = 0
    for t, names in cached_fields(book).items():
        for r in rows(book, t):
            for f in names:
                r[f + 'Cache'] = r.get(f)
            r[CACHE_FLAG] = 1
            n += 1
    return n


def save(book: dict) -> None:
    regen_prerequisites(book)
    ensure_assessments(book)
    clear_caches(book)
    RULEBOOK.write_text(_dump_single_line_leaves(book))


def sha256_file(p: Path | str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rulebook_hash() -> str:
    return sha256_file(RULEBOOK)


# ---------- lookups ----------
def rows(book: dict, table: str) -> list[dict]:
    return book[table]['data']


def row(book: dict, table: str, key: str) -> dict:
    pk = book[table]['schema'][0]['name']
    for r in rows(book, table):
        if r[pk] == key:
            return r
    raise KeyError(f'{table}.{key}')


def has(book: dict, table: str, key: str) -> bool:
    try:
        row(book, table, key)
        return True
    except KeyError:
        return False


def _strip_derived(book: dict, table: str, r: dict) -> dict:
    """Keep only raw/relationship columns; compiled columns are rebuilt by the build."""
    keep = [f['name'] for f in book[table]['schema'] if f['type'] in ('raw', 'relationship')]
    return {k: r[k] for k in keep if k in r}


# ---------- structural invariants ----------
def ensure_assessments(book: dict) -> None:
    present = {r['AssessmentId'] for r in rows(book, 'Assessments')}
    for a in rows(book, 'Assertions'):
        if a['AssertionId'] not in present:
            rows(book, 'Assessments').append({'AssessmentId': a['AssertionId'], 'Assertion': a['AssertionId'], 'ProjectKey': 'Rule30'})


def regen_prerequisites(book: dict) -> None:
    ids = {a['AssertionId'] for a in rows(book, 'Assertions')}
    for a in rows(book, 'Assertions'):
        assert a['ReportedStatus'] in ALLOWED, a
    parents: dict[str, set[str]] = {k: set() for k in ids}
    for d in rows(book, 'Dependencies'):
        assert d['Conclusion'] in ids and d['Premise'] in ids, d
        parents[d['Conclusion']].add(d['Premise'])

    def closure(k, active=frozenset()):
        assert k not in active, f'claim cycle through {k}'
        s = {k}
        for p in parents[k]:
            s |= closure(p, active | {k})
        return s

    new = []
    for k in sorted(ids, key=lambda x: [a['AssertionId'] for a in rows(book, 'Assertions')].index(x)):
        for p in sorted(closure(k)):
            new.append({'PrerequisiteId': f'{k}-{p}', 'ConclusionKey': k, 'Premise': p})
    book['Prerequisites']['data'] = new


# ---------- mutations ----------
KIND_BY_PREFIX = [('D', 'Definition'), ('K', 'Known result'), ('T', 'Theorem'), ('F', 'Finite check'), ('H', 'Hypothesis'), ('B', 'Bridge obligation'), ('P', 'Prize problem')]


def add_assertion(book, aid, statement, status='OPEN', proof_section='', deps=(), kind=None):
    assert not has(book, 'Assertions', aid), f'{aid} exists'
    kind = kind or next(k for p, k in KIND_BY_PREFIX if aid.startswith(p))
    rows(book, 'Assertions').append({'AssertionId': aid, 'Statement': statement, 'ReportedStatus': status, 'ProofSection': proof_section, 'Kind': kind, 'IntroducedInLoop': CURRENT_LOOP})
    for p in deps:
        add_dependency(book, aid, p)


def add_dependency(book, conclusion, premise):
    did = f'{conclusion}-{premise}'
    if not has(book, 'Dependencies', did):
        rows(book, 'Dependencies').append({'DependencyId': did, 'Conclusion': conclusion, 'Premise': premise})


def set_status(book, aid, new_status, reason, replacement=''):
    a = row(book, 'Assertions', aid)
    prior = a['ReportedStatus']
    assert new_status in ALLOWED
    n = 1 + sum(1 for r in rows(book, 'Revisions') if r['Assertion'] == aid)
    rows(book, 'Revisions').append({'RevisionId': f'revision-{aid}-{n}', 'Assertion': aid, 'PriorStatus': prior, 'NewStatus': new_status, 'Reason': reason, 'Replacement': replacement, 'Loop': CURRENT_LOOP})
    a['ReportedStatus'] = new_status


def add_evidence(book, eid, path, supports=()):
    """path is relative to the repo root. Hash is computed from the file, never typed."""
    p = ROOT / path
    assert p.is_file(), p
    if has(book, 'Evidence', eid):
        row(book, 'Evidence', eid).update({'Path': path, 'Sha256': sha256_file(p)})
    else:
        rows(book, 'Evidence').append({'EvidenceId': eid, 'Path': path, 'Sha256': sha256_file(p)})
    for aid in supports:
        link_evidence(book, eid, aid)


def link_evidence(book, eid, aid):
    lid = f'{eid}-{aid}'
    if not has(book, 'EvidenceLinks', lid):
        rows(book, 'EvidenceLinks').append({'EvidenceLinkId': lid, 'Evidence': eid, 'Assertion': aid})


def verify_evidence(book) -> list[str]:
    bad = []
    for e in rows(book, 'Evidence'):
        p = ROOT / e['Path']
        if not p.is_file() or sha256_file(p) != e['Sha256']:
            bad.append(e['EvidenceId'])
    return bad


# ---------- build / consume / loop record ----------
def _effortless_build() -> tuple[int, str]:
    proc = subprocess.run(['effortless', 'build'], cwd=ROOT, capture_output=True, text=True)
    log = proc.stdout + proc.stderr
    versions = [ln.strip() for ln in log.splitlines() if ln.startswith('cli:>')]
    assert proc.returncode == 0 and len(versions) >= 2, log[-2000:]
    return versions, log


def build() -> dict:
    """Clear the caches, `effortless build`, fill the caches from that compile, build again.

    Returns a receipt (never a value). The second build compiles with the caches set, so it yields
    the same values and regenerates every spoke from the cached rulebook.
    """
    t0 = time.time()
    book = load()
    clear_caches(book)
    RULEBOOK.write_text(_dump_single_line_leaves(book))
    versions, log = _effortless_build()
    book = load()
    filled = fill_caches(book)
    RULEBOOK.write_text(_dump_single_line_leaves(book))
    _, log2 = _effortless_build()
    receipt = {'exit': 0, 'seconds': round(time.time() - t0, 1), 'versions': versions, 'cached_rows': filled,
               'log_sha256': hashlib.sha256((log + log2).encode()).hexdigest()}
    receipt['editor'] = refresh_editor()
    return receipt


def refresh_editor() -> str:
    """Ask the running rulebook editor to rebuild, so the explorer shows this build.

    The editor does not rebuild by itself when the rulebook file changes from outside: it
    offers a rebuild in its UI and drops the offer if nobody answers. An explicit
    run-build request is the documented way to say yes. Skipped when the admin portal holds
    unsaved edits, because a rebuild would push the rulebook's values over them.
    """
    try:
        st = json.load(urllib.request.urlopen(f'{EDITOR_API}/api/uncommitted-status', timeout=3))
    except Exception:
        return 'editor not running'
    if st.get('pending'):
        return f"skipped: {st.get('changeCount')} unsaved admin-portal edit(s)"
    try:
        req = urllib.request.Request(f'{EDITOR_API}/api/admin/run-build', data=b'{}', method='POST', headers={'Content-Type': 'application/json'})
        r = json.load(urllib.request.urlopen(req, timeout=10))
    except Exception as e:
        return f'refresh failed: {e}'
    if r.get('started'):
        return 'refresh requested'
    # The editor drops requests while it is building; a detached waiter retries until it is current.
    subprocess.Popen([sys.executable, str(ROOT / 'research' / 'editor_refresh.py')], cwd=ROOT,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return 'refresh queued (editor busy)'



def consume(book, assertion_ids) -> dict:
    """Read compiled values back. This is the only legal way to learn a status."""
    out = {}
    for aid in assertion_ids:
        r = row(book, 'Assessments', aid)
        out[aid] = {k: r[k] for k in ('ReportedStatus', 'EffectiveStatus', 'IsModelDecided', 'CurrentStatus', 'BlockedCount', 'ProofBlockedCount', 'ProofEligible', 'SupportCount', 'EvidenceGap') if k in r}
    out['_dashboard'] = dict(rows(book, 'Dashboards')[0])
    return out


def _now():
    return time.strftime('%Y-%m-%dT%H:%M:%S%z')


def start_loop(book, loop_id, hypothesis):
    """Add the loop as RUNNING so the explorer shows it while it works. A PLANNED row (research/strategy.py)
    with the same id is started in place, keeping its plan and its LoopTargets."""
    if has(book, 'Loops', loop_id) and row(book, 'Loops', loop_id)['State'] == 'PLANNED':
        row(book, 'Loops', loop_id).update({'State': 'RUNNING', 'StartedAt': _now(), 'Hypothesis': hypothesis})
        return
    assert not has(book, 'Loops', loop_id)
    seq = 1 + max(r['Sequence'] for r in rows(book, 'Loops'))
    rows(book, 'Loops').append({'LoopId': loop_id, 'Kind': 'EFFORTLESS', 'State': 'RUNNING', 'BuildReceipt': '', 'InputHash': '', 'OutputHash': '',
                                'Sequence': seq, 'StartedAt': _now(), 'FinishedAt': '', 'ProjectKey': 'Rule30', 'Hypothesis': hypothesis, 'Summary': ''})


def finish_loop(book, loop_id, summary, input_hash, receipt, output_hash):
    r = row(book, 'Loops', loop_id)
    assert r['State'] == 'RUNNING'
    r.update({'State': 'VERIFIED', 'BuildReceipt': json.dumps(receipt, sort_keys=True), 'InputHash': input_hash, 'OutputHash': output_hash,
              'Summary': summary, 'FinishedAt': _now()})


def record_model_outcomes(book, loop_id, aids) -> list[str]:
    """After a build: a Revision for each claim whose status the model decided differently from its report.

    The status itself is never typed: Assertions.EffectiveStatus is computed from the claim's predicate.
    The revision only records, in the loop that caused it, what the build decided and why.
    """
    made = []
    for aid in aids:
        a = row(book, 'Assertions', aid)
        if a.get('EffectiveStatus') and a['EffectiveStatus'] != a['ReportedStatus']:
            n = 1 + sum(1 for r in rows(book, 'Revisions') if r['Assertion'] == aid)
            rows(book, 'Revisions').append({'RevisionId': f'revision-{aid}-{n}', 'Assertion': aid, 'PriorStatus': a['ReportedStatus'],
                                            'NewStatus': a['EffectiveStatus'], 'Reason': f"decided by the model ({a['Predicate']}): {a['ModelVerdict']}",
                                            'Replacement': '', 'Loop': loop_id})
            made.append(aid)
    return made


def run_loop(loop_id: str, hypothesis: str, edit, consume_ids, outdir: Path, summarize=None) -> dict:
    """The whole loop: start (RUNNING) -> edit -> build -> consume -> finish (VERIFIED) -> build.

    `edit(book)` applies this loop's hub changes and returns a one-paragraph summary.
    A model-native loop passes `summarize(book)` instead of writing its outcome into `edit`: it runs on
    the built rulebook, records the model's decisions as Revisions and returns the summary.
    Returns the consumed compiled values, also written to outdir/consumed.json.
    """
    global CURRENT_LOOP
    outdir.mkdir(parents=True, exist_ok=True)
    pre_bytes = RULEBOOK.read_bytes()
    book = load()
    start_loop(book, loop_id, hypothesis)
    save(book)
    build()
    CURRENT_LOOP = loop_id
    try:
        book = load()
        summary = edit(book)
        save(book)
    except BaseException:
        # A crash in the loop's own code is not a research outcome: put the hub back as it was.
        RULEBOOK.write_bytes(pre_bytes)
        build()
        raise
    finally:
        CURRENT_LOOP = ''
    input_hash = rulebook_hash()
    receipt = build()
    output_hash = rulebook_hash()
    book = load()
    consumed = consume(book, consume_ids)
    consumed['_receipt'] = receipt
    consumed['_input_hash'] = input_hash
    consumed['_output_hash'] = output_hash
    (outdir / 'consumed.json').write_text(json.dumps(consumed, indent=1) + '\n')
    if summarize:
        record_model_outcomes(book, loop_id, consume_ids)
        summary = f'{summary} {summarize(book)}'.strip()
    finish_loop(book, loop_id, summary, input_hash, receipt, output_hash)
    save(book)
    receipt2 = build()
    final = load()
    dash = dict(rows(final, 'Dashboards')[0])
    (outdir / 'loop-record.json').write_text(json.dumps({'loop': row(final, 'Loops', loop_id), 'post_record_build': receipt2, 'dashboard_after': dash}, indent=1) + '\n')
    return consumed
