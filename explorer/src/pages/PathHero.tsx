import { Link } from 'react-router-dom';
import { num, useRows, type Row } from '../data';
import { ClaimLink, D, Group, useFlash } from '../ui';

const ROLE_CLASS: Record<string, string> = {
  Goal: 'role-goal', Reduction: 'role-reduction', 'Open obligation': 'role-open', Evidence: 'role-evidence', 'Ruled out': 'role-ruled',
};

function Step({ s, isNext }: { s: Row; isNext: boolean }) {
  const flash = useFlash('StrategySteps', s.strategy_step_id);
  return (
    <li className={`path-step ${ROLE_CLASS[s.role] ?? ''}${isNext ? ' is-next' : ''}${flash}`}>
      <div className="path-step-top">
        <ClaimLink id={s.assertion} />
        <span className="path-role">{s.role}</span>
        <Group value={s.status_group} f="StrategySteps.StatusGroup" />
        {num(s.blocks_goal) === 1 && <D f="StrategySteps.BlocksGoal" className="pill g-open">blocking</D>}
        {isNext && <span className="pill running">next loop</span>}
      </div>
      <div className="path-note">{s.note}</div>
    </li>
  );
}

/** The plan in force: where things stand, the route to the goal, what blocks it, where the next loop aims. */
export default function PathHero() {
  const plan = useRows('Strategies').find((r) => num(r.is_current) === 1);
  const steps = useRows('StrategySteps').filter((r) => plan && r.strategy === plan.strategy_id).sort((a, b) => num(a.sequence) - num(b.sequence));
  const flash = useFlash('Strategies', plan?.strategy_id ?? '');
  if (!plan) return null;
  const route = steps.filter((s) => ['Goal', 'Reduction', 'Open obligation'].includes(s.role));
  const evidence = steps.filter((s) => s.role === 'Evidence');
  const ruled = steps.filter((s) => s.role === 'Ruled out');

  return (
    <section className={`path-hero${flash}`}>
      <div className="path-head">
        <div className="eyebrow">Most promising path to <ClaimLink id={plan.goal} /> · plan after <Link to={`/loops/${plan.updated_in_loop}`}>{plan.updated_in_loop}</Link></div>
        <h1 className="path-headline">{plan.headline}</h1>
        <div className="path-counts">
          <span><D f="Strategies.EstablishedStepCount"><b>{num(plan.established_step_count)}</b></D> established</span>
          <span><D f="Strategies.OpenStepCount"><b>{num(plan.open_step_count)}</b></D> open</span>
          <span><D f="Strategies.BlockingStepCount"><b>{num(plan.blocking_step_count)}</b></D> blocking the goal</span>
          <span><D f="Strategies.RuledOutCount"><b>{num(plan.ruled_out_count)}</b></D> ruled out</span>
          <span><D f="Strategies.GoalAncestorBlockedCount"><b>{num(plan.goal_ancestor_blocked_count)}</b></D> open ancestors of {plan.goal}</span>
        </div>
      </div>

      <div className="path-body">
        <div className="path-col">
          <h2>The route</h2>
          <ol className="path-route">{route.map((s) => <Step key={s.strategy_step_id} s={s} isNext={s.assertion === plan.next_target} />)}</ol>
        </div>
        <div className="path-col">
          <div className="card next-card">
            <div className="eyebrow">Next loop aims at <ClaimLink id={plan.next_target} /> <Group value={plan.next_target_status_group} f="Strategies.NextTargetStatusGroup" /></div>
            <p className="statement">{plan.next_hypothesis}</p>
            {plan.next_loop && <Link to={`/loops/${plan.next_loop}`}>Planned loop {plan.next_loop} <D f="Strategies.NextLoopState" className="pill planned">{String(plan.next_loop_state ?? '').toLowerCase()}</D> →</Link>}
          </div>
          <div className="card">
            <div className="eyebrow">The approach</div>
            <p className="statement">{plan.approach}</p>
            <div className="eyebrow">What is missing</div>
            <p className="statement">{plan.missing}</p>
            <div className="eyebrow">Honest odds</div>
            <p className="statement muted">{plan.estimate}</p>
          </div>
          {evidence.length > 0 && (
            <div className="card">
              <div className="eyebrow">Evidence the route rests on</div>
              <ul className="path-mini">{evidence.map((s) => <Step key={s.strategy_step_id} s={s} isNext={false} />)}</ul>
            </div>
          )}
          {ruled.length > 0 && (
            <div className="card">
              <div className="eyebrow">Ruled out (do not retry)</div>
              <ul className="path-mini">{ruled.map((s) => <Step key={s.strategy_step_id} s={s} isNext={false} />)}</ul>
              <Link to="/files?path=docs%2Fp1-frontier.md">Full frontier map →</Link>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
