import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'node:path';

// Hard-coded ports: explorer 7431, rulebook editor API 42441 (effortless-rulebook/ports.env).
const PORT = 7431;
const API = 'http://localhost:42441';
const REPO = path.resolve(__dirname, '..');
const ALLOWED = ['research/', 'bootstrap/', 'docs/'];
const TYPES: Record<string, string> = { '.md': 'text/markdown', '.json': 'application/json', '.txt': 'text/plain', '.py': 'text/plain', '.log': 'text/plain', '.wl': 'text/plain' };

/** Read-only access to proof and evidence files under research/, bootstrap/ and docs/. */
function repoFiles(): Plugin {
  return {
    name: 'repo-files',
    configureServer(server) {
      server.middlewares.use('/repo-files/', (req, res) => {
        const rel = decodeURIComponent((req.url ?? '').split('?')[0]).replace(/^\/+/, '');
        const abs = path.resolve(REPO, rel);
        const type = TYPES[path.extname(abs)];
        const ok = type && ALLOWED.some((p) => rel.startsWith(p)) && abs.startsWith(REPO + path.sep) && fs.existsSync(abs) && fs.statSync(abs).isFile();
        if (!ok) {
          res.statusCode = 404;
          res.end('not found');
          return;
        }
        res.setHeader('Content-Type', `${type}; charset=utf-8`);
        res.setHeader('X-File-Size', String(fs.statSync(abs).size));
        fs.createReadStream(abs).pipe(res);
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), repoFiles()],
  server: { port: PORT, strictPort: true, proxy: { '/api': API } },
});
