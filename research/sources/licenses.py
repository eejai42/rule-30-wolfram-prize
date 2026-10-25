"""Every external source this repo references, its license, and how much of it may be kept here.

The rule (owner, 2026-10-25): include as much of an external work as its license allows, with its credit and
license cited. A work whose license allows redistribution may be copied in (its text, its proofs); a work
with no license, or one that reserves its rights, is only referenced: its URL, its authors, its version
and hash, and the RESULTS about it (what our checks or the verifier said, names, counts). Whoever runs the
checks downloads such a work into external/ (gitignored) and validates it there.

research/sources/sync.py reads ALLOWS to decide what each snapshot keeps; build_challenge.py loads both
tables (Licenses, ChallengeSources) into the rulebook.
"""

# LicenseId -> (title, url, allows redistribution here)
LICENSES = {
    'none': ('No license stated: all rights reserved by the authors', '', 0),
    'all-rights-reserved': ('All rights reserved', '', 0),
    'Apache-2.0': ('Apache License 2.0', 'https://www.apache.org/licenses/LICENSE-2.0', 1),
    'MIT': ('MIT License', 'https://opensource.org/licenses/MIT', 1),
    'CC-BY-4.0': ('Creative Commons Attribution 4.0', 'https://creativecommons.org/licenses/by/4.0/', 1),
    'unrecognized': ('A license file GitHub does not recognize: read it before copying anything', '', 0),
    'MIT+Commons-Clause': ('MIT License with the Commons Clause (no selling of products or services built on it)',
                           'https://github.com/EffortlessAPI/effortless-skills/blob/main/LICENSE', 1),
}
ALLOWS = {k: v[2] for k, v in LICENSES.items()}

# The external sources: (id, title, url, role, license, what this repo keeps of it, credit, is official prize material)
SOURCES = [
    ('kit', 'Rule 30 Prize kit (reference Lean environment)', 'https://github.com/WolframInstitute/Rule30PrizeKit',
     'The official statements, the catalog of partial results and the equivalent forms, in Lean.', 'none',
     'References and results only: module and declaration names, kinds, lines, imports and uses, file hashes, and the axioms '
     'and verdicts our checks found. No source, statement or docstring. sync.py checks the kit out into external/.',
     'Wolfram Institute and the contributors named in its lean/README.md', 1),
    ('verifier', "The verifier's environment", 'https://www.wolframcloud.com/obj/rule-30-prize/Agents/api/environment',
     'The kit commit, Lean and Mathlib versions a submission is checked against, and the modules it may import.', 'none',
     'Its facts (commits, versions, module names), as served.', 'Wolfram Research', 1),
    ('submissions', 'Rule 30 Prize submissions', 'https://www.wolframcloud.com/obj/rule-30-prize/Agents/submissions.json',
     "Every public submission: its claim, headline theorems, the verifier's status and the reviewers' tags.", 'none',
     'Per submission: id, title, authors, agent, dates, status, tags, headline theorem names, kit modules, links, and our own '
     're-check verdict. No abstract and no Lean source: sync.py downloads the sources into external/ to re-check them.',
     'Each submission\'s authors, as listed on it', 1),
    ('skill', 'The Rule 30 Prize, for AI agents (skill.md)', 'https://www.wolframcloud.com/obj/rule-30-prize/Agents/skill.md',
     'The official instructions for agents: setup, ground rules, what is known, how to prove and submit.', 'none',
     'Its version, retrieval time and hash only.', 'Wolfram Research', 1),
    ('announcement', 'Announcing the Rule 30 Prizes (Wolfram, 2019)', 'https://writings.stephenwolfram.com/2019/10/announcing-the-rule-30-prizes/',
     'The three problems in words, and the prize rules (https://rule30prize.org/).', 'all-rights-reserved',
     'A link.', 'Stephen Wolfram', 1),
    ('lean4', 'Lean 4', 'https://github.com/leanprover/lean4', 'The prover; the kit pins v4.35.0.', 'Apache-2.0',
     'Not copied: elan installs it.', 'The Lean FRO and contributors', 0),
    ('mathlib', 'Mathlib', 'https://github.com/leanprover-community/mathlib4', 'The kit\'s equivalent forms and our ledger import it.', 'Apache-2.0',
     'Not copied: the kit fetches it (lake exe cache get).', 'The Mathlib community', 0),
    ('formal-conjectures', 'Formal Conjectures (Google DeepMind)', 'https://github.com/google-deepmind/formal-conjectures',
     "Its Rule30.lean states Problems 1 and 2; the kit's official statements match it.", 'Apache-2.0', 'A link.', 'Google DeepMind and contributors', 0),
    ('effortless-skills', 'Effortless skills', 'https://github.com/EffortlessAPI/effortless-skills',
     'The Claude Code skills for Effortless Rulebook projects.', 'MIT+Commons-Clause',
     'Included in full under .claude/skills/, with its LICENSE.', 'EffortlessAPI', 0),
    ('cmcc-paper', 'The Conceptual Model Completeness Conjecture (CMCC) as a Universal Computational Framework', 'https://doi.org/10.5281/zenodo.14760293',
     'The framework this ledger is built on (research v05 used sections 2, 3, 4 and 6).', 'CC-BY-4.0',
     'Included with credit: bootstrap/cmcc_rule30_effortless_migration/research_v05/sources/cmcc-foundations.pdf (and its text).', 'EJ Alexandra', 0),
    ('brcc-paper', 'The Business Rule Completeness Conjecture (BRCC) and Its Proof Sketch', 'https://doi.org/10.5281/zenodo.14759299',
     'Background for the rulebook method.', 'CC-BY-4.0',
     'Included with credit: bootstrap/cmcc_rule30_effortless_migration/research_v05/sources/brcc-proof.pdf (and its text).', 'EJ Alexandra', 0),
    ('cmcc-repo', 'CMCC repository', 'https://github.com/eejai42/conceptual-model-completeness-conjecture-toe-meta-model',
     'Where the CMCC sources are indexed.', 'unrecognized', 'A link.', 'EJ Alexandra', 0),
    ('effortless-rulebooks', 'Effortless rulebooks (examples)', 'https://github.com/EffortlessAPI/effortless-rulebooks',
     'The simpsons-paradox and effortless-math examples this model follows.', 'none', 'Links.', 'EffortlessAPI', 0),
    ('rule30prize-org', 'Rule 30 Prizes (official rules)', 'https://rule30prize.org/', 'The prize statements, the full-proof requirement and the rules.',
     'all-rights-reserved', 'A link.', 'Wolfram Foundation', 1),
    ('ruliad-essay', 'The Concept of the Ruliad (Wolfram, 2021)', 'https://writings.stephenwolfram.com/2021/11/the-concept-of-the-ruliad/',
     'Conceptual context consulted by research v05.', 'all-rights-reserved', 'A link.', 'Stephen Wolfram', 0),
    ('rule30-lab', 'rule30-lab (wryan2986)', 'https://github.com/wryan2986/rule30-lab',
     'Another public effort on the prize problems (computational tools; no proof of a prize problem).', 'MIT',
     'A link; nothing is copied yet. Its license would allow including it with credit.', 'wryan2986', 0),
]


def notice() -> str:
    """NOTICE.md: every external source, its license, and what this repo keeps of it."""
    out = ['# Third-party sources and licenses', '',
           'GENERATED by `python3 research/sources/licenses.py` from research/sources/licenses.py. Do not edit.', '',
           'This repo keeps of each external work only what its license allows. Works that state no license, or that',
           'reserve their rights, are referenced, not copied: their links, authors, versions and hashes, and the results',
           "of checking them. `research/sources/sync.py` downloads them into `external/` (gitignored) for whoever runs",
           'the checks, and validating them is up to that person.', '',
           '| Source | License | Credit | Kept here |', '|---|---|---|---|']
    for sid, title, url, role, lic, kept, credit, official in SOURCES:
        name, lurl, _ = LICENSES[lic]
        out.append(f'| [{title}]({url}) | {f"[{lic}]({lurl})" if lurl else name} | {credit} | {kept} |')
    out += ['', 'Each public submission to the Rule 30 Prize is listed in the model (table `Submissions`) with its authors, links',
            'and the license its Lean source declares; none declared one when last synced, so none is copied here.', '']
    return '\n'.join(out)


if __name__ == '__main__':
    from pathlib import Path
    (Path(__file__).resolve().parents[2] / 'NOTICE.md').write_text(notice())
    print('wrote NOTICE.md')
