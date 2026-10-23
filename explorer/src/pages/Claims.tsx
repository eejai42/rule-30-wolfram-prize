import { useMemo } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { byId, num, useRows, type Row } from '../data';
import { CardLink, ClaimLink, D, Group, Section, fileHref, proofLink, useFlash } from '../ui';

const KINDS = ['Prize problem', 'Bridge obligation', 'Theorem', 'Known result', 'Definition', 'Finite check', 'Hypothesis'];
const GROUPS = ['Proved', 'Checked', 'Open', 'Falsified', 'Superseded'];

function ClaimCard({ a, counts }: { a: Row; counts?: Row }) {
  const flash = useFlash('Assessments', a.assessment_id);
  return (
    <CardLink to={`/claims/${encodeURIComponent(a.assessment_id)}`} className={`card claim-card${flash}`}>
      <div className="card-top">
        <span className="claim-id">{a.assessment_id}</span>
        <span className="kind">{a.kind}</span>
        <Group value={a.status_group} f="Assessments.StatusGroup" />
        {num(a.is_at_risk) === 1 && <D f="Assessments.IsAtRisk" className="pill g-falsified">at risk</D>}
      </div>
      <p className="statement">{a.statement}</p>
      {counts && (
        <div className="counts">
          <span><D f="Assertions.PremiseCount">{num(counts.premise_count)}</D> premises</span>
          <span><D f="Assertions.DependentCount">{num(counts.dependent_count)}</D> dependents</span>
          <span><D f="Assertions.EvidenceCount">{num(counts.evidence_count)}</D> evidence</span>
        </div>
      )}
    </CardLink>
  );
}

export function ClaimsPage() {
  const [params, setParams] = useSearchParams();
  const kind = params.get('kind') ?? '';
  const group = params.get('group') ?? '';
  const q = (params.get('q') ?? '').toLowerCase();
  const assessments = useRows('Assessments');
  const assertions = useRows('Assertions');
  const set = (k: string, v: string) => {
    const next = new URLSearchParams(params);
    if (v) next.set(k, v); else next.delete(k);
    setParams(next, { replace: true });
  };
  const rows = useMemo(() => assessments
    .filter((a) => (!kind || a.kind === kind) && (!group || a.status_group === group))
    .filter((a) => !q || `${a.assessment_id} ${a.statement}`.toLowerCase().includes(q))
    .sort((x, y) => KINDS.indexOf(x.kind) - KINDS.indexOf(y.kind)), [assessments, kind, group, q]);

  return (
    <div className="page">
      <h1>Claims</h1>
      <input className="search" placeholder="Search id or statement" value={params.get('q') ?? ''} onChange={(e) => set('q', e.target.value)} />
      <div className="chips">
        <button className={!group ? 'chip on' : 'chip'} onClick={() => set('group', '')}>Any status</button>
        {GROUPS.map((g) => <button key={g} className={group === g ? 'chip on' : 'chip'} onClick={() => set('group', group === g ? '' : g)}>{g}</button>)}
      </div>
      <div className="chips">
        <button className={!kind ? 'chip on' : 'chip'} onClick={() => set('kind', '')}>Any kind</button>
        {KINDS.map((k) => <button key={k} className={kind === k ? 'chip on' : 'chip'} onClick={() => set('kind', kind === k ? '' : k)}>{k}</button>)}
      </div>
      <p className="muted small">{rows.length} of {assessments.length} claims</p>
      <div className="grid">{rows.map((a) => <ClaimCard key={a.assessment_id} a={a} counts={byId(assertions, 'assertion_id', a.assessment_id)} />)}</div>
    </div>
  );
}

export function ClaimPage() {
  const { id = '' } = useParams();
  const a = byId(useRows('Assertions'), 'assertion_id', id);
  const s = byId(useRows('Assessments'), 'assessment_id', id);
  const assessments = useRows('Assessments');
  const deps = useRows('Dependencies');
  const premises = deps.filter((d) => d.conclusion === id);
  const dependents = deps.filter((d) => d.premise === id);
  const blockers = useRows('Prerequisites').filter((p) => p.conclusion_key === id && num(p.is_blocking_ancestor) === 1);
  const evidence = useRows('EvidenceLinks').filter((e) => e.assertion === id);
  const revisions = useRows('Revisions').filter((r) => r.assertion === id);
  const flash = useFlash('Assessments', id);
  if (!a || !s) return <p className="muted">Loading…</p>;
  const proof = proofLink(a.proof_section);
  const mini = (cid: string) => {
    const c = byId(assessments, 'assessment_id', cid);
    return (
      <li key={cid}>
        <ClaimLink id={cid} /> {c && <Group value={c.status_group} f="Assessments.StatusGroup" />}
        <div className="muted">{c?.statement}</div>
      </li>
    );
  };

  return (
    <div className="page">
      <Link to="/claims" className="back">← Claims</Link>
      <div className={`card claim-hero${flash}`}>
        <div className="card-top">
          <h1>{a.assertion_id}</h1>
          <span className="kind">{a.kind}</span>
          <Group value={s.status_group} f="Assessments.StatusGroup" />
        </div>
        <p className="statement big">{a.statement}</p>
        <dl className="kv">
          <dt>Reported</dt><dd className="mono">{a.reported_status}</dd>
          <dt>Compiled</dt><dd className="mono"><D f="Assessments.CurrentStatus">{s.current_status}</D></dd>
          <dt>Usable as premise</dt><dd><D f="Assertions.IsUsable">{num(a.is_usable) ? 'yes' : 'no'}</D></dd>
          <dt>Proof-eligible</dt><dd><D f="Assessments.ProofEligible">{num(s.proof_eligible) ? 'yes' : 'no'}</D></dd>
          <dt>Blocking ancestors</dt><dd><D f="Assessments.AncestorBlockedCount">{num(s.ancestor_blocked_count)}</D></dd>
          {num(s.is_at_risk) === 1 && <><dt>At risk</dt><dd><D f="Assessments.IsAtRisk" className="pill g-falsified">rests on an unestablished claim</D></dd></>}
          <dt>Added in</dt><dd>{a.introduced_in_loop ? <Link to={`/loops/${a.introduced_in_loop}`}>{a.introduced_in_loop}</Link> : <span className="muted">research v05</span>}</dd>
          <dt>Proof</dt><dd>{proof ? <Link to={fileHref(proof.path, proof.anchor)}>{proof.label}</Link> : <span className="muted">none (not a proved claim)</span>}</dd>
        </dl>
      </div>

      {blockers.length > 0 && (
        <Section title="Blocked by">
          <ul className="list">{blockers.map((p) => mini(p.premise))}</ul>
        </Section>
      )}
      <Section title={`Premises (${num(a.premise_count)})`}>
        {premises.length ? <ul className="list">{premises.map((d) => mini(d.premise))}</ul> : <p className="muted">None. This is a root of the dependency graph.</p>}
      </Section>
      <Section title={`Used by (${num(a.dependent_count)})`}>
        {dependents.length ? <ul className="list">{dependents.map((d) => mini(d.conclusion))}</ul> : <p className="muted">Nothing depends on this yet.</p>}
      </Section>
      <Section title={`Evidence (${num(a.evidence_count)})`}>
        {evidence.length ? (
          <ul className="list">
            {evidence.map((e) => (
              <li key={e.evidence_link_id}>
                <span className="claim-id">{e.evidence}</span> <Link to={fileHref(e.evidence_path)}><D f="EvidenceLinks.EvidencePath" className="mono small">{e.evidence_path}</D></Link>
              </li>
            ))}
          </ul>
        ) : <p className="muted">No linked files.</p>}
      </Section>
      <Section title={`History (${num(a.revision_count)})`}>
        {revisions.length ? (
          <ul className="list">
            {revisions.map((r) => (
              <li key={r.revision_id}>
                <span className="mono">{r.prior_status}</span> → <span className="mono">{r.new_status}</span>
                {r.loop && <> in <Link to={`/loops/${r.loop}`}>{r.loop}</Link></>}
                <div className="muted">{r.reason}</div>
              </li>
            ))}
          </ul>
        ) : <p className="muted">No status changes recorded.</p>}
      </Section>
      <p><Link to={`/graph?focus=${encodeURIComponent(id)}`}>Show in graph →</Link></p>
    </div>
  );
}
