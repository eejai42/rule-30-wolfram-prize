/**
 * One store for the whole app: every view the screens read, re-fetched every 5 s.
 * Values are rendered as the views return them; nothing here derives a status, count or flag.
 */
import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react';

export type Row = Record<string, any>;
export const TABLES = ['Dashboards', 'Assessments', 'Assertions', 'Dependencies', 'Prerequisites', 'Loops', 'Revisions', 'Evidence', 'EvidenceLinks', 'Strategies', 'StrategySteps', 'Predicates', 'PredicateInstances'] as const;
export type TableName = (typeof TABLES)[number];
export type Data = Record<TableName, Row[]>;
export type Sync = 'loading' | 'live' | 'syncing' | 'offline';

interface Store {
  data: Data | null;
  sync: Sync;
  editorBuilding: boolean;
  updatedAt: Date | null;
  changed: Set<string>; // "Table:id" rows whose values changed on the last refresh
}

const Ctx = createContext<Store>({ data: null, sync: 'loading', editorBuilding: false, updatedAt: null, changed: new Set() });
const POLL_MS = 5000;
const PK: Record<TableName, string> = {
  Dashboards: 'dashboard_id', Assessments: 'assessment_id', Assertions: 'assertion_id', Dependencies: 'dependency_id', Prerequisites: 'prerequisite_id',
  Loops: 'loop_id', Revisions: 'revision_id', Evidence: 'evidence_id', EvidenceLinks: 'evidence_link_id',
  Strategies: 'strategy_id', StrategySteps: 'strategy_step_id', Predicates: 'predicate_id', PredicateInstances: 'predicate_instance_id',
};

async function fetchTable(t: TableName): Promise<Row[]> {
  const r = await fetch(`/api/tables/${t}`);
  if (!r.ok) throw new Error(`${t}: ${r.status}`);
  return (await r.json()).rows as Row[];
}

function diff(prev: Data | null, next: Data): Set<string> {
  const out = new Set<string>();
  if (!prev) return out;
  for (const t of TABLES) {
    const before = new Map(prev[t].map((r) => [r[PK[t]], JSON.stringify(r)]));
    for (const r of next[t]) if (before.get(r[PK[t]]) !== JSON.stringify(r)) out.add(`${t}:${r[PK[t]]}`);
  }
  return out;
}

export function DataProvider({ children }: { children: ReactNode }) {
  const [store, setStore] = useState<Store>({ data: null, sync: 'loading', editorBuilding: false, updatedAt: null, changed: new Set() });
  const last = useRef<Data | null>(null);
  useEffect(() => {
    let alive = true;
    let inFlight = false;   // a poll can outlast POLL_MS (PredicateInstances reads in ~7 s); never stack them
    async function tick() {
      if (inFlight) return;
      inFlight = true;
      try { await poll(); } finally { inFlight = false; }
    }
    async function poll() {
      let building = false;
      try {
        const s = await fetch('/api/admin/build-status');
        if (s.ok) building = !!(await s.json()).running;
      } catch { /* editor restarting */ }
      try {
        const rows = await Promise.all(TABLES.map(fetchTable));
        const next = Object.fromEntries(TABLES.map((t, i) => [t, rows[i]])) as Data;
        const changed = diff(last.current, next);
        last.current = next;
        if (alive) setStore({ data: next, sync: building ? 'syncing' : 'live', editorBuilding: building, updatedAt: new Date(), changed });
      } catch {
        if (alive) setStore((s) => ({ ...s, sync: s.data ? 'syncing' : 'offline', editorBuilding: building, changed: new Set() }));
      }
    }
    tick();
    const id = setInterval(tick, POLL_MS);
    return () => { alive = false; clearInterval(id); };
  }, []);
  return <Ctx.Provider value={store}>{children}</Ctx.Provider>;
}

export const useStore = () => useContext(Ctx);

/** Rows of one view, or [] while loading. */
export function useRows(t: TableName): Row[] {
  return useStore().data?.[t] ?? [];
}

export function byId(rows: Row[], key: string, id: string | undefined): Row | undefined {
  return rows.find((r) => r[key] === id);
}

export const num = (v: unknown) => (v === null || v === undefined || v === '' ? 0 : Number(v));
