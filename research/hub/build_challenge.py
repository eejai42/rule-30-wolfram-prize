"""The challenge in the model: the public record of the Rule 30 Prize, loaded from the synced snapshots.

  Sources        ChallengeSources, SourceSyncs                   (research/sources/snapshots/, sync.py)
  The kit        LeanModules, LeanImports, LeanDeclarations, LeanUses   (lean/ExportKit.lean)
  Submissions    Submissions, SubmissionTags, SubmissionHeadlines, SubmissionModules, and every
                 submission's own declarations (re-verified here by the kit's Check.lean)
  The bridge     ClaimLinks (our claims -> kit declarations), LeanProofs (Lean proofs of our claims),
                 LeanChecks (what the kernel said, research/lean/checks.json)
  The ledger     one claim per kit module (L-...), the kit's case split of Problem 1 (KC...), its open
                 statements (Q-...), the route node B10, and the Lean side of every claim's status:
                 LeanStatement, IsLeanVerified, LEAN_VERIFIED in EffectiveStatus.

Only structure and inputs are data: what the export, the submissions list and the kernel said. Every
status, count and flag is a formula. Rerunnable: the tables above are replaced; kit claims are upserted
(a module that leaves the kit keeps its claim, SUPERSEDED). build_model.py calls apply(); run this file
alone after research/sources/sync.py.
Usage: python3 research/hub/build_challenge.py && python3 research/build.py
"""
from __future__ import annotations
import gzip, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'research' / 'lean'))
import loop_tools as lt

SNAP = ROOT / 'research' / 'sources' / 'snapshots'
CHECKS = ROOT / 'research' / 'lean' / 'checks.json'
NS = 'Ruliology.CellularAutomata.'
KIT_URL = 'https://github.com/WolframInstitute/Rule30PrizeKit'
AGENTS = 'https://www.wolframcloud.com/obj/rule-30-prize/Agents'
OWNED = ('ChallengeSources', 'SourceSyncs', 'LeanModules', 'LeanImports', 'LeanDeclarations', 'LeanUses',
         'Submissions', 'SubmissionTags', 'SubmissionHeadlines', 'SubmissionModules', 'ClaimLinks', 'LeanProofs', 'LeanChecks')
ROUTE_CASES = ('Period 1', 'Period 2', 'Least period 3', 'Least period 4', 'Longer periods')
# The kit's open statements (lean/README.md, "Status by period"), by the case that waits on them. The Lean
# name is checked against the export, so a rename in the kit fails the load instead of linking nothing.
OPEN_STATEMENTS = [
    ('Q-Q01', 'Period 2', 'Rule30ZeroBoundary.Q01',
     'Q01: no finite row of the zero-boundary left half keeps the center alternating forever. Period 2 of Problem 1 reduces to it; proved in Lean for every start of width <= 52.'),
    ('Q-Q001', 'Least period 3', 'Rule30EtherThree.Q001',
     'Q001 (or AbsorptionT t001, or C3s001): the open statement that excludes the period-3 word 001.'),
    ('Q-C3w011', 'Least period 3', 'Rule30EtherThree.C3w',
     'C3w(011): the open statement that excludes the period-3 word 011.'),
    ('Q-Absorption', 'Least period 4', 'Rule30Ether.Absorption',
     'Absorption: the ether-and-wall trap statement that period 4 reduces to.'),
    ('Q-EdgeObservable', None, 'Rule30TraceEdge.EdgeObservable',
     'EdgeObservable: equal infinite center traces of finite rows imply equal left edges. Open; with it the kit proves the official Problem 1 (Rule30TraceEdge.problem1_of_edgeObservable).'),
]


# ---------- schema helpers (the conventions of build_model.py) ----------
def F(name, dt='string', ty='raw', formula=None, rel=None, desc='', nullable=True):
    f = {'name': name, 'datatype': dt, 'type': ty, 'nullable': nullable, 'Description': desc}
    if formula:
        f['formula'] = formula
    if rel:
        f['RelatedTo'] = rel
    return f


def KEY(name, desc):
    return [F(name, desc=desc, nullable=False), F('Name', ty='calculated', formula=f'={{{{{name}}}}}', desc='Display alias.')]


def LK(name, table, fk, key, field, desc, dt='integer'):
    return F(name, dt, 'lookup', f'=INDEX({table}!{{{{{field}}}}},MATCH({{{{{fk}}}}},{table}!{{{{{key}}}}},0))', desc=desc)


def CALC(name, formula, desc, dt='integer'):
    return F(name, dt, 'calculated', formula, desc=desc)


def AGG(name, formula, desc, dt='integer'):
    return F(name, dt, 'aggregation', formula, desc=desc)


def REL(name, table, desc, nullable=True):
    return F(name, ty='relationship', rel=table, desc=desc, nullable=nullable)


def table(desc, schema, data):
    return {'Description': desc, 'schema': schema, 'data': data}


def ensure_field(book, tbl, field):
    sch = book[tbl]['schema']
    for n, f in enumerate(sch):
        if f['name'] == field['name']:
            sch[n] = field
            return
    sch.append(field)


def cached(name, formula):
    """The cache form build_model.py gives load-bearing fields: IF({{IsCached}}=1, {{<name>Cache}}, <formula>)."""
    return lt.CACHED_PREFIX + '{{%sCache}},%s)' % (name, formula[1:])


def one_line(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def clip(s, n):
    s = s or ''
    return s if len(s) <= n else s[:n - 2] + ' …'


# ---------- inputs ----------
def load_inputs():
    kit = json.loads((SNAP / 'kit.json').read_text())
    export = json.loads(gzip.decompress((SNAP / 'kit-export.json.gz').read_bytes()))
    env = json.loads((SNAP / 'environment.json').read_text())
    subs = json.loads((SNAP / 'submissions.json').read_text())
    checks = json.loads((SNAP / 'submission-checks.json').read_text()) if (SNAP / 'submission-checks.json').exists() else {}
    syncs = json.loads((SNAP / 'syncs.json').read_text()) if (SNAP / 'syncs.json').exists() else []
    readme = (SNAP / 'kit-lean-README.md').read_text()
    skill = (SNAP / 'skill.md').read_text()
    lean_checks = json.loads(CHECKS.read_text()) if CHECKS.exists() else {'checks': []}
    return kit, export, env, subs, checks, syncs, readme, skill, lean_checks


def module_path(name, files):
    for cand in (f"lean/{name.replace('.', '/')}.lean", f"equivalents/{name.replace('.', '/')}.lean", f"{name.replace('.', '/')}.lean"):
        if cand in files:
            return cand
    return ''


def short(name):
    return name.removeprefix(NS)


def is_certificate(name):
    return '.Rule30Certificates.' in name


def md_table(readme, heading):
    """Rows of the first Markdown table under a '## heading' of the kit README, as lists of cells."""
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
    return rows[1:]   # drop the header


def plain(md):
    return one_line(re.sub(r'\*\*|`', '', md))


# ---------- the load ----------
def apply(book: dict) -> dict:
    kit, export, env, subs, checks, syncs, readme, skill, lean_checks = load_inputs()
    commit = kit['commit']
    files = kit['files']
    verifier_commit = env['kit']['commit']
    verifier_modules = set(m for ms in env.get('modules', {}).values() for m in ms)
    for t in OWNED:
        book.pop(t, None)

    # --- sources ---
    skill_version = next((ln.split(':', 1)[1].strip() for ln in skill.splitlines() if ln.startswith('version:')), '')
    sources = [
        {'ChallengeSourceId': 'kit', 'Title': 'Rule 30 Prize kit (reference Lean environment)', 'Url': KIT_URL, 'Role': 'The official statements, the catalog of partial results and the equivalent forms, in Lean.',
         'Version': commit, 'VersionDate': kit['date'], 'Snapshot': 'research/sources/snapshots/kit.json', 'IsOfficial': 1},
        {'ChallengeSourceId': 'verifier', 'Title': "The verifier's environment", 'Url': f'{AGENTS}/api/environment', 'Role': 'The kit commit, Lean and Mathlib versions a submission is checked against, and the modules it may import.',
         'Version': verifier_commit, 'VersionDate': env['kit'].get('date', ''), 'Snapshot': 'research/sources/snapshots/environment.json', 'IsOfficial': 1},
        {'ChallengeSourceId': 'submissions', 'Title': 'Rule 30 Prize submissions', 'Url': f'{AGENTS}/submissions.json', 'Role': 'Every submission: abstract, headline theorems, verifier status, reviewer tags.',
         'Version': subs['updated'], 'VersionDate': subs['updated'], 'Snapshot': 'research/sources/snapshots/submissions.json', 'IsOfficial': 1},
        {'ChallengeSourceId': 'skill', 'Title': 'The Rule 30 Prize, for AI agents (skill.md)', 'Url': f'{AGENTS}/skill.md', 'Role': 'The official instructions for agents: setup, ground rules, what is known, how to prove and submit.',
         'Version': skill_version, 'VersionDate': '', 'Snapshot': 'research/sources/snapshots/skill.md', 'IsOfficial': 1},
        {'ChallengeSourceId': 'announcement', 'Title': 'Announcing the Rule 30 Prizes (Wolfram, 2019)', 'Url': 'https://writings.stephenwolfram.com/2019/10/announcing-the-rule-30-prizes/',
         'Role': 'The three problems in words, and the prize rules (rule30prize.org).', 'Version': '2019-10-01', 'VersionDate': '2019-10-01', 'Snapshot': '', 'IsOfficial': 1},
    ]
    book['ChallengeSources'] = table(
        'The public record of the Rule 30 Prize this model is measured against, and the version of each that was last synced (research/sources/sync.py).',
        KEY('ChallengeSourceId', 'kit, verifier, submissions, skill, announcement.') + [
            F('Title'), F('Url'), F('Role', desc='What the source is for.'),
            F('Version', desc='What was synced: a commit, a timestamp, a version.'), F('VersionDate'),
            F('Snapshot', desc='The repo file holding the synced copy (pinned as Evidence).'),
            F('IsOfficial', 'integer', desc='1 for a source published by the prize (Wolfram, the Wolfram Institute).', nullable=False),
            AGG('SyncCount', '=COUNTIFS(SourceSyncs!{{Source}},{{ChallengeSourceId}})', 'Times it was synced.'),
            AGG('ModuleCount', '=COUNTIFS(LeanModules!{{Source}},{{ChallengeSourceId}})', 'Lean modules from this source.'),
        ], sources)
    src_ids = {s['ChallengeSourceId'] for s in sources}
    sync_rows = []
    for n, r in enumerate(syncs, 1):
        src = {'kit-export': 'kit', 'submission-checks': 'submissions'}.get(r['source'], r['source'])
        sync_rows.append({'SourceSyncId': f"sync-{n:04d}", 'Source': src if src in src_ids else None, 'What': r['source'], 'RetrievedAt': r['retrievedAt'],
                          'Version': r.get('version', ''), 'Sha256': r.get('sha256', ''), 'Snapshot': r.get('snapshot', '')})
    book['SourceSyncs'] = table(
        'Every sync of a challenge source: when, what version, and the hash of what was saved. Appended by research/sources/sync.py.',
        KEY('SourceSyncId', 'sync-<n>.') + [REL('Source', 'ChallengeSources', 'The source synced.'), F('What', desc='The file synced (environment, submissions, skill, kit, kit-export, submission-checks).'),
                                            F('RetrievedAt'), F('Version'), F('Sha256'), F('Snapshot')],
        sync_rows)

    # --- the kit: modules, imports, declarations, uses ---
    added = {}
    for cells in md_table(readme, 'Added in the kit'):
        if len(cells) >= 4:
            mod = NS + plain(cells[0]).replace('/', '.')
            added[mod] = {'AddedOn': plain(cells[1]), 'Credit': plain(cells[2]), 'Headlines': re.findall(r'`([^`]+)`', cells[3])}
    mods = {m['name']: m for m in export['modules']}
    decls = export['declarations']
    by_module = {}
    for d in decls:
        by_module.setdefault(d['module'], []).append(d)
    headline_names = {NS + short(m) + '.' + h if not h.startswith(NS) else h for m, a in added.items() for h in a['Headlines']}
    mod_rows = []
    for name, m in sorted(mods.items()):
        docs = m.get('moduleDocs') or []
        first = docs[0] if docs else ''
        title = next((ln.lstrip('# ').strip() for ln in first.splitlines() if ln.startswith('#')), '')
        body = one_line('\n'.join(ln for ln in first.splitlines() if not ln.startswith('#')))
        path = module_path(name, files)
        a = added.get(name, {})
        pkg = 'Rule30Equivalents' if name.startswith('Rule30Equivalents') else 'Ruliology' if name.startswith('Ruliology') else 'Rule30PrizeKit'
        mod_rows.append({'LeanModuleId': name, 'Source': 'kit', 'Package': pkg, 'ShortName': short(name), 'Path': path,
                         'Sha256': files.get(path, {}).get('sha256', ''), 'LineCount': files.get(path, {}).get('lines', 0),
                         'Title': clip(title, 300), 'Summary': clip(body, 1500), 'AddedOn': a.get('AddedOn', ''), 'Credit': clip(a.get('Credit', ''), 600),
                         'IsCertificateData': int(is_certificate(name)), 'IsInVerifier': int(name in verifier_modules), 'IsExported': 1})
    # Submissions' own modules (each compiled here as Rule30Submission) and their declarations.
    sub_decls = []
    for e in subs['entries']:
        rec = checks.get(e['id'], {})
        if rec.get('declarations'):
            mid = f"submission:{e['id']}"
            mod_rows.append({'LeanModuleId': mid, 'Source': 'submissions', 'Package': 'Submission', 'ShortName': e['id'], 'Path': rec.get('source', ''),
                             'Sha256': rec.get('sha256', ''), 'LineCount': 0, 'Title': clip(e['title'], 300), 'Summary': clip(one_line(e.get('abstract', '')), 1500),
                             'AddedOn': e.get('submitted', '')[:10], 'Credit': clip(e.get('authors', ''), 600), 'IsCertificateData': 0, 'IsInVerifier': 0, 'IsExported': 1})
            heads = set(e.get('headlines') or [])
            for d in rec['declarations']:
                if d['kind'] in ('theorem', 'proposition') or d['name'] in heads:
                    sub_decls.append(dict(d, module=mid, key=f"{e['id']}:{d['name']}", headline=int(d['name'] in heads)))
    mod_ids = {r['LeanModuleId'] for r in mod_rows}
    book['LeanModules'] = table(
        "The kit's Lean modules (the official statements, the catalog of partial results, the equivalent forms) and every submission's module, as the compiled environment reports them (lean/ExportKit.lean). A module is verified when none of its declarations depends on a non-standard axiom.",
        KEY('LeanModuleId', 'The Lean module name, or submission:<id> for a submission compiled here.') + [
            REL('Source', 'ChallengeSources', 'Where the module comes from.', False),
            F('Package', desc='Ruliology (the catalog), Rule30Equivalents, Rule30PrizeKit, or Submission.'),
            F('ShortName'), F('Path', desc='Its file in the kit (or the snapshot of a submission).'), F('Sha256', desc="The file's sha256 at the synced commit."),
            F('LineCount', 'integer'), F('Title', desc="The module docstring's title."), F('Summary', desc="The module docstring's first section."),
            F('AddedOn', desc='For modules added after the catalog snapshot: the date (lean/README.md, Added in the kit).'),
            F('Credit', desc='Who proved it (lean/README.md, Added in the kit; a submission: its authors).'),
            F('IsCertificateData', 'integer', desc='1 for a data module under Rule30Certificates/.', nullable=False),
            F('IsInVerifier', 'integer', desc="1 when the verifier's environment lists the module, so a submission may import it now.", nullable=False),
            F('IsExported', 'integer', desc='1 when the module was compiled and exported here.', nullable=False),
            LK('SourceUrl', 'ChallengeSources', 'Source', 'ChallengeSourceId', 'Url', 'The source repository.', 'string'),
            LK('SourceVersion', 'ChallengeSources', 'Source', 'ChallengeSourceId', 'Version', 'The commit synced.', 'string'),
            CALC('Url', '=IF({{Package}}="Submission",{{Path}},CONCAT({{SourceUrl}},"/blob/",{{SourceVersion}},"/",{{Path}}))', 'The file at the synced commit.', 'string'),
            AGG('DeclarationCount', '=COUNTIFS(LeanDeclarations!{{Module}},{{LeanModuleId}})', 'Named declarations.'),
            AGG('TheoremCount', '=COUNTIFS(LeanDeclarations!{{Module}},{{LeanModuleId}},LeanDeclarations!{{Kind}},"theorem")', 'Theorems.'),
            AGG('PropositionCount', '=COUNTIFS(LeanDeclarations!{{Module}},{{LeanModuleId}},LeanDeclarations!{{Kind}},"proposition")', 'Propositions it defines (statements, some of them open).'),
            AGG('BadAxiomDeclarationCount', '=COUNTIFS(LeanDeclarations!{{Module}},{{LeanModuleId}},LeanDeclarations!{{BadAxiomCount}},">0")', 'Declarations that depend on sorry, native_decide or a new axiom. Must be 0.'),
            AGG('ImportCount', '=COUNTIFS(LeanImports!{{Module}},{{LeanModuleId}})', 'Kit modules it imports.'),
            AGG('ImportedByCount', '=COUNTIFS(LeanImports!{{Imports}},{{LeanModuleId}})', 'Kit modules that import it.'),
            AGG('SubmissionCount', '=COUNTIFS(SubmissionModules!{{Module}},{{LeanModuleId}})', 'Submissions that contributed it.'),
            CALC('IsVerified', '=IF(AND({{IsExported}}=1,{{BadAxiomDeclarationCount}}=0),1,0)', '1 when it compiled here and every declaration uses only propext, Classical.choice and Quot.sound.'),
        ], mod_rows)
    imports = []
    for name, m in sorted(mods.items()):
        for imp in m.get('imports', []):
            if imp in mod_ids:
                imports.append({'LeanImportId': f'{name}>{imp}', 'Module': name, 'Imports': imp})
    book['LeanImports'] = table('Which kit module imports which.', KEY('LeanImportId', '<module>><import>.') + [
        REL('Module', 'LeanModules', 'The importing module.', False), REL('Imports', 'LeanModules', 'The imported module.', False)], imports)

    decl_rows, uses = [], []
    # Certificate data modules hold thousands of data lemmas: keep only their headlines (the module row counts them).
    decls = [d for d in decls if not is_certificate(d['module']) or d['name'] in headline_names]
    kit_names = {d['name'] for d in decls}
    kinds = {d.get('key', d['name']): d['kind'] for d in decls + sub_decls}
    for d in decls + sub_decls:
        key = d.get('key', d['name'])
        bad = d.get('badAxioms') or []
        decl_rows.append({'LeanDeclarationId': key, 'LeanName': d['name'], 'Module': d['module'], 'ShortName': d['name'].rsplit('.', 1)[-1], 'Kind': d['kind'],
                          'Statement': clip(one_line(d.get('statement')), 600), 'Definition': clip(one_line(d.get('definition')), 1200),
                          'Doc': clip(one_line(d.get('doc')), 400), 'Line': d.get('line') or 0, 'BadAxioms': ', '.join(bad), 'BadAxiomCount': len(bad),
                          'IsHeadline': int(d.get('headline', d['name'] in headline_names))})
        if d['kind'] != 'theorem':
            continue
        for u in d.get('uses') or []:   # theorem -> the theorems and propositions it rests on
            target = f"{key.split(':')[0]}:{u}" if ':' in key and f"{key.split(':')[0]}:{u}" in kinds else u if u in kit_names else None
            if target and kinds.get(target) in ('theorem', 'proposition'):
                uses.append({'Declaration': key, 'Uses': target})
    decl_ids = {r['LeanDeclarationId'] for r in decl_rows}
    uses = [dict(u, LeanUseId=f'u{n:05d}') for n, u in enumerate(sorted((u for u in uses if u['Uses'] in decl_ids), key=lambda u: (u['Declaration'], u['Uses'])), 1)]
    book['LeanDeclarations'] = table(
        "Every named declaration of the kit (and the theorems of each submission compiled here): its statement as Lean prints it, its docstring, and the non-standard axioms it depends on, followed through every import. A theorem is verified when that list is empty.",
        KEY('LeanDeclarationId', 'The Lean name; <submission id>:<name> for a submission.') + [
            F('LeanName', desc='The full Lean name.'), REL('Module', 'LeanModules', 'Its module.', False), F('ShortName'),
            F('Kind', desc='theorem, def, proposition (a definition of type Prop: a statement), structure, inductive, opaque, axiom.'),
            F('Statement', desc='Its type, as Lean prints it (namespace Ruliology.CellularAutomata left out).'),
            F('Definition', desc="A proposition's definition: what the statement says."), F('Doc', desc='Its docstring.'), F('Line', 'integer'),
            F('BadAxioms', desc='The non-standard axioms it depends on (sorryAx, Lean.ofReduceBool, Lean.trustCompiler, any new axiom).'),
            F('BadAxiomCount', 'integer', desc='How many. 0 for every declaration the kit ships.', nullable=False),
            F('IsHeadline', 'integer', desc="1 for a module's headline theorem (lean/README.md) or a submission's headline.", nullable=False),
            LK('ModuleUrl', 'LeanModules', 'Module', 'LeanModuleId', 'Url', "Its module's file.", 'string'),
            LK('ModuleIsVerified', 'LeanModules', 'Module', 'LeanModuleId', 'IsVerified', '1 when its module is verified.'),
            CALC('Url', '=IF({{Line}}>0,CONCAT({{ModuleUrl}},"#L",{{Line}}),{{ModuleUrl}})', 'Where it is in the source.', 'string'),
            CALC('IsVerified', '=IF(AND({{Kind}}="theorem",{{BadAxiomCount}}=0),1,0)', '1 for a theorem with standard axioms only: the kernel accepted it.'),
            AGG('UsesCount', '=COUNTIFS(LeanUses!{{Declaration}},{{LeanDeclarationId}})', 'Named kit declarations it uses.'),
            AGG('UsedByCount', '=COUNTIFS(LeanUses!{{Uses}},{{LeanDeclarationId}})', 'Declarations that use it.'),
            AGG('ClaimLinkCount', '=COUNTIFS(ClaimLinks!{{Declaration}},{{LeanDeclarationId}})', 'Ledger claims linked to it.'),
        ], decl_rows)
    book['LeanUses'] = table('Which theorem rests on which theorem or proposition (looking through auxiliary match_ and proof_ constants).', [F('LeanUseId', desc='u<n>.', nullable=False)] + [
        REL('Declaration', 'LeanDeclarations', 'The user.', False), REL('Uses', 'LeanDeclarations', 'The declaration it uses.', False)], uses)

    # --- submissions ---
    srows, tags, heads, smods = [], [], [], []
    sub_ids = {e['id'] for e in subs['entries']}
    for e in subs['entries']:
        rec = checks.get(e['id'], {})
        ck = e.get('check') or {}
        ours = rec.get('check', {})
        verdict = ('no Lean source' if not rec.get('source') else 'did not compile' if not rec.get('compiled') else ours.get('verdict', 'error'))
        srows.append({'SubmissionId': e['id'], 'Title': clip(e['title'], 300), 'Problem': e.get('problem'), 'Claim': e.get('claim', ''),
                      'Authors': clip(e.get('authors', ''), 300), 'Agent': clip(e.get('agent', ''), 200), 'Abstract': clip(e.get('abstract', ''), 3000),
                      'Status': e.get('status', ''), 'Submitted': e.get('submitted', ''), 'Supersedes': e['supersedes'] if e.get('supersedes') in sub_ids else None,
                      'PageUrl': e.get('page', ''), 'LeanUrl': (e.get('files') or {}).get('lean', ''), 'VerifierVerdict': ck.get('verdict', ''),
                      'VerifierKitCommit': ck.get('kitCommit', ''), 'VerifierCheckedAt': ck.get('checkedAt', ''), 'OurVerdict': verdict,
                      'OurKitCommit': commit, 'LeanModule': f"submission:{e['id']}" if f"submission:{e['id']}" in mod_ids else None})
        for t in e.get('tags') or []:
            tags.append({'SubmissionTagId': f"{e['id']}:{t}", 'Submission': e['id'], 'Tag': t})
        ours_by = {h['name']: h for h in ours.get('headlines', [])}
        for h in e.get('headlines') or []:
            key = f"{e['id']}:{h}"
            heads.append({'SubmissionHeadlineId': key, 'Submission': e['id'], 'TheoremName': h, 'Declaration': key if key in decl_ids else None,
                          'OurOk': int(bool(ours_by.get(h, {}).get('ok'))), 'OurAxioms': ', '.join(ours_by.get(h, {}).get('axioms', []))})
        for m in (e.get('kitContribution') or {}).get('modules', []):
            smods.append({'SubmissionModuleId': f"{e['id']}>{m}", 'Submission': e['id'], 'Module': m if m in mod_ids else None, 'ModuleName': m})
    book['Submissions'] = table(
        "Every public Rule 30 Prize submission (submissions.json): its claim, abstract and headline theorems, the verifier's verdict and the reviewers' tags, and our own verdict: its Lean source compiled against the synced kit and checked by the kit's Check.lean.",
        KEY('SubmissionId', 'R30-<date>-<hash>.') + [
            F('Title'), F('Problem', 'integer', desc='1, 2 or 3.'), F('Claim', desc='proof, disproof or partial.'), F('Authors'), F('Agent'), F('Abstract'),
            F('Status', desc='Lean Verified or Lean Unverified (the verifier).'), F('Submitted'), REL('Supersedes', 'Submissions', 'The earlier submission this one replaces.'),
            F('PageUrl'), F('LeanUrl'), F('VerifierVerdict'), F('VerifierKitCommit', desc='The kit commit the verifier checked it against.'), F('VerifierCheckedAt'),
            F('OurVerdict', desc='pass, fail, error, did not compile, or no Lean source: the kit\'s Check.lean here, against OurKitCommit.'),
            F('OurKitCommit'), REL('LeanModule', 'LeanModules', 'The submission compiled here, with its declarations.'),
            AGG('IsHumanVerified', '=COUNTIFS(SubmissionTags!{{Submission}},{{SubmissionId}},SubmissionTags!{{Tag}},"Human Verified")', 'Reviewer tag.'),
            AGG('IsKitContribution', '=COUNTIFS(SubmissionTags!{{Submission}},{{SubmissionId}},SubmissionTags!{{Tag}},"Kit Contribution")', 'Reviewer tag: its proof joined the kit.'),
            AGG('IsPrizeClaimed', '=COUNTIFS(SubmissionTags!{{Submission}},{{SubmissionId}},SubmissionTags!{{Tag}},"Prize Claimed")', 'Reviewer tag: the Prize Committee accepted it.'),
            AGG('HeadlineCount', '=COUNTIFS(SubmissionHeadlines!{{Submission}},{{SubmissionId}})', 'Headline theorems.'),
            AGG('OurOkHeadlineCount', '=SUMIFS(SubmissionHeadlines!{{OurOk}},SubmissionHeadlines!{{Submission}},{{SubmissionId}})', 'Headlines that pass Check.lean here.'),
            AGG('KitModuleCount', '=COUNTIFS(SubmissionModules!{{Submission}},{{SubmissionId}})', 'Kit modules it contributed.'),
            CALC('IsLeanVerified', '=IF({{Status}}="Lean Verified",1,0)', "1 when the verifier accepted it."),
            CALC('AgreesWithVerifier', '=IF({{IsLeanVerified}}=1,IF({{OurVerdict}}="pass",1,0),IF({{OurVerdict}}="pass",0,1))', '1 when our check and the verifier agree.'),
        ], srows)
    book['SubmissionTags'] = table('Reviewer tags on submissions.', KEY('SubmissionTagId', '<submission>:<tag>.') + [
        REL('Submission', 'Submissions', 'The submission.', False), F('Tag', desc='Human Verified, Kit Contribution or Prize Claimed.')], tags)
    book['SubmissionHeadlines'] = table('The headline theorems of each submission, with our check of each.', KEY('SubmissionHeadlineId', '<submission>:<theorem>.') + [
        REL('Submission', 'Submissions', 'The submission.', False), F('TheoremName'), REL('Declaration', 'LeanDeclarations', 'The theorem, as exported here.'),
        F('OurOk', 'integer', desc="1 when the kit's Check.lean accepts it here.", nullable=False), F('OurAxioms'),
        LK('Statement', 'LeanDeclarations', 'Declaration', 'LeanDeclarationId', 'Statement', 'What it states.', 'string')], heads)
    book['SubmissionModules'] = table('Kit modules a submission contributed (reviewer tag Kit Contribution).', KEY('SubmissionModuleId', '<submission>><module>.') + [
        REL('Submission', 'Submissions', 'The submission.', False), REL('Module', 'LeanModules', 'The kit module, when it is in the synced kit.'), F('ModuleName')], smods)

    # --- the bridge: claim links, Lean proofs, kernel checks ---
    import claim_links
    import proofs as lean_proofs
    links = []
    for aid, decl, rel, note in claim_links.LINKS:
        assert decl in decl_ids, f'claim link {aid} -> {decl}: no such declaration in the synced kit'
        assert rel in ('same', 'stronger', 'jointly', 'weaker', 'related', 'contradicts'), rel
        links.append({'ClaimLinkId': f'{aid}>{decl}', 'Assertion': aid, 'Declaration': decl, 'Relation': rel, 'Note': note})
    book['ClaimLinks'] = table(
        "Our claims set against the kit: the kit declaration that states the same thing (same), more (stronger), less (weaker), something near it (related), or its negation (contradicts). Authored in research/hub/claim_links.py after reading both statements; a link is a reading, a LeanChecks pass is a proof.",
        KEY('ClaimLinkId', '<claim>><declaration>.') + [
            REL('Assertion', 'Assertions', 'Our claim.', False), REL('Declaration', 'LeanDeclarations', 'The kit declaration.', False),
            F('Relation', desc='same, stronger, jointly (our claim is the conjunction of its jointly links), weaker, related or contradicts: the kit declaration relative to our claim.'), F('Note'),
            LK('DeclarationStatement', 'LeanDeclarations', 'Declaration', 'LeanDeclarationId', 'Statement', 'What the kit states.', 'string'),
            LK('DeclarationIsVerified', 'LeanDeclarations', 'Declaration', 'LeanDeclarationId', 'IsVerified', '1 when the kit theorem is verified.'),
            LK('DeclarationUrl', 'LeanDeclarations', 'Declaration', 'LeanDeclarationId', 'Url', 'Where it is.', 'string'),
            CALC('Covers', '=IF(AND(OR({{Relation}}="same",{{Relation}}="stronger"),{{DeclarationIsVerified}}=1),1,0)', '1 when a verified kit theorem states our claim or more: the claim is known.'),
            CALC('Contradicts', '=IF(AND({{Relation}}="contradicts",{{DeclarationIsVerified}}=1),1,0)', '1 when a verified kit theorem refutes our claim.'),
            CALC('IsJoint', '=IF({{Relation}}="jointly",1,0)', '1 for a jointly link.'),
            CALC('IsJointVerified', '=IF(AND({{Relation}}="jointly",{{DeclarationIsVerified}}=1),1,0)', '1 for a jointly link to a verified theorem.'),
        ], links)
    book['LeanProofs'] = table(
        "A Lean proof of a claim's Lean statement (research/lean/proofs.py), usually a few lines citing the kit; or, for kind alignment, of our statement's equivalence with the official one. research/lean/ledger.py writes them into lean/Rule30Ledger.lean; the kernel's verdict is in LeanChecks.",
        KEY('LeanProofId', '<kind>-<claim>.') + [
            REL('Assertion', 'Assertions', 'The claim.', False), F('Kind', desc='claim (proves the claim) or alignment (our statement <-> the official one).'),
            F('Target', desc='For an alignment: the official Lean constant.'), F('Proof', desc='The Lean proof (a term or a tactic block).'),
            F('KitDeclarations', desc='Kit declarations it cites.'),
            F('IsKitGlue', 'integer', desc='1 when the proof only restates kit theorems: the claim is known in the kit, not new.', nullable=False), F('Note')],
        [{'LeanProofId': f"{p['kind']}-{p['claim']}", 'Assertion': p['claim'], 'Kind': p['kind'], 'Target': p.get('target', ''), 'Proof': p['proof'],
          'KitDeclarations': ', '.join(p.get('kit', [])), 'IsKitGlue': int(p.get('kit_glue', False)), 'Note': p.get('note', '')} for p in lean_proofs.PROOFS])
    book['LeanChecks'] = table(
        "What the Lean kernel said about each claim's Lean statement: lean/Rule30Ledger.lean, written from the compiled rulebook and checked by the kit's Check.lean (research/lean/ledger.py). A check counts only while its statement is the claim's current Lean statement.",
        KEY('LeanCheckId', '<kind>-<claim>.') + [
            REL('Assertion', 'Assertions', 'The claim.', False), F('Kind', desc='claim or alignment.'), F('Theorem', desc='Its name in Rule30Ledger.lean.'),
            F('CheckedStatement', desc='The Lean statement that was checked (for an alignment, our side of the equivalence).'), F('Target'),
            F('Elaborates', 'integer', desc='1 when Lean accepted the statement as well-formed.', nullable=False),
            F('HasProof', 'integer', desc='1 when a proof was supplied (otherwise the theorem is a sorry: an open Lean obligation).', nullable=False),
            F('Ok', 'integer', desc="1 when Check.lean passed it: kernel replay, standard axioms only.", nullable=False),
            F('Axioms'), F('Problems'), F('KitCommit'), F('CheckedAt'), F('LeanFileSha256'),
            LK('CurrentStatement', 'Assertions', 'Assertion', 'AssertionId', 'LeanStatement', "The claim's Lean statement now.", 'string'),
            CALC('IsCurrent', '=IF({{CheckedStatement}}={{CurrentStatement}},1,0)', '1 while the statement checked is still the one the build writes.'),
        ], [])
    load_lean_checks(book, lean_checks)

    # --- kit results as ledger claims ---
    lt_ids = {a['AssertionId']: a for a in lt.rows(book, 'Assertions')}
    for f in (REL('Source', 'ChallengeSources', 'Where a claim comes from: kit for the kit\'s results; empty for this ledger\'s own claims.'),
              REL('LeanModule', 'LeanModules', 'For a kit result: its module.'),
              REL('LeanDeclaration', 'LeanDeclarations', 'The Lean declaration that states the claim: a prize problem\'s official statement, a kit case\'s headline theorem.')):
        ensure_field(book, 'Assertions', f)

    def claim_id(module):
        return 'L-' + (short(module) if module.startswith(NS) else 'Eq-' + module.removeprefix('Rule30Equivalents.') if module.startswith('Rule30Equivalents') else module)

    def is_result(name):
        m = mods[name]
        return (name.startswith(NS) or name.startswith('Rule30Equivalents.')) and not is_certificate(name) and len(by_module.get(name, [])) > 0

    result_mods = sorted(n for n in mods if is_result(n))

    def result_imports(name, seen=None):
        """Kit result modules this module rests on, looking through certificate and aggregator modules."""
        seen = seen or set()
        out = set()
        for imp in mods[name].get('imports', []):
            if imp in seen or imp not in mods:
                continue
            seen.add(imp)
            out |= {imp} if is_result(imp) else result_imports(imp, seen)
        return out

    def upsert(aid, statement, status, kind, deps, **extra):
        if aid in lt_ids:
            a = lt_ids[aid]
            a.update({'Statement': statement, 'ReportedStatus': status, 'Kind': kind, **extra})
        else:
            lt.rows(book, 'Assertions').append({'AssertionId': aid, 'Statement': statement, 'ReportedStatus': status, 'ProofSection': '', 'Kind': kind,
                                                'IntroducedInLoop': lt.CURRENT_LOOP, **extra})
            lt_ids[aid] = lt.rows(book, 'Assertions')[-1]
        book['Dependencies']['data'] = [d for d in book['Dependencies']['data'] if d['Conclusion'] != aid]
        for p in sorted(deps):
            lt.add_dependency(book, aid, p)

    kit_claims = set()
    for name in result_mods:
        mrow = next(r for r in mod_rows if r['LeanModuleId'] == name)
        statement = mrow['Title'] or short(name)
        kind = 'Equivalent form' if name.startswith('Rule30Equivalents') else 'Lean result'
        upsert(claim_id(name), statement, 'LEAN_VERIFIED', kind, set(), Source='kit', LeanModule=name, LeanDeclaration=None)
        kit_claims.add(claim_id(name))
    for name in result_mods:
        deps = {claim_id(m) for m in result_imports(name)} - {claim_id(name)}
        book['Dependencies']['data'] = [d for d in book['Dependencies']['data'] if d['Conclusion'] != claim_id(name)]
        for p in sorted(deps):
            lt.add_dependency(book, claim_id(name), p)
    for a in lt.rows(book, 'Assertions'):   # a module that left the kit keeps its claim, superseded
        if a.get('Source') == 'kit' and a['AssertionId'].startswith('L-') and a['AssertionId'] not in kit_claims:
            a.update({'ReportedStatus': 'SUPERSEDED', 'LeanModule': None})

    # The kit's case split of Problem 1 (lean/README.md, Status by period) and its open statements.
    def resolve(token):
        token = token.strip()
        if token.endswith('*'):
            return {m for m in result_mods if short(m).startswith(token[:-1])}, set()
        if '/' in token:   # Rule30PeriodTwoWidth5/6
            stem = re.match(r'(.*?)(\d+)/(\d+)$', token)
            return ({NS + stem.group(1) + stem.group(2), NS + stem.group(1) + stem.group(3)} & set(result_mods)) if stem else set(), set()
        if NS + token in mods:
            return {NS + token}, set()
        for cand in (NS + token, NS + 'Rule30Prize.' + token):
            if cand in decl_ids:
                return {next(d['module'] for d in decls if d['name'] == cand)}, {cand}
        return set(), set()

    cases = md_table(readme, 'Status by period')
    case_ids = {}
    for n, cells in enumerate(cases, 1):
        title, status_md, lean_md = cells[0], cells[1], cells[2]
        cmods, cdecls = set(), set()
        for tok in re.findall(r'`([^`]+)`', lean_md):
            m_, d_ = resolve(tok)
            cmods |= m_
            cdecls |= d_
        cmods &= set(result_mods)
        proved = status_md.startswith('**Proved')
        aid = f'KC{n}'
        case_ids[title] = aid
        first_decl = sorted(cdecls)[0] if cdecls else None
        upsert(aid, f'{title}: {plain(status_md)}', 'LEAN_VERIFIED' if proved else 'OPEN', 'Kit case',
               {claim_id(m) for m in cmods}, Source='kit', LeanModule=sorted(cmods)[0] if (proved and cmods and not first_decl) else None,
               LeanDeclaration=first_decl if proved else None)
    for aid, case, lean_name, statement in OPEN_STATEMENTS:
        decl = NS + lean_name
        upsert(aid, statement, 'OPEN', 'Kit open statement', set(), Source='kit', LeanModule=None,
               LeanDeclaration=decl if decl in decl_ids else None)
        if case:
            lt.add_dependency(book, case_ids[case], aid)
    upsert('B10', "P1 by the least period, the kit's case split: derived from the cases period 1, period 2, least period 3, least period 4 and every longer least period, none of which can be an eventual period of the center.",
           'PROVED_HUMAN_READABLE', 'Bridge obligation', {case_ids[c] for c in ROUTE_CASES}, Source='kit')
    upsert('B11', "P1 through EdgeObservable: derived from the open hypothesis EdgeObservable and the kit's Lean theorem that it implies the official Problem 1 (Rule30TraceEdge.problem1_of_edgeObservable).",
           'PROVED_HUMAN_READABLE', 'Bridge obligation', {'Q-EdgeObservable', claim_id(NS + 'Rule30TraceEdge')}, Source='kit')
    official = {'P1': NS + 'Rule30Prize.Problem1', 'P2': NS + 'Rule30Prize.Problem2'}
    for aid, decl in official.items():
        if decl in decl_ids:
            lt_ids[aid]['LeanDeclaration'] = decl

    # --- evidence: the snapshots, pinned ---
    for eid, path, supports in [('S-kit', 'research/sources/snapshots/kit.json', ['B10']), ('S-kit-export', 'research/sources/snapshots/kit-export.json.gz', ['B10']),
                                ('S-environment', 'research/sources/snapshots/environment.json', ['P1']), ('S-submissions', 'research/sources/snapshots/submissions.json', ['P1']),
                                ('S-skill', 'research/sources/snapshots/skill.md', ['P1']), ('S-kit-readme', 'research/sources/snapshots/kit-lean-README.md', ['B10']),
                                ('S-submission-checks', 'research/sources/snapshots/submission-checks.json', ['P1']), ('S-lean-checks', 'research/lean/checks.json', ['P1'])]:
        if (ROOT / path).is_file():
            lt.add_evidence(book, eid, path, supports)

    ledger_status(book)
    return {'modules': len(mod_rows), 'declarations': len(decl_rows), 'uses': len(uses), 'submissions': len(srows), 'kit_claims': len(kit_claims),
            'cases': len(cases), 'claim_links': len(links), 'lean_checks': len(book['LeanChecks']['data'])}


def load_lean_checks(book, lean_checks):
    """LeanChecks rows from research/lean/checks.json (written by research/lean/ledger.py)."""
    aids = {a['AssertionId'] for a in lt.rows(book, 'Assertions')}
    book['LeanChecks']['data'] = [
        {'LeanCheckId': f"{c['kind']}-{c['claim']}", 'Assertion': c['claim'], 'Kind': c['kind'], 'Theorem': c['theorem'],
         'CheckedStatement': c['statement'], 'Target': c.get('target', ''), 'Elaborates': int(c['elaborates']), 'Ok': int(c['ok']),
         'HasProof': int(c['has_proof']), 'Axioms': ', '.join(c.get('axioms', [])), 'Problems': clip('; '.join(c.get('problems', [])), 1500),
         'KitCommit': lean_checks.get('kitCommit', ''), 'CheckedAt': lean_checks.get('checkedAt', ''), 'LeanFileSha256': lean_checks.get('leanFileSha256', '')}
        for c in lean_checks.get('checks', []) if c['claim'] in aids]
    if CHECKS.exists():
        lt.add_evidence(book, 'S-lean-checks', 'research/lean/checks.json', ['P1'])


def ledger_status(book):
    """The Lean side of every claim's status, and LEAN_VERIFIED in the status vocabulary."""
    A = 'Assertions'
    for f in [
        LK('LeanStatement', 'Predicates', 'Predicate', 'PredicateId', 'LeanStatement', "The claim's statement in Lean, written by the build from its term tree (empty while some operator has no Lean meaning).", 'string'),
        LK('IsLeanExpressible', 'Predicates', 'Predicate', 'PredicateId', 'IsLeanExpressible', '1 when the build writes the statement in Lean.'),
        AGG('LeanCheckCount', '=COUNTIFS(LeanChecks!{{Assertion}},{{AssertionId}},LeanChecks!{{Kind}},"claim",LeanChecks!{{IsCurrent}},1)', 'Kernel checks of the current Lean statement.'),
        AGG('LeanCheckOk', '=COUNTIFS(LeanChecks!{{Assertion}},{{AssertionId}},LeanChecks!{{Kind}},"claim",LeanChecks!{{IsCurrent}},1,LeanChecks!{{Ok}},1)', 'Kernel checks of the current Lean statement that passed.'),
        AGG('IsOfficiallyAligned', '=COUNTIFS(LeanChecks!{{Assertion}},{{AssertionId}},LeanChecks!{{Kind}},"alignment",LeanChecks!{{IsCurrent}},1,LeanChecks!{{Ok}},1)', "1 when Lean proves the claim's statement equivalent to the official one."),
        AGG('IsKitModuleLinked', '=COUNTIFS(LeanModules!{{LeanModuleId}},{{LeanModule}})', '1 when the claim is a kit module.'),
        AGG('IsKitDeclarationLinked', '=COUNTIFS(LeanDeclarations!{{LeanDeclarationId}},{{LeanDeclaration}})', '1 when a Lean declaration states the claim.'),
        LK('LeanModuleIsVerified', 'LeanModules', 'LeanModule', 'LeanModuleId', 'IsVerified', '1 when the kit module is verified.'),
        LK('LeanDeclarationIsVerified', 'LeanDeclarations', 'LeanDeclaration', 'LeanDeclarationId', 'IsVerified', '1 when the Lean declaration is a verified theorem.'),
        LK('LeanDeclarationStatement', 'LeanDeclarations', 'LeanDeclaration', 'LeanDeclarationId', 'Statement', 'The Lean declaration, as Lean prints it.', 'string'),
        LK('LeanDeclarationDefinition', 'LeanDeclarations', 'LeanDeclaration', 'LeanDeclarationId', 'Definition', "For an official statement: its definition.", 'string'),
        LK('LeanModuleUrl', 'LeanModules', 'LeanModule', 'LeanModuleId', 'Url', "The kit module's file.", 'string'),
        CALC('IsOwnClaim', '=IF({{Source}}="kit",0,1)', "1 for this ledger's own claims, 0 for the kit's."),
        CALC('IsLeanLinked', '=IF(OR({{IsLeanExpressible}}=1,{{IsKitModuleLinked}}>0,{{IsKitDeclarationLinked}}>0),1,0)', '1 when the claim has a Lean form: its own Lean statement, a kit module or a Lean declaration.'),
        CALC('IsFormallyStated', '=IF(OR({{IsModelLinked}}=1,{{IsLeanLinked}}=1),1,0)', '1 when the claim is stated formally: as a term tree of the model or in Lean.'),
        CALC('IsLeanVerified', '=IF({{LeanCheckOk}}>0,1,IF(AND({{ReportedStatus}}="LEAN_VERIFIED",OR({{LeanModuleIsVerified}}=1,{{LeanDeclarationIsVerified}}=1)),1,0))',
             "1 when the kernel accepted a proof of the claim's current Lean statement here, or the claim is a kit result reported proved and its module (or theorem) is verified here."),
        AGG('KitLinkCount', '=COUNTIFS(ClaimLinks!{{Assertion}},{{AssertionId}})', 'Kit declarations linked to this claim.'),
        AGG('KitCoverCount', '=COUNTIFS(ClaimLinks!{{Assertion}},{{AssertionId}},ClaimLinks!{{Covers}},1)', 'Verified kit theorems that state this claim or more.'),
        AGG('KitContradictionCount', '=COUNTIFS(ClaimLinks!{{Assertion}},{{AssertionId}},ClaimLinks!{{Contradicts}},1)', 'Verified kit theorems that refute this claim. Must be 0 for a claim we hold.'),
        AGG('KitJointCount', '=COUNTIFS(ClaimLinks!{{Assertion}},{{AssertionId}},ClaimLinks!{{IsJoint}},1)', 'Kit theorems whose conjunction is this claim.'),
        AGG('KitJointVerifiedCount', '=COUNTIFS(ClaimLinks!{{Assertion}},{{AssertionId}},ClaimLinks!{{IsJointVerified}},1)', 'Of those, the verified ones.'),
        AGG('KitGlueProofCount', '=COUNTIFS(LeanProofs!{{Assertion}},{{AssertionId}},LeanProofs!{{Kind}},"claim",LeanProofs!{{IsKitGlue}},1)', 'Lean proofs of this claim that only restate kit theorems.'),
        CALC('IsKnownInKit', '=IF(OR({{KitCoverCount}}>0,AND({{KitJointCount}}>0,{{KitJointVerifiedCount}}={{KitJointCount}}),AND({{KitGlueProofCount}}>0,{{LeanCheckOk}}>0)),1,0)',
             '1 when the kit already proves this claim (a verified kit theorem says it or more, the jointly linked ones are all verified, or its Lean proof only restates the kit): not new against the catalog.'),
        CALC('IsKitContradicted', '=IF(AND({{KitContradictionCount}}>0,{{IsUsable}}=1),1,0)', '1 when a verified kit theorem refutes a claim the ledger holds (usable). A falsified claim the kit also refutes is agreement, not contradiction.'),
        CALC('IsLeanContradicted', '=IF(AND({{IsLeanVerified}}=1,OR({{ReportedStatus}}="FALSIFIED",{{PredicateIsRefuted}}=1)),1,0)', '1 when Lean proves a claim the model or the ledger refutes. Must be 0.'),
        CALC('IsLeanUnconfirmed', '=IF(AND({{ReportedStatus}}="LEAN_VERIFIED",{{IsLeanVerified}}=0),1,0)', '1 when a source reports the claim proved in Lean and the check here does not confirm it. Must be 0.'),
        CALC('ProofBasis', '=IF({{IsLeanVerified}}=1,"Lean",IF({{IsModelDecided}}=1,"Model","Report"))', 'What the status rests on: the Lean kernel, the model, or a report.', 'string'),
    ]:
        ensure_field(book, A, f)
    usable = ['DEFINITION', 'PROVED_HUMAN_READABLE', 'REDERIVED_KNOWN', 'LEAN_VERIFIED']

    def any_of(field, values):
        return 'OR(' + ','.join(f'{{{{{field}}}}}="{v}"' for v in values) + ')'
    formulas = {
        'EffectiveStatus': ('=IF(AND({{IsModelLinked}}=1,{{PredicateIsRefuted}}=1),"FALSIFIED",IF({{IsLeanVerified}}=1,"LEAN_VERIFIED",IF({{ReportedStatus}}="LEAN_VERIFIED","OPEN",'
                            'IF(AND({{IsModelLinked}}=1,{{PredicateIsVerified}}=1,OR({{ReportedStatus}}="OPEN",{{ReportedStatus}}="FINITE_VERIFIED")),"FINITE_VERIFIED",{{ReportedStatus}}))))',
                            'The status the ledger uses: FALSIFIED when the model holds a counterexample; LEAN_VERIFIED when the Lean kernel accepts a proof of the claim (or confirms a kit result); OPEN for a reported Lean result the check here does not confirm; FINITE_VERIFIED when the model decides an open or checked claim true; otherwise the reported status.', 'string'),
        'IsModelContradicted': (f'=IF(AND({{{{IsModelLinked}}}}=1,{{{{PredicateIsRefuted}}}}=1,{any_of("ReportedStatus", usable + ["FINITE_VERIFIED"])}),1,0)',
                                '1 when the report asserts the claim (proved, Lean-verified, checked or definitional) and the model refutes it: the report is wrong. An OPEN claim the model refutes is decided, not contradicted.', 'integer'),
        'StatusGroup': (f'=IF({any_of("EffectiveStatus", usable)},"Proved",IF({{{{EffectiveStatus}}}}="FINITE_VERIFIED","Checked",IF({{{{EffectiveStatus}}}}="FALSIFIED","Falsified",IF({{{{EffectiveStatus}}}}="SUPERSEDED","Superseded","Open"))))',
                        'Proved (definition, proved, rederived known or Lean-verified), Checked (finite verification only), Falsified, Superseded or Open.', 'string'),
        'IsUsable': (f'=IF({any_of("EffectiveStatus", usable + ["FINITE_VERIFIED"])},1,0)', '1 when the claim may be used as a premise.', 'integer'),
        'IsProofEligible': (f'=IF({any_of("EffectiveStatus", usable)},1,0)', '1 when the claim may be used in a proof (finite checks may not).', 'integer'),
    }
    for name, (formula, desc, dt) in formulas.items():
        ensure_field(book, A, F(name, dt, 'calculated', cached(name, formula), desc=desc))
        ensure_field(book, A, F(f'{name}Cache', dt, desc=f'Cached {name} from the last fresh compile; read by {name} while {lt.CACHE_FLAG} = 1.'))
    D = 'Dashboards'
    for f in [
        AGG('UnmodeledClaimCount', '=COUNTIFS(Assertions!{{IsFormallyStated}},0)', 'Claims still only stated in words (no term tree, no Lean form).'),
        AGG('OwnClaimCount', '=COUNTIFS(Assertions!{{IsOwnClaim}},1)', "This ledger's own claims."),
        AGG('KitClaimCount', '=COUNTIFS(Assertions!{{IsOwnClaim}},0)', "Claims from the kit: its modules, its cases and its open statements."),
        AGG('LeanVerifiedCount', '=COUNTIFS(Assertions!{{EffectiveStatus}},"LEAN_VERIFIED")', 'Claims the Lean kernel verifies.'),
        AGG('OwnLeanVerifiedCount', '=COUNTIFS(Assertions!{{IsOwnClaim}},1,Assertions!{{EffectiveStatus}},"LEAN_VERIFIED")', 'Our claims with a kernel-checked Lean proof.'),
        AGG('OwnLeanExpressibleCount', '=COUNTIFS(Assertions!{{IsOwnClaim}},1,Assertions!{{IsLeanExpressible}},1)', 'Our claims the build writes in Lean.'),
        AGG('OwnKnownInKitCount', '=COUNTIFS(Assertions!{{IsOwnClaim}},1,Assertions!{{IsKnownInKit}},1)', 'Our claims the kit already proves.'),
        AGG('KitModuleCount', '=COUNTIFS(LeanModules!{{Source}},"kit")', 'Kit modules synced.'),
        AGG('KitDeclarationCount', '=COUNTIFS(LeanDeclarations!{{BadAxiomCount}},">=0")', 'Lean declarations in the model (kit and submissions).'),
        AGG('KitUnverifiedModuleCount', '=COUNTIFS(LeanModules!{{IsVerified}},0)', 'Modules with a declaration on a non-standard axiom. Must be 0.'),
        AGG('SubmissionCount', '=COUNTIFS(Submissions!{{Problem}},">=1")', 'Public submissions.'),
        AGG('SubmissionLeanVerifiedCount', '=COUNTIFS(Submissions!{{Status}},"Lean Verified")', 'Submissions the verifier accepted.'),
        AGG('SubmissionDisagreementCount', '=COUNTIFS(Submissions!{{AgreesWithVerifier}},0)', 'Submissions where our check and the verifier disagree (often a different kit commit).'),
        AGG('LeanContradictionCount', '=COUNTIFS(Assertions!{{IsLeanContradicted}},1)', 'Claims Lean proves although the model or the ledger refutes them. Must be 0.'),
        AGG('LeanUnconfirmedCount', '=COUNTIFS(Assertions!{{IsLeanUnconfirmed}},1)', 'Reported Lean results the check here does not confirm. Must be 0.'),
        AGG('KitContradictionCount', '=COUNTIFS(Assertions!{{IsKitContradicted}},1)', 'Claims we hold that a verified kit theorem refutes. Must be 0.'),
        AGG('KitAgreementCount', '=COUNTIFS(Assertions!{{IsOwnClaim}},1,Assertions!{{KitContradictionCount}},">0",Assertions!{{StatusGroup}},"Falsified")', 'Claims we falsified that a kit theorem refutes too.'),
        AGG('OfficialAlignmentCount', '=SUMIFS(Assertions!{{IsOfficiallyAligned}},Assertions!{{Kind}},"Prize problem")', 'Prize problems whose formal statement Lean proves equivalent to the official one.'),
    ]:
        ensure_field(book, D, f)


def main():
    book = lt.load()
    stats = apply(book)
    lt.save(book)
    print(stats)


if __name__ == '__main__':
    main()
