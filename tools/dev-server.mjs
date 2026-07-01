#!/usr/bin/env node
// Zero-dependency dev server with live reload for the 3d-viewer.
// Serves ../3d-viewer, injects an SSE snippet into HTML, and reloads the
// browser whenever any file under the served root changes.
//
//   node tools/dev-server.mjs [port]        (default port 8777)
//
// Conditional GET (Last-Modified/304) keeps large data files from re-downloading
// on every reload; only changed files come down fresh.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '../3d-viewer');
const PORT = Number(process.argv[2]) || 8777;

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
};

const RELOAD_SNIPPET = `
<script>(()=>{let es;function go(){es=new EventSource('/__livereload');
es.onmessage=e=>{if(e.data==='reload')location.reload()};
es.onerror=()=>{es.close();setTimeout(go,1000)};}go();})();</script>`;

const clients = new Set();

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);

  if (url === '/__livereload') {                     // SSE channel
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
    res.write('retry: 1000\n\n');
    clients.add(res);
    req.on('close', () => clients.delete(res));
    return;
  }

  let file = path.join(ROOT, url === '/' ? '/lab.html' : url);
  if (!file.startsWith(ROOT)) { res.writeHead(403).end('forbidden'); return; }   // no path traversal

  fs.stat(file, (err, st) => {
    if (err || st.isDirectory()) { res.writeHead(404).end('not found'); return; }
    const mtime = st.mtime.toUTCString();
    if (req.headers['if-modified-since'] === mtime) { res.writeHead(304).end(); return; }
    const ext = path.extname(file).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    const headers = { 'Content-Type': type, 'Cache-Control': 'no-cache', 'Last-Modified': mtime };

    if (ext === '.html') {                            // inject live-reload snippet
      let html = fs.readFileSync(file, 'utf8');
      html = html.includes('</body>') ? html.replace('</body>', RELOAD_SNIPPET + '\n</body>') : html + RELOAD_SNIPPET;
      res.writeHead(200, headers); res.end(html);
    } else {
      res.writeHead(200, headers);
      fs.createReadStream(file).pipe(res);
    }
  });
});

let timer = null;
fs.watch(ROOT, { recursive: true }, (_e, name) => {
  if (name && name.startsWith('.')) return;           // ignore dotfiles
  clearTimeout(timer);
  timer = setTimeout(() => {
    for (const c of clients) c.write('data: reload\n\n');
    console.log('reload →', name);
  }, 120);
});

server.listen(PORT, () => {
  console.log(`dev server: http://127.0.0.1:${PORT}/lab.html  (live reload on, serving ${path.relative(process.cwd(), ROOT)})`);
});
