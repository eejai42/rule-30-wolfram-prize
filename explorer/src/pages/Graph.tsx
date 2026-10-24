import { useMemo, useRef, useState, type PointerEvent, type WheelEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import dagre from '@dagrejs/dagre';
import { byId, num, useRows } from '../data';
import { D, Group } from '../ui';

const W = 64, H = 30;

/** Dependency graph: premises below, conclusions above, prize problems at the top. */
export default function Graph() {
  const assessments = useRows('Assessments');
  const deps = useRows('Dependencies');
  const prereqs = useRows('Prerequisites');
  const assertions = useRows('Assertions');
  const [params, setParams] = useSearchParams();
  const focus = params.get('focus') ?? '';
  const showFalsified = params.get('falsified') === '1';
  const navigate = useNavigate();

  const layout = useMemo(() => {
    const g = new dagre.graphlib.Graph();
    g.setGraph({ rankdir: 'BT', nodesep: 14, ranksep: 46, marginx: 20, marginy: 20 });
    g.setDefaultEdgeLabel(() => ({}));
    const nodes = assessments.filter((a) => showFalsified || a.status_group !== 'Falsified');
    const ids = new Set(nodes.map((a) => a.assessment_id));
    nodes.forEach((a) => g.setNode(a.assessment_id, { width: W, height: H }));
    deps.forEach((d) => { if (ids.has(d.premise) && ids.has(d.conclusion)) g.setEdge(d.premise, d.conclusion); });
    dagre.layout(g);
    const w = g.graph().width, h = g.graph().height;
    return { g, nodes, w: Number.isFinite(w) && w! > 0 ? w! : 400, h: Number.isFinite(h) && h! > 0 ? h! : 400 };
  }, [assessments, deps, showFalsified]);

  // Ancestors of the focused claim come from the rulebook's Prerequisites closure, not from a graph walk.
  const ancestors = useMemo(() => new Set(prereqs.filter((p) => p.conclusion_key === focus).map((p) => p.premise)), [prereqs, focus]);
  const descendants = useMemo(() => new Set(prereqs.filter((p) => p.premise === focus).map((p) => p.conclusion_key)), [prereqs, focus]);
  const lit = (id: string) => !focus || ancestors.has(id) || descendants.has(id);

  const [view, setView] = useState({ x: 0, y: 0, k: 1 });
  const drag = useRef<{ x: number; y: number; vx: number; vy: number; moved: boolean } | null>(null);
  const onDown = (e: PointerEvent<SVGSVGElement>) => { drag.current = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y, moved: false }; };
  const onMove = (e: PointerEvent<SVGSVGElement>) => {
    const d = drag.current;
    if (!d) return;
    if (Math.abs(e.clientX - d.x) + Math.abs(e.clientY - d.y) > 4) d.moved = true;
    setView((v) => ({ ...v, x: d.vx + (e.clientX - d.x), y: d.vy + (e.clientY - d.y) }));
  };
  const onUp = () => { setTimeout(() => { drag.current = null; }, 0); };
  const onWheel = (e: WheelEvent<SVGSVGElement>) => setView((v) => ({ ...v, k: Math.min(3, Math.max(0.3, v.k * (e.deltaY < 0 ? 1.1 : 0.9))) }));
  const select = (id: string) => {
    if (drag.current?.moved) return;
    const next = new URLSearchParams(params);
    if (focus === id) next.delete('focus'); else next.set('focus', id);
    setParams(next, { replace: true });
  };
  const sel = byId(assessments, 'assessment_id', focus);

  return (
    <div className="page graph-page">
      <div className="graph-bar">
        <h1>Dependency graph</h1>
        <label className="chip"><input type="checkbox" checked={showFalsified} onChange={(e) => { const n = new URLSearchParams(params); if (e.target.checked) n.set('falsified', '1'); else n.delete('falsified'); setParams(n, { replace: true }); }} /> show falsified</label>
        <button className="chip" onClick={() => setView({ x: 0, y: 0, k: 1 })}>reset view</button>
      </div>
      <p className="muted small">Arrows point from a premise up to the claim that uses it. Tap a claim to light up everything it rests on and everything that rests on it; double-click it to open its page. Claims with a thick outline are on the current path to P1. Drag to pan, scroll to zoom.</p>
      <div className="legend">
        {['Proved', 'Checked', 'Open', 'Falsified'].map((g) => <span key={g} className={`pill g-${g.toLowerCase()}`}>{g}</span>)}
      </div>
      <div className="graph-wrap">
        <svg viewBox={`0 0 ${layout.w} ${layout.h}`} onPointerDown={onDown} onPointerMove={onMove} onPointerUp={onUp} onPointerLeave={onUp} onWheel={onWheel}>
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" className="arrowhead" />
            </marker>
          </defs>
          <g transform={`translate(${view.x},${view.y}) scale(${view.k})`}>
            {layout.g.edges().map((e) => {
              const pts = layout.g.edge(e).points;
              const on = !focus || ((ancestors.has(e.v) || e.v === focus) && (ancestors.has(e.w) || e.w === focus)) || ((descendants.has(e.w) || e.w === focus) && (descendants.has(e.v) || e.v === focus));
              return <polyline key={`${e.v}-${e.w}`} points={pts.map((p) => `${p.x},${p.y}`).join(' ')} className={`edge${on ? '' : ' dim'}`} markerEnd="url(#arrow)" />;
            })}
            {layout.nodes.map((a) => {
              const n = layout.g.node(a.assessment_id);
              const onPath = num(byId(assertions, 'assertion_id', a.assessment_id)?.on_current_path) > 0;
              const cls = `node g-${String(a.status_group).toLowerCase()}${lit(a.assessment_id) ? '' : ' dim'}${focus === a.assessment_id ? ' focus' : ''}${onPath ? ' on-path' : ''}`;
              return (
                <g key={a.assessment_id} className={cls} transform={`translate(${n.x - W / 2},${n.y - H / 2})`} onClick={() => select(a.assessment_id)} onDoubleClick={() => navigate(`/claims/${a.assessment_id}`)}>
                  <rect width={W} height={H} rx={8} />
                  <text x={W / 2} y={H / 2 + 4} textAnchor="middle">{a.assessment_id}</text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>
      {sel && (
        <div className="card focus-card">
          <div className="card-top">
            <b>{sel.assessment_id}</b> <span className="kind">{sel.kind}</span> <Group value={sel.status_group} f="Assessments.StatusGroup" />
          </div>
          <p className="statement">{sel.statement}</p>
          <div className="counts">
            <span>rests on <D f="Assessments.AncestorCount">{num(sel.ancestor_count)}</D></span>
            <span>supports <D f="Assertions.DescendantCount">{num(byId(assertions, 'assertion_id', sel.assessment_id)?.descendant_count)}</D></span>
            <span><D f="Assessments.AncestorBlockedCount">{num(sel.ancestor_blocked_count)}</D> blocking</span>
          </div>
          <Link to={`/claims/${encodeURIComponent(sel.assessment_id)}`}>Open claim →</Link>
        </div>
      )}
    </div>
  );
}
