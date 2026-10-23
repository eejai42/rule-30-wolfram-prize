import { useEffect, useState } from 'react';
import { NavLink, Route, Routes, useLocation } from 'react-router-dom';
import { useStore } from './data';
import { DagFieldPage, DagIndexPage, DagTablePage, ExplainerEnhance, useExplainerRouting } from './explainer-bridge';
import Progress from './pages/Progress';
import { LoopPage, LoopsPage } from './pages/Loops';
import { ClaimPage, ClaimsPage } from './pages/Claims';
import Graph from './pages/Graph';
import FileView from './pages/FileView';

const NAV = [
  { to: '/', label: 'Progress', end: true },
  { to: '/loops', label: 'Loops' },
  { to: '/claims', label: 'Claims' },
  { to: '/graph', label: 'Graph' },
  { to: '/dag', label: 'Rules' },
];

function SyncBadge() {
  const { sync, updatedAt } = useStore();
  const [, tick] = useState(0);
  useEffect(() => { const id = setInterval(() => tick((n) => n + 1), 1000); return () => clearInterval(id); }, []);
  const ago = updatedAt ? Math.max(0, Math.round((Date.now() - updatedAt.getTime()) / 1000)) : null;
  const label = sync === 'live' ? 'Live' : sync === 'syncing' ? 'Syncing' : sync === 'offline' ? 'Editor offline' : 'Loading';
  return (
    <span className={`sync sync-${sync}`} title={updatedAt ? `Last refresh ${updatedAt.toLocaleTimeString()}` : ''}>
      <span className="dot" /> {label}{ago !== null && sync !== 'offline' ? ` · ${ago}s` : ''}
    </span>
  );
}

export default function App() {
  useExplainerRouting();
  const [menu, setMenu] = useState(false);
  const loc = useLocation();
  useEffect(() => setMenu(false), [loc.pathname]);
  const { sync } = useStore();

  return (
    <>
      <ExplainerEnhance />
      <header className="topbar">
        <NavLink to="/" className="brand"><span className="logo" aria-hidden>▚</span> Rule 30 Explorer</NavLink>
        <nav className={menu ? 'nav open' : 'nav'}>
          {NAV.map((n) => <NavLink key={n.to} to={n.to} end={n.end}>{n.label}</NavLink>)}
          <a href="http://localhost:42442" target="_blank" rel="noreferrer">Admin ↗</a>
        </nav>
        <div className="topbar-right">
          <SyncBadge />
          <div id="effortless-dag-toggle" />
          <button className="menu-btn" aria-label="Menu" onClick={() => setMenu((m) => !m)}>☰</button>
        </div>
      </header>
      {sync === 'offline' && (
        <div className="banner warn-banner page">
          The rulebook editor API is not answering on port 42441. Start it with <code>./start.sh</code> from the repo root.
        </div>
      )}
      <main>
        <Routes>
          <Route path="/" element={<Progress />} />
          <Route path="/loops" element={<LoopsPage />} />
          <Route path="/loops/:id" element={<LoopPage />} />
          <Route path="/claims" element={<ClaimsPage />} />
          <Route path="/claims/:id" element={<ClaimPage />} />
          <Route path="/graph" element={<Graph />} />
          <Route path="/files" element={<FileView />} />
          <Route path="/dag" element={<div className="page"><DagIndexPage /></div>} />
          <Route path="/dag/:table" element={<div className="page"><DagTablePage /></div>} />
          <Route path="/dag/:table/:field" element={<div className="page"><DagFieldPage /></div>} />
          <Route path="*" element={<Progress />} />
        </Routes>
      </main>
    </>
  );
}
