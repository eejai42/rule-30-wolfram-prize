import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { marked } from 'marked';

const MAX_CHARS = 200_000;

/** A proof or evidence file from the repo, read-only. Markdown is rendered; JSON and text are shown as-is. */
export default function FileView() {
  const [params] = useSearchParams();
  const path = params.get('path') ?? '';
  const at = params.get('at') ?? '';
  const [state, setState] = useState<{ text: string; size: number; error?: string } | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setState(null);
    fetch(`/repo-files/${path.split('/').map(encodeURIComponent).join('/')}`)
      .then(async (r) => (r.ok ? setState({ text: await r.text(), size: Number(r.headers.get('X-File-Size') ?? 0) }) : setState({ text: '', size: 0, error: `Not available (${r.status}).` })))
      .catch(() => setState({ text: '', size: 0, error: 'Not available.' }));
  }, [path]);

  useEffect(() => {
    if (!state || !at || !ref.current) return;
    const target = [...ref.current.querySelectorAll('h1,h2,h3,h4')].find((h) => (h.textContent ?? '').trim().startsWith(at) || (h.textContent ?? '').includes(`${at}.`) || (h.textContent ?? '').split(/[ .:]/)[0] === at);
    if (target) { target.classList.add('anchor-hit'); target.scrollIntoView({ block: 'start' }); }
  }, [state, at]);

  const isMd = path.endsWith('.md');
  let body = state?.text ?? '';
  const truncated = body.length > MAX_CHARS;
  if (truncated) body = body.slice(0, MAX_CHARS);
  if (path.endsWith('.json') && !truncated) {
    try { body = JSON.stringify(JSON.parse(body), null, 1); } catch { /* show raw */ }
  }

  return (
    <div className="page">
      <button className="back linklike" onClick={() => history.back()}>← Back</button>
      <h1 className="mono file-title">{path}</h1>
      {!state && <p className="muted">Loading…</p>}
      {state?.error && <p className="muted">{state.error}</p>}
      {state && !state.error && (
        <>
          {truncated && <p className="banner warn-banner">Showing the first {MAX_CHARS.toLocaleString()} characters of {state.size.toLocaleString()} bytes.</p>}
          {isMd ? <div ref={ref} className="markdown" dangerouslySetInnerHTML={{ __html: marked.parse(body, { async: false }) as string }} /> : <pre className="filebox">{body}</pre>}
        </>
      )}
      <p className="muted small">Files are served read-only from the repo. <Link to="/claims">Claims</Link></p>
    </div>
  );
}
