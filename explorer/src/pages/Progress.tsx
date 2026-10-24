import { Link } from 'react-router-dom';
import { num, useRows, byId, type Row } from '../data';
import { CardLink, ClaimLink, D, Group, LoopState, Section, Tile, useFlash } from '../ui';
import PathHero from './PathHero';

function PrizeCard({ a }: { a: Row }) {
  const prereqs = useRows('Prerequisites');
  const assessments = useRows('Assessments');
  const blockers = prereqs.filter((p) => p.conclusion_key === a.assessment_id && num(p.is_blocking_ancestor) === 1);
  const flash = useFlash('Assessments', a.assessment_id);
  return (
    <div className={`card prize${flash}`}>
      <div className="card-top">
        <ClaimLink id={a.assessment_id} />
        <Group value={a.status_group} f="Assessments.StatusGroup" />
      </div>
      <p className="statement">{a.statement}</p>
      <div className="meta">
        Waiting on <D f="Assessments.AncestorBlockedCount"><b>{num(a.ancestor_blocked_count)}</b></D> open ancestor{num(a.ancestor_blocked_count) === 1 ? '' : 's'}
      </div>
      {blockers.length > 0 && (
        <ul className="blockers">
          {blockers.map((p) => {
            const b = byId(assessments, 'assessment_id', p.premise);
            return (
              <li key={p.prerequisite_id}>
                <ClaimLink id={p.premise} /> <span className="muted">{b?.statement}</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function LoopRow({ l }: { l: Row }) {
  const flash = useFlash('Loops', l.loop_id);
  return (
    <CardLink to={`/loops/${l.loop_id}`} className={`card loop-card${l.state === 'RUNNING' ? ' is-running' : ''}${flash}`}>
      <div className="card-top">
        <b>{l.name}</b>
        <LoopState row={l} />
      </div>
      <p className="statement">{l.hypothesis}</p>
      {l.kind === 'EFFORTLESS' && (
        <div className="counts">
          <span><D f="Loops.ClaimsAdded">{num(l.claims_added)}</D> added</span>
          <span><D f="Loops.ProofsMade">{num(l.proofs_made)}</D> proved</span>
          <span><D f="Loops.FalsificationsMade">{num(l.falsifications_made)}</D> falsified</span>
        </div>
      )}
    </CardLink>
  );
}

export default function Progress() {
  const dash = useRows('Dashboards')[0];
  const assessments = useRows('Assessments');
  const loops = useRows('Loops');
  if (!dash) return <p className="muted">Loading…</p>;
  const prize = assessments.filter((a) => a.kind === 'Prize problem');
  const running = loops.filter((l) => l.state === 'RUNNING');
  const recent = [...loops].sort((x, y) => num(y.sequence) - num(x.sequence)).slice(0, 4);
  const allClear = num(dash.at_risk_count) === 0 && num(dash.evidence_gap_count) === 0;

  return (
    <div className="page">
      <PathHero />
      <div className="hero">
        <div className="hero-big"><D f="Dashboards.OpenPrizeProblemCount">{num(dash.open_prize_problem_count)}</D> of {prize.length}</div>
        <div className="hero-sub">prize problems still open</div>
      </div>

      {running.length > 0 && (
        <div className="banner running-banner">
          <span className="dot" /> <D f="Dashboards.RunningLoopCount">{num(dash.running_loop_count)}</D> loop running:{' '}
          {running.map((l) => <Link key={l.loop_id} to={`/loops/${l.loop_id}`}>{l.name}</Link>)}
        </div>
      )}

      <div className="tiles">
        <Tile label="Proved" value={num(dash.proved_count)} f="Dashboards.ProvedCount" tone="g-proved" to="/claims?group=Proved" />
        <Tile label="Checked (finite)" value={num(dash.checked_count)} f="Dashboards.CheckedCount" tone="g-checked" to="/claims?group=Checked" />
        <Tile label="Falsified" value={num(dash.falsified_count)} f="Dashboards.FalsifiedCount" tone="g-falsified" to="/claims?group=Falsified" />
        <Tile label="Open" value={num(dash.open_count)} f="Dashboards.OpenCount" tone="g-open" to="/claims?group=Open" />
        <Tile label="Native loops verified" value={num(dash.completed_native_loops)} f="Dashboards.CompletedNativeLoops" to="/loops" />
        <Tile label="Legacy cycles" value={num(dash.legacy_loop_count)} f="Dashboards.LegacyLoopCount" to="/loops" />
      </div>

      <div className={`banner ${allClear ? 'ok-banner' : 'warn-banner'}`}>
        {allClear ? 'Ledger consistent: ' : 'Check the ledger: '}
        <D f="Dashboards.AtRiskCount">{num(dash.at_risk_count)}</D> established claims rest on something unestablished,{' '}
        <D f="Dashboards.EvidenceGapCount">{num(dash.evidence_gap_count)}</D> finite checks lack evidence.
      </div>

      <Section title="Prize problems">
        <div className="grid">{prize.map((a) => <PrizeCard key={a.assessment_id} a={a} />)}</div>
      </Section>

      <Section title="Latest loops" right={<Link to="/loops">All loops</Link>}>
        <div className="grid">{recent.map((l) => <LoopRow key={l.loop_id} l={l} />)}</div>
      </Section>
    </div>
  );
}
