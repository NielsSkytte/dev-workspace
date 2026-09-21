/* Projects -- where everything stands.
 *
 * One row per project, worst attention first, in three bands. The band rule lives on the
 * server (dashboard.project_band) so the page cannot drift from it: gone quiet, in
 * flight, dormant. The workspace bucket is not a project and is not listed.
 *
 * This replaces the old "Not working on -- active projects gone quiet" panel, which
 * stated the problem without stating the position.
 */
import {
  html, render, useState, useMemo, useEffect,
  Shell, Tile, Drawer, Empty, Fragment, useData, launch, post, toast,
  hrs, ago, fresh, label, plural,
} from './app.js';

const BANDS = [
  ['quiet', 'Gone quiet', 'active, and nobody has touched it in 14 days'],
  ['inflight', 'In flight', 'worked in the last 14 days'],
  ['dormant', 'Dormant', 'the context reads complete, delivered or archived'],
];

const worst = (a, b) => (b === null ? 1e9 : b) - (a === null ? 1e9 : a);

function sortBand(band, rows) {
  if (band === 'inflight') {
    return rows.slice().sort((a, b) =>
      (a.days_idle - b.days_idle) || (b.hours_30d - a.hours_30d));
  }
  return rows.slice().sort((a, b) => worst(a.days_idle, b.days_idle));
}

const statusOf = p => (p.ctx_status || p.status || '').trim().toLowerCase() || 'no status';

/* -> [{key, title, hint, rows}] in the order they should appear.
   Activity is the default because it answers "what is slipping"; status answers
   "what did I say this project is", which is a different question and sometimes the
   one being asked. */
function groupRows(mode, projects) {
  if (mode === 'status') {
    const by = {};
    projects.forEach(p => { (by[statusOf(p)] = by[statusOf(p)] || []).push(p); });
    return Object.keys(by)
      .sort((a, b) => by[b].length - by[a].length || a.localeCompare(b))
      .map(key => ({
        key,
        title: key.charAt(0).toUpperCase() + key.slice(1),
        hint: 'as the context declares it',
        rows: sortBand('quiet', by[key]),
      }));
  }
  return BANDS
    .map(([key, title, hint]) => ({
      key, title, hint, rows: sortBand(key, projects.filter(p => p.band === key)),
    }))
    .filter(b => b.rows.length);
}

/* Which groups are folded away, remembered per viewer. A private window or blocked
   site data just means the page opens with everything expanded. */
const FOLD_KEY = 'dev-dashboard-projects-folded';

function useFolded() {
  const [folded, setFolded] = useState(() => {
    try { return new Set(JSON.parse(localStorage.getItem(FOLD_KEY) || '[]')); }
    catch (e) { return new Set(); }
  });
  useEffect(() => {
    try { localStorage.setItem(FOLD_KEY, JSON.stringify([...folded])); } catch (e) { /* ignore */ }
  }, [folded]);
  const toggle = id => setFolded(f => {
    const next = new Set(f);
    if (next.has(id)) next.delete(id); else next.add(id);
    return next;
  });
  return [folded, toggle, () => setFolded(new Set())];
}

/* ---------- row ---------- */

function Row({ p, th, onOpen }) {
  const f = fresh(p.days_idle, th);
  const c = p.counts;
  const standAge = p.standing_date ? daysBetween(p.standing_date) : null;
  return html`
    <tr class="clickable" onClick=${() => onOpen(p)}>
      <td>
        <b>${label(p)}</b>
        <div class="sub">${p.fno_code}</div>
      </td>
      <td class="ink2">${p.ctx_status || p.status || '—'}</td>
      <td>
        <span style=${'color:' + f.c}>${f.i}</span> ${f.w}
        <div class="sub">${ago(p.days_idle)}</div>
      </td>
      <td>
        ${p.standing_date || html`<span class="muted">no card</span>`}
        ${standAge === null ? null : html`<div class="sub">${ago(standAge)}</div>`}
      </td>
      <td class="num">
        ${c.in_progress || c.open
          ? html`${c.in_progress} ip / ${c.open} op`
          : html`<span class="muted">—</span>`}
        ${c.parked ? html`<div class="sub">${c.parked} parked</div>` : null}
      </td>
      <td class="ink2 opt">${p.blocked_people.length
        ? p.blocked_people.join(', ')
        : html`<span class="muted">—</span>`}</td>
      <td class="num">${c.asks_unsent
        ? html`<span style="color:var(--accent);font-weight:600">${c.asks_unsent}</span>`
        : html`<span class="muted">—</span>`}</td>
      <td class="num">${p.hours_month ? hrs(p.hours_month) : html`<span class="muted">—</span>`}</td>
    </tr>`;
}

function daysBetween(iso) {
  const d = new Date(iso + 'T00:00:00');
  if (isNaN(d)) return null;
  const now = new Date();
  return Math.floor((new Date(now.getFullYear(), now.getMonth(), now.getDate()) - d) / 86400000);
}

/* ---------- table ---------- */

function Table({ projects, th, onOpen, mode, folded, onToggle }) {
  const bands = groupRows(mode, projects).filter(b => b.rows.length);
  const n = bands.reduce((s, b) => s + b.rows.length, 0);

  return html`
    <section>
      <h2>Projects${n ? ' — ' + n : ''}</h2>
      ${!bands.length ? html`<div class="card"><${Empty}>No project matches.<//></div>` : html`
      <div class="card">
      <table>
        <tr>
          <th>Project</th><th>Status</th><th>Last worked</th><th>Standing</th>
          <th class="num">Tasks</th><th class="opt">Blocked on</th><th class="num">Asks</th>
          <th class="num">Hours MTD</th>
        </tr>
        ${bands.map(b => {
          const id = mode + ':' + b.key;
          const shut = folded.has(id);
          return html`
          <${Fragment} key=${b.key}>
            <tr class=${'band band-' + b.key}>
              <td class="bandhead" colspan="8">
                <button class="fold" onClick=${() => onToggle(id)}
                        aria-expanded=${shut ? 'false' : 'true'}>
                  <span class="caret">${shut ? '▸' : '▾'}</span>
                  ${b.title} — ${b.rows.length}
                  <span class="muted">· ${shut ? 'hidden' : b.hint}</span>
                </button>
              </td>
            </tr>
            ${shut ? null
              : b.rows.map(p => html`<${Row} key=${p.key} p=${p} th=${th} onOpen=${onOpen}/>`)}
          <//>`;
        })}
      </table>
      </div>`}
    </section>`;
}

/* ---------- detail ---------- */

function List({ title, items }) {
  if (!items || !items.length) return null;
  return html`
    <div class="block"><h4>${title}</h4>
      <ul class="tight">${items.map((x, i) => html`<li key=${i}>${x}</li>`)}</ul></div>`;
}

function Detail({ p, tasks }) {
  if (!p) return null;
  const mine = tasks.filter(t => t.project === p.key && t.state !== 'done' && t.state !== 'cancelled');
  return html`
    <h3>${label(p)}</h3>
    <p class="sub">${p.key}</p>
    <dl class="kv">
      <dt>F&O</dt><dd>${p.fno_code}</dd>
      <dt>Status</dt><dd>${p.ctx_status || p.status || '—'}</dd>
      <dt>Last worked</dt><dd>${ago(p.days_idle)}${p.last_activity ? ' · ' + p.last_activity : ''}</dd>
      <dt>Card</dt><dd>${p.card_shape === 'card' ? 'resume card' : p.card_shape === 'legacy' ? 'legacy CONTEXT.md' : 'none'}</dd>
      ${p.standing_date ? html`<dt>Where we stand</dt><dd>${p.standing_date}</dd>` : null}
      <dt>Hours</dt><dd>${hrs(p.hours_month)} this month · ${hrs(p.hours)} all time</dd>
    </dl>
    ${p.goal ? html`<div class="block"><h4>Goal</h4><p class="ink2">${p.goal}</p></div>` : null}
    ${p.focus ? html`<div class="block"><h4>Current focus</h4><p class="ink2">${p.focus}</p></div>` : null}
    <${List} title="Blocked on others" items=${p.blocked_people}/>
    <${List} title="In progress" items=${p.in_progress}/>
    <${List} title="Blocked on" items=${p.blocked_on}/>
    <${List} title="Next actions" items=${p.next_actions}/>
    <${List} title="Open threads" items=${p.open_threads}/>
    ${mine.length ? html`
      <div class="block"><h4>${plural(mine.length, 'task')}</h4>
        ${mine.map(t => html`
          <div class="tcard" key=${t.slug}>
            <b>${t.title || t.slug}</b>
            <div class="sub">${t.state}${t.fno_task ? ' · ' + t.fno_task : ''}</div>
          </div>`)}
      </div>` : null}
    <div class="block" style="display:flex;gap:8px">
      <button class="primary" onClick=${() => launch(p.path, 'claude')}>Start a session</button>
      <button onClick=${() => launch(p.path, 'code')}>VS Code</button>
    </div>
    <div class="block"><code>${p.path}</code></div>`;
}

/* ---------- the filter bar ----------
   Lifted from the retired `today.html`, which is the only place this existed. Two rows:
   who the open work sits with, and what state it is in.

   The counts are taken BEFORE the bar's own filters, on purpose -- a bar that recounted
   itself would collapse to the one chip you picked and stop being a distribution. */

const OWN = '__own__';
const bucketOf = p => p.customer || (p.key.startsWith('own/') ? OWN : OWN);
const bucketLabel = k => (k === OWN ? 'Own' : k);

/* Which task states a project can be filtered on. Every one is already counted per
   project by the server (`merge_card_fields`), so this reads a number rather than
   re-deriving a rule the day brief already owns. */
const STATES = [
  ['in_progress', 'In progress'],
  ['open', 'Open'],
  ['stalled', 'Stalled'],
  ['parked', 'Parked'],
  ['asks_unsent', 'Asks unsent'],
  ['due_back', 'Due back'],
];

function FilterBar({ projects, pick, onPick, state, onState }) {
  const by = {};
  projects.forEach(p => {
    const k = bucketOf(p);
    const b = by[k] || (by[k] = { total: 0, stalled: 0, asks: 0 });
    b.total += p.counts.total;
    b.stalled += p.counts.stalled;
    b.asks += p.counts.asks_unsent;
  });
  /* A customer with no open task still has projects, and hiding it would make the bar
     lie about who exists. It just gets no bar. */
  const order = Object.keys(by).sort((a, b) => by[b].total - by[a].total
    || (a === OWN) - (b === OWN) || a.localeCompare(b));
  const max = Math.max(1, ...order.map(k => by[k].total));
  const all = order.reduce((s, k) => s + by[k].total, 0);

  const stateCounts = {};
  STATES.forEach(([k]) => {
    stateCounts[k] = projects.reduce((s, p) => s + (p.counts[k] || 0), 0);
  });

  const chip = (key, text, count, pct, hot) => html`
    <button key=${key || 'all'} class=${'fc-chip' + (pick === key ? ' on' : '')}
            onClick=${() => onPick(key)}>
      <span>${text}</span><span class="cc">${count}</span>
      ${hot}
      <span class="fc-bar" style=${`width:${pct}%`}></span>
    </button>`;

  return html`
    <div class="fcbar">
      <div class="fc-row">
        <span class="fc-lbl">Customer</span>
        ${chip(null, 'All', all, 100, null)}
        ${order.map(k => chip(k, bucketLabel(k), by[k].total,
          Math.round(100 * by[k].total / max), html`
            <${Fragment}>
              ${by[k].stalled ? html`<span class="fc-hot">${by[k].stalled} stalled</span>` : null}
              ${by[k].asks ? html`<span class="fc-hot">${by[k].asks} unsent</span>` : null}
            <//>`))}
      </div>
      <div class="fc-row">
        <span class="fc-lbl">Task state</span>
        <button class=${'fc-chip sm' + (state ? '' : ' on')}
                onClick=${() => onState(null)}>All</button>
        ${STATES.map(([k, text]) => html`
          <button key=${k} class=${'fc-chip sm' + (state === k ? ' on' : '')}
                  disabled=${!stateCounts[k]}
                  title=${stateCounts[k] ? `${stateCounts[k]} across the listed projects`
                    : 'none right now'}
                  onClick=${() => onState(state === k ? null : k)}>
            ${text}<span class="cc">${stateCounts[k]}</span></button>`)}
      </div>
    </div>`;
}

/* ---------- customers ---------- */

function Customers({ customers, th, picked, onPick }) {
  if (!customers.length) return null;
  return html`
    <section>
      <h2>Customers${picked ? ' \u2014 filtering on ' + picked : ''}</h2>
      <div class="card">
        <table>
          <tr><th>Customer</th><th>Last activity</th>
            <th class="num">Proj</th><th class="num">Tasks</th><th class="num">Hours</th></tr>
          ${customers.map(c => {
            const f = fresh(c.days_idle, th);
            return html`
              <tr key=${c.name} class=${'clickable' + (picked === c.name ? ' picked' : '')}
                  title=${picked === c.name ? 'click to clear the filter' : 'click to show only this customer'}
                  onClick=${() => onPick(picked === c.name ? null : c.name)}>
                <td><b>${c.name}</b><div class="sub">${c.status || ''}</div></td>
                <td><span style=${'color:' + f.c}>${f.i}</span> ${ago(c.days_idle)}</td>
                <td class="num">${c.projects.length}</td>
                <td class="num">${c.open_tasks || html`<span class="muted">—</span>`}</td>
                <td class="num">${hrs(c.hours)}<div class="sub">${c.hours_30d ? hrs(c.hours_30d) + ' / 30d' : ''}</div></td>
              </tr>`;
          })}
        </table>
      </div>
    </section>`;
}

/* ---------- F&O readiness, per customer ----------
 *
 * Two different things are called a task in this workspace:
 *
 *   a WORK-TASK   `ops/tasks/<state>/<slug>.md` -- a unit of work you open a session on
 *   an F&O TASK   the Azure DevOps work-item id that goes in the Task column of a time line
 *
 * A work-task carries the F&O task (and the activity) so that every timesheet line worked
 * under it is complete the moment it is written. A work-task without one is a line that
 * cannot be entered, discovered at month close instead of now -- so the check belongs
 * beside the customer whose rule decides it, not on the timesheet line where it is already
 * too late to help.
 *
 * `fno_task: none` is the convention for "no DevOps work item yet" (id-or-none, never
 * blank). It is an honest answer, not a value, so it counts as missing here.
 */

const PLACEHOLDER = v => {
  const s = (v || '').trim();
  return !s || /\?/.test(s) || /^(unset|none)$/i.test(s) || /^pending/i.test(s);
};
const NORM = s => (s || '').toLowerCase()
  .replace(/\u00e6/g, 'ae').replace(/\u00f8/g, 'oe').replace(/\u00e5/g, 'aa')
  .replace(/[\s\-_/.]/g, '');

function TaskDims({ task, rule, onDone }) {
  const [fno, setFno] = useState('');
  const [act, setAct] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    setFno(PLACEHOLDER(task.fno_task) ? '' : task.fno_task);
    setAct(PLACEHOLDER(task.activity) ? '' : task.activity);
    setBusy(false);
  }, [task.slug]);

  const wants = new Set(rule ? rule.requires : []);
  const short = (wants.has('task') && !fno) || (wants.has('activity') && !act && !rule.activity);
  const save = async () => {
    setBusy(true);
    const j = await post('/api/task', { slug: task.slug, action: 'set-dims',
                                        fno_task: fno.trim() || 'none',
                                        activity: act.trim() });
    setBusy(false);
    toast(j.message || (j.ok ? 'saved' : 'failed'));
    if (j.ok) onDone();
  };

  return html`
    <div class=${'wtask' + (short ? ' short' : '')}>
      <div class="wtitle">${task.title || task.slug}
        <span class="sub">${task.state} · ${task.slug}</span></div>
      <div class="actrow">
        <span class="flabel" style="min-width:66px">F&O task</span>
        <input type="text" value=${fno} onInput=${e => setFno(e.target.value)}
               placeholder=${wants.has('task') ? 'required — the DevOps work item' : 'none'}
               aria-label=${'fno_task ' + task.slug}/>
        <span class="flabel" style="min-width:58px">Activity</span>
        <input type="text" value=${act} onInput=${e => setAct(e.target.value)}
               placeholder=${wants.has('task') ? 'F&O derives it'
                 : (rule && rule.activity) ? rule.activity + ' (customer default)' : 'activity id'}
               aria-label=${'activity ' + task.slug}/>
        <button class="act" disabled=${busy} onClick=${save}>Save</button>
      </div>
    </div>`;
}

function FnoReadiness({ D, customer, onDone }) {
  if (!customer) return null;
  const rule = (((D.entry || {}).rules) || {})[NORM(customer)] || null;
  const tasks = (D.targets || []).filter(t => t.project.startsWith('customers/' + customer + '/'));
  const wants = new Set(rule ? rule.requires : []);
  const shortOf = t => (wants.has('task') && PLACEHOLDER(t.fno_task))
    || (wants.has('activity') && PLACEHOLDER(t.activity) && !(rule && rule.activity));
  const short = tasks.filter(shortOf);

  return html`
    <section>
      <h2>F&O readiness — ${customer}</h2>
      <div class="card">
        <p class="sub" style="margin:0 0 8px">
          ${rule && rule.requires.length
            ? html`Every ${customer} time line must carry <b>${rule.requires.join(', ')}</b>
                   (<code>fno_requires</code> on the customer node; ops/time/README.md 4.1).`
            : html`No registration rule recorded for ${customer} — a line needs a Proj ID and
                   nothing more. Set <code>fno_requires</code> from a line's panel on
                   <a href="/time">Time</a> if that is wrong.`}
          ${rule && rule.activity
            ? html` The default activity is <code>${rule.activity}</code>.` : null}</p>
        ${!tasks.length
          ? html`<${Empty}>No open work-task under ${customer}.<//>`
          : html`
            <${Fragment}>
              <p class=${'sub' + (short.length ? ' accentink' : '')} style="margin:0 0 10px">
                ${short.length
                  ? html`<b>${short.length} of ${tasks.length}</b> open work-tasks cannot
                         produce an enterable line yet. Any time logged to them has to be
                         corrected day by day afterwards.`
                  : html`All ${tasks.length} open work-tasks carry what ${customer} registers
                         on, so time logged to them is enterable as written.`}</p>
              ${tasks.map(t => html`
                <${TaskDims} key=${t.slug} task=${t} rule=${rule} onDone=${onDone}/>`)}
            <//>`}
      </div>
    </section>`;
}

/* ---------- page ---------- */

function App() {
  const { data: D, err, stamp, reload, auto, setAuto } = useData('/api/data');
  const [sel, setSel] = useState(null);
  const [q, setQ] = useState('');
  const [mode, setMode] = useState('band');
  const [cust, setCust] = useState(null);
  const [state, setState] = useState(null);
  const [folded, toggleFold, expandAll] = useFolded();

  /* Everything the page lists, before the bar's filters -- what the bar counts. */
  const listed = useMemo(
    () => (D ? D.projects.filter(p => p.band !== 'workspace') : []), [D]);

  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return listed.filter(p => {
      if (cust && bucketOf(p) !== cust) return false;
      if (state && !p.counts[state]) return false;
      if (!needle) return true;
      return (label(p) + ' ' + p.key + ' ' + p.fno_code + ' ' + p.goal + ' ' + p.focus)
        .toLowerCase().includes(needle);
    });
  }, [listed, q, cust, state]);

  const counts = useMemo(() => {
    const n = { quiet: 0, inflight: 0, dormant: 0, asks: 0 };
    rows.forEach(p => { n[p.band] = (n[p.band] || 0) + 1; n.asks += p.counts.asks_unsent; });
    return n;
  }, [rows]);

  const tiles = [
    html`<${Tile} key="a" label="Projects" value=${rows.length} foot="excluding the workspace"/>`,
    html`<${Tile} key="i" label="In flight" value=${counts.inflight} foot="worked in 14 days"/>`,
    html`<${Tile} key="q" label="Gone quiet" value=${counts.quiet} hot=${counts.quiet > 0}
                  foot="active, untouched"/>`,
    html`<${Tile} key="k" label="Unsent asks" value=${counts.asks} hot=${counts.asks > 0}
                  foot="across these projects"/>`,
  ];

  return html`
    <${Shell} here="/projects" title="Projects"
              sub=${D ? plural(rows.length, 'project') : 'loading…'}
              stamp=${stamp} auto=${auto} onAuto=${() => setAuto(a => !a)} onRefresh=${reload}
              tiles=${tiles}>
      ${err ? html`<div class="alert">Cannot reach the server: ${err}</div>` : null}

      ${D ? html`<${FilterBar} projects=${listed} pick=${cust} onPick=${setCust}
                               state=${state} onState=${setState}/>` : null}

      <div class="filterbar">
        <span class="flabel">Group by</span>
        ${[['band', 'Activity'], ['status', 'Status']].map(([k, tx]) => html`
          <button key=${k} class=${'chip' + (mode === k ? ' on' : '')}
                  onClick=${() => setMode(k)}>${tx}</button>`)}
        ${folded.size ? html`
          <button class="chip" onClick=${expandAll}>Expand all (${folded.size} folded)</button>`
          : null}
        <span class="fsep"></span>
        <input type="search" placeholder="Filter projects…" value=${q}
               onInput=${e => setQ(e.target.value)}/>
      </div>

      ${D ? html`
        <${Fragment}>
          <div class="split-wide">
            <${Customers} customers=${D.customers} th=${D.thresholds}
                          picked=${cust === OWN ? null : cust} onPick=${setCust}/>
            <${Table} projects=${rows} th=${D.thresholds} onOpen=${setSel}
                      mode=${mode} folded=${folded} onToggle=${toggleFold}/>
          </div>
          <${FnoReadiness} D=${D} customer=${cust === OWN ? null : cust} onDone=${reload}/>
        <//>` : null}

      <${Drawer} open=${!!sel} onClose=${() => setSel(null)}>
        <${Detail} p=${sel} tasks=${D ? D.tasks : []}/>
      <//>
    <//>`;
}

render(html`<${App}/>`, document.getElementById('root'));
