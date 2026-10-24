import { useMemo } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { byId, num, useRows, type Row } from '../data';
import { CardLink, ClaimLink, D, Group, LoopState, Section, fileHref, proofLink, useFlash } from '../ui';

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

function ModelSection({ a }: { a: Row }) {
  const pred = byId(useRows('Predicates'), 'predicate_id', a.predicate);
  const insts = useRows('PredicateInstances').filter((i) => i.predicate === a.predicate);
  const step = useRows('StrategySteps').find((s) => s.assertion === a.assertion_id && num(s.strategy_is_current) === 1);
  return (
    <>
      {step && (
        <Section title="On the current path to P1">
          <div className="card">
            <div className="card-top"><span className="path-role">{step.role}</span> {num(step.blocks_goal) === 1 && <D f="StrategySteps.BlocksGoal" className="pill g-open">blocking the goal</D>}</div>
            <p className="statement">{step.note}</p>
            <Link to="/">See the whole path →</Link>
          </div>
        </Section>
      )}
      <Section title="In the model">
        {!pred ? <p className="muted">Not linked to a modeled predicate.</p> : (
          <div className="card">
            <div className="card-top"><span className="claim-id">{pred.predicate_id}</span> <span className="kind">{pred.problem}</span></div>
            <p className="statement">{pred.statement}</p>
            <pre className="formal"><D f="Predicates.Formal">{pred.formal}</D></pre>
            <dl className="kv">
              <dt>Model verdict</dt><dd><D f="Predicates.FiniteVerdict" className="mono">{pred.finite_verdict}</D></dd>
              <dt>Decided by the model</dt><dd><D f="Assertions.IsModelDecided">{num(a.is_model_decided) ? 'yes: the build sets the status' : 'no: the status is a report'}</D></dd>
              <dt>Ledger status</dt><dd><D f="Assertions.EffectiveStatus" className="mono">{a.effective_status}</D></dd>
              {num(a.is_model_contradicted) === 1 && <><dt>Contradiction</dt><dd><D f="Assertions.IsModelContradicted" className="pill g-falsified">the model disagrees with the reported status</D></dd></>}
              <dt>Quantifiers</dt><dd><D f="Predicates.QuantifierCount">{num(pred.quantifier_count)}</D>, <D f="Predicates.UnboundedQuantifierCount">{num(pred.unbounded_quantifier_count)}</D> over infinite domains</dd>
              <dt>Computable from the model</dt><dd><D f="Predicates.IsComputable">{num(pred.is_computable) ? 'yes' : `no: ${num(pred.unmodeled_operator_count)} operator(s) not modeled yet`}</D></dd>
              <dt>Finitely decidable</dt><dd><D f="Predicates.IsFinitelyDecidable">{num(pred.is_finitely_decidable) ? 'yes' : 'no: only bounded instances can be checked'}</D></dd>
              <dt>Instances</dt><dd><D f="Predicates.InstanceCount">{num(pred.instance_count)}</D> in domain, <D f="Predicates.HoldingCount">{num(pred.holding_count)}</D> hold, <D f="Predicates.FailingCount">{num(pred.failing_count)}</D> fail</dd>
            </dl>
            {pred.instance_meaning && <p className="muted small">One instance: {pred.instance_meaning}</p>}
            {insts.length > 0 && (
              <details>
                <summary>{insts.length} instance rows</summary>
                <ul className="list inst-list">
                  {insts.slice(0, 200).map((i) => (
                    <li key={i.predicate_instance_id}>
                      <span className="mono small">{i.predicate_instance_id}</span>{' '}
                      <D f="PredicateInstances.Holds" className={`pill ${num(i.holds) ? 'g-proved' : 'g-falsified'}`}>{num(i.holds) ? 'holds' : 'fails'}</D>
                      {num(i.in_domain) === 0 && <span className="muted small"> outside the domain</span>}
                      {i.witness !== null && i.witness !== undefined && i.witness !== '' && <span className="muted small"> witness <D f="PredicateInstances.Witness">{String(i.witness)}</D></span>}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}
      </Section>
    </>
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
  const loopLinks = useRows('LoopTargets').filter((t) => t.assertion === id);
  const loops = useRows('Loops');
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

      <ModelSection a={a} />
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
      {loopLinks.length > 0 && (
        <Section title={`Loops (${num(a.loop_target_count)})`}>
          <ul className="list">
            {loopLinks.map((t) => {
              const l = byId(loops, 'loop_id', t.loop);
              return (
                <li key={t.loop_target_id}>
                  <Link to={`/loops/${t.loop}`}>{t.loop}</Link> {l && <LoopState row={l} />} <span className="path-role">{t.role}</span>
                  <div className="muted">{t.note}</div>
                </li>
              );
            })}
          </ul>
        </Section>
      )}
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
