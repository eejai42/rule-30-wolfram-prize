import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { byId, num, useRows, useTable, type Row } from '../data';
import { ClaimLink, D, Group, Section, Tile } from '../ui';

const short = (sha: string | null | undefined) => (sha ? String(sha).slice(0, 10) : '');

function ProblemCard({ id }: { id: string }) {
  const a = byId(useRows('Assertions'), 'assertion_id', id);
  const s = byId(useRows('Assessments'), 'assessment_id', id);
  if (!a || !s) return null;
  return (
    <div className="card prize">
      <div className="card-top">
        <ClaimLink id={id} /> <Group value={s.status_group} f="Assessments.StatusGroup" />
        {num(a.is_officially_aligned) === 1 && <D f="Assertions.IsOfficiallyAligned" className="pill g-proved">matches the official statement in Lean</D>}
      </div>
      <p className="statement">{a.statement}</p>
      {a.lean_declaration_definition ? (
        <>
          <div className="eyebrow">Official Lean statement (kit)</div>
          <pre className="formal"><D f="Assertions.LeanDeclarationDefinition">{a.lean_declaration}{' := '}{a.lean_declaration_definition}</D></pre>
        </>
      ) : <p className="muted small">No official Lean statement: Problem 3 needs a model of computation (the kit has a reference one, Rule30Problem3).</p>}
      {a.lean_statement && (
        <>
          <div className="eyebrow">Ours, written by the build from the term tree</div>
          <pre className="formal"><D f="Assertions.LeanStatement">{a.lean_statement}</D></pre>
        </>
      )}
    </div>
  );
}

function CaseRow({ a }: { a: Row }) {
  const deps = useRows('Dependencies').filter((d) => d.conclusion === a.assessment_id && String(d.premise).startsWith('Q-'));
  return (
    <li>
      <ClaimLink id={a.assessment_id} /> <Group value={a.status_group} f="Assessments.StatusGroup" />
      <div>{a.statement}</div>
      {deps.length > 0 && <div className="muted small">waits on {deps.map((d) => <span key={d.dependency_id}><ClaimLink id={d.premise} /> </span>)}</div>}
    </li>
  );
}

function Sources() {
  const sources = useTable('ChallengeSources');
  const syncs = useTable('SourceSyncs');
  const last = [...syncs].sort((x, y) => String(y.retrieved_at).localeCompare(String(x.retrieved_at)))[0];
  return (
    <Section title="What this model is measured against" right={last ? <span className="muted small">last synced {last.retrieved_at}</span> : null}>
      <ul className="list">
        {sources.map((s) => (
          <li key={s.challenge_source_id}>
            <a href={s.url} target="_blank" rel="noreferrer"><b>{s.title}</b></a> <span className="mono small">{s.challenge_source_id === 'kit' || s.challenge_source_id === 'verifier' ? short(s.version) : s.version}</span>
            <div className="muted small">{s.role}</div>
          </li>
        ))}
      </ul>
      <p className="muted small">Sync with <code>./start.sh sync</code>: it fetches every source, builds and exports the kit, and re-checks every submission's Lean source here.</p>
    </Section>
  );
}

function Ours() {
  const assertions = useRows('Assertions');
  const assessments = useRows('Assessments');
  const own = assertions.filter((a) => num(a.is_own_claim) === 1 && (num(a.is_lean_expressible) === 1 || num(a.kit_link_count) > 0));
  const checks = useTable('LeanChecks');
  return (
    <Section title="Our claims, against Lean and the kit">
      <ul className="list">
        {own.sort((x, y) => num(y.is_lean_verified) - num(x.is_lean_verified) || num(x.is_known_in_kit) - num(y.is_known_in_kit)).map((a) => {
          const s = byId(assessments, 'assessment_id', a.assertion_id);
          const ck = checks.find((c) => c.assertion === a.assertion_id && c.kind === 'claim');
          return (
            <li key={a.assertion_id}>
              <ClaimLink id={a.assertion_id} /> {s && <Group value={s.status_group} f="Assessments.StatusGroup" />}{' '}
              <D f="Assertions.ProofBasis" className="mono small">{a.proof_basis}</D>{' '}
              {num(a.is_known_in_kit) === 1 ? <D f="Assertions.IsKnownInKit" className="pill g-superseded">known in the kit</D>
                : num(a.is_lean_verified) === 1 ? <span className="pill g-proved">not in the kit</span> : null}
              {ck && num(ck.ok) === 0 && <span className="muted small"> · Lean: {ck.problems}</span>}
              <div className="muted small">{a.statement}</div>
            </li>
          );
        })}
      </ul>
    </Section>
  );
}

function Catalog() {
  const mods = useTable('LeanModules', 60000);
  const [q, setQ] = useState('');
  const [pkg, setPkg] = useState('Ruliology');
  const rows = useMemo(() => mods.filter((m) => m.package === pkg && num(m.is_certificate_data) === 0)
    .filter((m) => !q || `${m.short_name} ${m.title} ${m.credit}`.toLowerCase().includes(q.toLowerCase()))
    .sort((x, y) => String(y.added_on).localeCompare(String(x.added_on)) || String(x.short_name).localeCompare(String(y.short_name))), [mods, q, pkg]);
  return (
    <Section title="The catalog" right={<span className="muted small">{rows.length} modules</span>}>
      <div className="chips">
        {['Ruliology', 'Rule30Equivalents', 'Submission'].map((p) => <button key={p} className={pkg === p ? 'chip on' : 'chip'} onClick={() => setPkg(p)}>{p === 'Ruliology' ? 'Partial results' : p === 'Rule30Equivalents' ? 'Equivalent forms' : 'Submissions (compiled here)'}</button>)}
      </div>
      <input className="search" placeholder="Search module, title or credit" value={q} onChange={(e) => setQ(e.target.value)} />
      <ul className="list">
        {rows.map((m) => (
          <li key={m.lean_module_id}>
            <a href={m.url} target="_blank" rel="noreferrer" className="mono">{m.short_name}</a>{' '}
            <D f="LeanModules.IsVerified" className={`pill ${num(m.is_verified) ? 'g-proved' : 'g-falsified'}`}>{num(m.is_verified) ? 'verified' : 'unverified'}</D>{' '}
            <span className="muted small"><D f="LeanModules.TheoremCount">{num(m.theorem_count)}</D> theorems{num(m.is_in_verifier) ? '' : ' · not yet in the verifier'}{m.added_on ? ` · added ${m.added_on}` : ''}</span>
            <div>{m.title}</div>
            {m.credit && <div className="muted small">{m.credit}</div>}
          </li>
        ))}
      </ul>
    </Section>
  );
}

function Submissions() {
  const subs = useTable('Submissions');
  const rows = [...subs].sort((x, y) => String(y.submitted).localeCompare(String(x.submitted)));
  return (
    <Section title="Submissions" right={<a href="https://www.wolframcloud.com/obj/rule-30-prize/Agents/submissions" target="_blank" rel="noreferrer">submissions page ↗</a>}>
      <ul className="list">
        {rows.map((s) => (
          <li key={s.submission_id}>
            <a href={s.page_url} target="_blank" rel="noreferrer"><b>{s.title}</b></a>{' '}
            <span className={`pill ${s.status === 'Lean Verified' ? 'g-proved' : 'g-open'}`}>{s.status}</span>{' '}
            {num(s.is_human_verified) === 1 && <span className="pill g-proved">Human Verified</span>}{' '}
            {num(s.is_kit_contribution) === 1 && <span className="pill g-checked">Kit Contribution</span>}{' '}
            {num(s.is_prize_claimed) === 1 && <span className="pill running">Prize Claimed</span>}
            <div className="muted small">P{s.problem} · {s.claim} · {s.authors} · {String(s.submitted).slice(0, 10)} · here: <D f="Submissions.OurVerdict" className="mono">{s.our_verdict}</D>
              {num(s.agrees_with_verifier) === 0 && <D f="Submissions.AgreesWithVerifier" className="pill g-open">differs from the verifier</D>}</div>
          </li>
        ))}
      </ul>
    </Section>
  );
}

/** The challenge itself: the official problems, the sources, the kit's frontier, our claims against it. */
export default function Challenge() {
  const dash = useRows('Dashboards')[0];
  const assessments = useRows('Assessments');
  const cases = assessments.filter((a) => a.kind === 'Kit case').sort((x, y) => String(x.assessment_id).localeCompare(String(y.assessment_id), undefined, { numeric: true }));
  if (!dash) return <p className="muted">Loading…</p>;
  const zeros = num(dash.kit_contradiction_count) + num(dash.lean_contradiction_count) + num(dash.lean_unconfirmed_count) + num(dash.kit_unverified_module_count);
  return (
    <div className="page">
      <h1>The Rule 30 Prize</h1>
      <p className="muted">Three problems about the center column of rule 30, $10,000 each. The prize is graded in Lean: a submission's headline theorem must have the official type and use only standard axioms. Everything below is read from the model.</p>
      <div className="grid">{['P1', 'P2', 'P3'].map((id) => <ProblemCard key={id} id={id} />)}</div>

      <div className="tiles">
        <Tile label="Kit modules" value={num(dash.kit_module_count)} f="Dashboards.KitModuleCount" />
        <Tile label="Lean declarations" value={num(dash.kit_declaration_count)} f="Dashboards.KitDeclarationCount" />
        <Tile label="Submissions" value={num(dash.submission_count)} f="Dashboards.SubmissionCount" />
        <Tile label="Ours verified in Lean" value={num(dash.own_lean_verified_count)} f="Dashboards.OwnLeanVerifiedCount" tone="g-proved" />
        <Tile label="Ours known in the kit" value={num(dash.own_known_in_kit_count)} f="Dashboards.OwnKnownInKitCount" tone="g-superseded" />
        <Tile label="Ours written in Lean" value={num(dash.own_lean_expressible_count)} f="Dashboards.OwnLeanExpressibleCount" />
      </div>
      <div className={`banner ${zeros === 0 ? 'ok-banner' : 'warn-banner'}`}>
        {zeros === 0 ? 'Consistent with the kit: ' : 'Check the consolidation: '}
        <D f="Dashboards.KitContradictionCount">{num(dash.kit_contradiction_count)}</D> kit theorems refute a claim of ours,{' '}
        <D f="Dashboards.LeanContradictionCount">{num(dash.lean_contradiction_count)}</D> Lean proofs of refuted claims,{' '}
        <D f="Dashboards.LeanUnconfirmedCount">{num(dash.lean_unconfirmed_count)}</D> reported Lean results not confirmed here,{' '}
        <D f="Dashboards.KitUnverifiedModuleCount">{num(dash.kit_unverified_module_count)}</D> modules on a non-standard axiom.
      </div>

      <Section title="Problem 1, case by case (the kit's split)" right={<ClaimLink id="B10">the route: B10</ClaimLink>}>
        <ul className="list">{cases.map((a) => <CaseRow key={a.assessment_id} a={a} />)}</ul>
      </Section>
      <Ours />
      <Sources />
      <Submissions />
      <Catalog />
      <p className="muted small">The plan in force is on the <Link to="/">progress page</Link>.</p>
    </div>
  );
}
