import type { KeyboardEvent, MouseEvent, ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useStore, type Row } from './data';

/** A derived value, marked for the explainer. `f` is the rulebook's Table.Field (PascalCase). */
export function D({ f, children, className }: { f: string; children: ReactNode; className?: string }) {
  return <span data-er-dag={f} className={className}>{children}</span>;
}

const GROUP_CLASS: Record<string, string> = { Proved: 'g-proved', Checked: 'g-checked', Falsified: 'g-falsified', Open: 'g-open', Superseded: 'g-superseded' };

/** StatusGroup pill; the value comes from the view. */
export function Group({ value, f }: { value: string; f: string }) {
  return <D f={f} className={`pill ${GROUP_CLASS[value] ?? ''}`}>{value}</D>;
}

/**
 * A whole card that opens `to` when tapped. Not an <a>: the explainer ignores double-clicks
 * inside links, and a tap on a derived value belongs to the explainer, not to the card.
 */
export function CardLink({ to, className, children }: { to: string; className: string; children: ReactNode }) {
  const navigate = useNavigate();
  const go = (e: MouseEvent | KeyboardEvent) => {
    const t = e.target as HTMLElement;
    if (t.closest('[data-er-dag], a, button, input')) return;
    navigate(to);
  };
  return (
    <div role="link" tabIndex={0} className={`${className} clickable`} onClick={go} onKeyDown={(e) => { if (e.key === 'Enter') go(e); }}>
      {children}
    </div>
  );
}

export function Tile({ label, value, f, tone, to }: { label: string; value: ReactNode; f: string; tone?: string; to?: string }) {
  const body = (
    <>
      <div className="tile-value"><D f={f}>{value}</D></div>
      <div className="tile-label">{label}</div>
    </>
  );
  return to ? <CardLink to={to} className={`tile ${tone ?? ''}`}>{body}</CardLink> : <div className={`tile ${tone ?? ''}`}>{body}</div>;
}

export function ClaimLink({ id, children }: { id: string; children?: ReactNode }) {
  return <Link className="claim-id" to={`/claims/${encodeURIComponent(id)}`}>{children ?? id}</Link>;
}

export function Section({ title, children, right }: { title: string; children: ReactNode; right?: ReactNode }) {
  return (
    <section className="section">
      <div className="section-head"><h2>{title}</h2>{right}</div>
      {children}
    </section>
  );
}

/** Highlights a card for one refresh after its row changed. */
export function useFlash(table: string, id: string) {
  return useStore().changed.has(`${table}:${id}`) ? ' flash' : '';
}

export function LoopState({ row }: { row: Row }) {
  const s = row.state as string;
  const cls = s === 'RUNNING' ? 'pill running' : s === 'VERIFIED' ? 'pill g-proved' : s === 'PLANNED' ? 'pill planned' : 'pill g-superseded';
  return <span className={cls}>{s === 'REPORTED_COMPLETE' ? 'legacy' : s.toLowerCase()}</span>;
}

/** "research/x/PROOFS.md §TJ" -> file link; "3" or "2; original THEOREM_004.md" -> the v05 report section. */
export function proofLink(section: string | null | undefined): { path: string; anchor: string; label: string } | null {
  if (!section) return null;
  if (section.startsWith('research/')) {
    const [path, rest] = section.split(' §');
    return { path, anchor: (rest ?? '').split(';')[0].trim(), label: section };
  }
  const sec = section.split(';')[0].trim();
  return { path: 'bootstrap/cmcc_rule30_effortless_migration/research_v05/REPORT.md', anchor: `${sec}.`, label: `research_v05 REPORT.md §${section}` };
}

export const fileHref = (path: string, anchor = '') => `/files?path=${encodeURIComponent(path)}${anchor ? `&at=${encodeURIComponent(anchor)}` : ''}`;

const ROLE_ORDER = ['Serves', 'Tests', 'Builds on', 'Rules out'];

/** The claims a loop serves, tests or builds on (LoopTargets rows), grouped by role. */
export function LoopTargetList({ rows, compact }: { rows: Row[]; compact?: boolean }) {
  if (!rows.length) return null;
  const sorted = [...rows].sort((a, b) => ROLE_ORDER.indexOf(a.role) - ROLE_ORDER.indexOf(b.role));
  if (compact) {
    return (
      <div className="target-chips">
        {sorted.map((t) => <span key={t.loop_target_id} className="target-chip" title={`${t.role}: ${t.note}`}><span className="muted small">{t.role}</span> <ClaimLink id={t.assertion} /></span>)}
      </div>
    );
  }
  return (
    <ul className="list">
      {sorted.map((t) => (
        <li key={t.loop_target_id}>
          <span className="path-role">{t.role}</span> <ClaimLink id={t.assertion} /> <Group value={t.status_group} f="LoopTargets.StatusGroup" />
          <div className="muted">{t.note}</div>
          <div className="muted small">{t.statement}</div>
        </li>
      ))}
    </ul>
  );
}
