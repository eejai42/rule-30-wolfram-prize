import { Link, useParams } from 'react-router-dom';
import { byId, num, useRows, type Row } from '../data';
import { CardLink, ClaimLink, D, Group, LoopState, LoopTargetList, Section, useFlash } from '../ui';

function LoopItem({ l }: { l: Row }) {
  const flash = useFlash('Loops', l.loop_id);
  const targets = useRows('LoopTargets').filter((t) => t.loop === l.loop_id);
  if (l.state === 'PLANNED') {
    return (
      <CardLink to={`/loops/${l.loop_id}`} className={`timeline-item is-planned${flash}`}>
        <div className="timeline-dot" data-kind="PLANNED" />
        <div className="timeline-body">
          <div className="card-top"><b>{l.name}</b> <LoopState row={l} /> <span className="muted small">next loop</span></div>
          <p className="statement">{l.hypothesis}</p>
          <p className="muted small">{l.plan}</p>
          <LoopTargetList rows={targets} compact />
        </div>
      </CardLink>
    );
  }
  return (
    <CardLink to={`/loops/${l.loop_id}`} className={`timeline-item${l.state === 'RUNNING' ? ' is-running' : ''}${flash}`}>
      <div className="timeline-dot" data-kind={l.kind} />
      <div className="timeline-body">
        <div className="card-top">
          <b>{l.name}</b>
          <LoopState row={l} />
        </div>
        <p className="statement">{l.hypothesis}</p>
        {l.kind === 'EFFORTLESS' ? (
          <div className="counts">
            <span><D f="Loops.ClaimsAdded">{num(l.claims_added)}</D> added</span>
            <span><D f="Loops.RevisionsMade">{num(l.revisions_made)}</D> revisions</span>
            <span><D f="Loops.ProofsMade">{num(l.proofs_made)}</D> proved</span>
            <span><D f="Loops.FalsificationsMade">{num(l.falsifications_made)}</D> falsified</span>
          </div>
        ) : (
          <p className="muted small">{l.summary}</p>
        )}
        <LoopTargetList rows={targets} compact />
      </div>
    </CardLink>
  );
}

export function LoopsPage() {
  const loops = [...useRows('Loops')].sort((a, b) => num(b.sequence) - num(a.sequence));
  return (
    <div className="page">
      <h1>Loops</h1>
      <p className="muted">Newest first, with the planned next loop at the top. Native loops ran a build and carry a receipt; legacy cycles come from research v05. Each loop links the claims it serves, tests or builds on.</p>
      <div className="timeline">{loops.map((l) => <LoopItem key={l.loop_id} l={l} />)}</div>
    </div>
  );
}

export function LoopPage() {
  const { id } = useParams();
  const l = byId(useRows('Loops'), 'loop_id', id);
  const assessments = useRows('Assessments');
  const added = useRows('Assertions').filter((a) => a.introduced_in_loop === id);
  const revisions = useRows('Revisions').filter((r) => r.loop === id);
  const targets = useRows('LoopTargets').filter((t) => t.loop === id);
  if (!l) return <p className="muted">Loading…</p>;
  let receipt: Record<string, any> | null = null;
  try { receipt = l.build_receipt ? JSON.parse(l.build_receipt) : null; } catch { receipt = null; }
  return (
    <div className="page">
      <Link to="/loops" className="back">← Loops</Link>
      <div className="card-top"><h1>{l.name}</h1><LoopState row={l} /></div>
      {l.state === 'PLANNED' && <div className="banner running-banner">Planned: this loop has not started. Its hypothesis is a draft until the run fixes it.</div>}
      <Section title="Hypothesis"><p>{l.hypothesis}</p></Section>
      {l.plan && <Section title="Plan"><p>{l.plan}</p></Section>}
      {l.summary && <Section title="What happened"><p>{l.summary}</p></Section>}
      {targets.length > 0 && <Section title={`Related claims (${num(l.target_count)})`}><LoopTargetList rows={targets} /></Section>}
      {l.kind === 'EFFORTLESS' && l.state !== 'PLANNED' && (
        <>
          <div className="tiles small-tiles">
            <div className="tile"><div className="tile-value"><D f="Loops.ClaimsAdded">{num(l.claims_added)}</D></div><div className="tile-label">claims added</div></div>
            <div className="tile"><div className="tile-value"><D f="Loops.RevisionsMade">{num(l.revisions_made)}</D></div><div className="tile-label">revisions</div></div>
            <div className="tile g-proved"><div className="tile-value"><D f="Loops.ProofsMade">{num(l.proofs_made)}</D></div><div className="tile-label">moved to proved</div></div>
            <div className="tile g-falsified"><div className="tile-value"><D f="Loops.FalsificationsMade">{num(l.falsifications_made)}</D></div><div className="tile-label">falsified</div></div>
          </div>
          <Section title="Claims added">
            {added.length === 0 ? <p className="muted">None.</p> : (
              <ul className="list">
                {added.map((a) => {
                  const s = byId(assessments, 'assessment_id', a.assertion_id);
                  return (
                    <li key={a.assertion_id}>
                      <ClaimLink id={a.assertion_id} /> {s && <Group value={s.status_group} f="Assessments.StatusGroup" />}
                      <div className="muted">{a.statement}</div>
                    </li>
                  );
                })}
              </ul>
            )}
          </Section>
          <Section title="Status changes">
            {revisions.length === 0 ? <p className="muted">None.</p> : (
              <ul className="list">
                {revisions.map((r) => (
                  <li key={r.revision_id}>
                    <ClaimLink id={r.assertion} /> <span className="mono">{r.prior_status}</span> → <span className="mono">{r.new_status}</span>
                    <div className="muted">{r.reason}</div>
                  </li>
                ))}
              </ul>
            )}
          </Section>
          <Section title="Build receipt">
            <dl className="kv">
              <dt>Started</dt><dd>{l.started_at || <span className="muted">not recorded</span>}</dd>
              <dt>Finished</dt><dd>{l.finished_at || <span className="muted">not recorded</span>}</dd>
              <dt>Rulebook in</dt><dd className="mono hash">{l.input_hash || '—'}</dd>
              <dt>Rulebook out</dt><dd className="mono hash">{l.output_hash || '—'}</dd>
              {receipt && <><dt>Build</dt><dd>exit {receipt.exit}, {receipt.seconds}s</dd>
                <dt>Transpilers</dt><dd>{(receipt.versions as string[]).map((v) => <div key={v} className="mono small">{v.replace('cli:> ', '')}</div>)}</dd></>}
            </dl>
          </Section>
        </>
      )}
      {l.kind !== 'EFFORTLESS' && revisions.length > 0 && (
        <Section title="Status changes">
          <ul className="list">{revisions.map((r) => <li key={r.revision_id}><ClaimLink id={r.assertion} /> {r.prior_status} → {r.new_status}<div className="muted">{r.reason}</div></li>)}</ul>
        </Section>
      )}
    </div>
  );
}
