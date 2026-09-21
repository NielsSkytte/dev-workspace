/* Shared runtime for the three dashboard pages.
 *
 * Today, Projects and Time are separate documents that share this module, app.css and
 * one payload. Rendering is Preact + htm (see vendor/README.md): the pages re-fetch on a
 * timer, and diffing is what stops each refresh from destroying an open drawer, the
 * scroll position, an expanded row or a half-typed filter.
 *
 * Nothing here knows about a particular page. Page-specific rendering lives in the page.
 */
import { h, render, Fragment } from './vendor/preact.module.js';
import { useState, useEffect, useRef, useCallback, useMemo } from './vendor/hooks.module.js';
import htm from './vendor/htm.module.js';

export const html = htm.bind(h);
export { render, Fragment, useState, useEffect, useRef, useCallback, useMemo };

/* ---------- formatting ---------- */

export const hrs = n => (Math.round(n * 100) / 100).toFixed(2).replace(/\.00$/, '');

export const ago = d =>
  d === null || d === undefined ? 'never' :
  d === 0 ? 'today' : d === 1 ? 'yesterday' : d + 'd ago';

export const label = p =>
  p.key === 'Dev' ? 'Dev (workspace)' : p.customer ? p.customer + ' / ' + p.name : p.key;

export const plural = (n, word) => n + ' ' + word + (n === 1 ? '' : 's');

/* How long since a project was touched, as one colour, one glyph and one word.
   The thresholds come from the payload so the server owns the rule. */
export function fresh(days, t) {
  const th = t || { good: 7, warn: 21, serious: 60 };
  if (days === null || days === undefined) return { c: 'var(--muted)', w: 'never', i: '○' };
  if (days <= th.good) return { c: 'var(--f1)', w: 'fresh', i: '●' };
  if (days <= th.warn) return { c: 'var(--f2)', w: 'aging', i: '◑' };
  if (days <= th.serious) return { c: 'var(--f3)', w: 'stale', i: '◓' };
  return { c: 'var(--f4)', w: 'cold', i: '○' };
}

/* ---------- toast ---------- */

let toastNode, toastTimer;
export function toast(msg) {
  if (!toastNode) {
    toastNode = document.createElement('div');
    toastNode.className = 'toast';
    document.body.appendChild(toastNode);
  }
  toastNode.textContent = msg;
  toastNode.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastNode.classList.remove('show'), 3200);
}

/* ---------- server ---------- */

export async function post(path, body) {
  try {
    const r = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return await r.json();
  } catch (e) {
    return { ok: false, message: e.message };
  }
}

/* Start a session (or a VS Code window) rooted at a project. That root is also what
   makes the session's tracked time attribute to the right project. */
export async function launch(path, mode, prompt) {
  toast('Starting…');
  const j = await post('/api/launch', { path, mode, prompt: prompt || '' });
  toast(j.message || (j.ok ? 'started' : 'failed'));
  return j;
}

/* The payload, fetched once per page and refreshed on a timer.
   `reload` is what a write path calls after a successful POST: the server drops its
   memo on every write, so the next read is already current. */
export function useData(url, intervalMs) {
  const [data, setData] = useState(null);
  const [err, setErr] = useState('');
  const [stamp, setStamp] = useState('');
  const [auto, setAuto] = useState(true);

  const load = useCallback(async () => {
    try {
      const r = await fetch(url, { cache: 'no-store' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const j = await r.json();
      setData(j);
      setErr('');
      setStamp(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    } catch (e) {
      setErr(e.message);
    }
  }, [url]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (!auto) return undefined;
    const id = setInterval(load, intervalMs || 60000);
    return () => clearInterval(id);
  }, [auto, load, intervalMs]);

  return { data, err, stamp, reload: load, auto, setAuto };
}

/* ---------- theme ---------- */

const THEME_KEY = 'dev-dashboard-theme';

export function useTheme() {
  const [theme, setTheme] = useState(() => {
    try { return localStorage.getItem(THEME_KEY) || ''; } catch (e) { return ''; }
  });
  useEffect(() => {
    if (theme) document.documentElement.setAttribute('data-theme', theme);
    else document.documentElement.removeAttribute('data-theme');
    try {
      if (theme) localStorage.setItem(THEME_KEY, theme);
      else localStorage.removeItem(THEME_KEY);
    } catch (e) { /* private window: the theme just does not persist */ }
  }, [theme]);
  const cycle = () => setTheme(t => (t === 'dark' ? 'light' : t === 'light' ? '' : 'dark'));
  return [theme, cycle];
}

/* ---------- shell ---------- */

const PAGES = [
  ['/', 'Today'],
  ['/projects', 'Projects'],
  ['/time', 'Time'],
];

export function Nav({ here }) {
  return html`
    <nav class="pagenav">
      ${PAGES.map(([href, name]) => html`
        <a href=${href} class=${href === here ? 'on' : ''}>${name}</a>`)}
    </nav>`;
}

export function Tile({ label: l, value, foot, hot }) {
  return html`
    <div class=${'tile' + (hot ? ' hot' : '')}>
      <div class="label">${l}</div>
      <div class="val">${value}</div>
      ${foot ? html`<div class="foot">${foot}</div>` : null}
    </div>`;
}

/* The brand band every page wears: title, nav, freshness stamp, the controls, and an
   optional tile strip. Children render into <main>. */
export function Shell({ here, title, sub, stamp, auto, onAuto, onRefresh, tiles, children }) {
  const [, cycleTheme] = useTheme();
  return html`
    <div class="shell">
      <div class="top">
        <header>
          <h1>${title}</h1>
          <span class="sub">${sub}</span>
          <${Nav} here=${here}/>
          <span class="grow"></span>
          <span class="sub">${stamp ? 'updated ' + stamp : ''}</span>
          <button class=${'mini' + (auto ? ' on' : '')} onClick=${onAuto}
                  title="re-fetch every 60 s">Auto</button>
          <button class="mini" onClick=${cycleTheme}>Theme</button>
          <button class="mini" onClick=${onRefresh}>Refresh</button>
        </header>
        ${tiles && tiles.length ? html`<div class="tiles">${tiles}</div>` : null}
      </div>
      <main>${children}</main>
    </div>`;
}

/* A right-hand detail panel. Mounted always, shown when `open` - so opening it does not
   remount its contents and a refresh underneath does not close it. */
export function Drawer({ open, onClose, children }) {
  useEffect(() => {
    if (!open) return undefined;
    const esc = e => { if (e.key === 'Escape') onClose(); };
    addEventListener('keydown', esc);
    return () => removeEventListener('keydown', esc);
  }, [open, onClose]);
  return html`
    <${Fragment}>
      <div class=${'scrim' + (open ? ' open' : '')} onClick=${onClose}></div>
      <aside class=${'drawer' + (open ? ' open' : '')}>
        <div class="inner">${open ? children : null}</div>
      </aside>
    <//>`;
}

export function Empty({ children }) {
  return html`<p class="empty">${children}</p>`;
}
