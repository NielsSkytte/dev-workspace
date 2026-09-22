/* Today -- the day's moves, grouped by project.
 *
 * What belongs here is anything that wants a decision TODAY: a raw capture that has not
 * been routed, a task parked until now, an ask that was never sent, and work in
 * progress. A task with nothing to do today is not here; it is on Projects. That is the
 * whole rule, and it is why this page does not carry the full queue.
 *
 * Two payloads: /api/data for the tiles and the capture list, /api/today for the task
 * model with its progress dates. Both are memoised server-side.
 */
import {
  html, render, useState, useMemo, useEffect, Fragment,
  Shell, Tile, Drawer, Empty, useData, post, launch, toast, hrs, ago, plural,
} from './app.js';

const PROJECT_LABEL = key =>
  key.startsWith('customers/') ? key.slice('customers/'.length) : key;

/* A customer project bills to a task, so opening one switches the session's task;
   an internal project has no task-level tracking, so it just gets pointed at the file. */
const workPrompt = t => t.project.startsWith('customers/')
  ? '/switch-task ' + t.slug
  : 'Work on task ' + t.slug + ' (ops/tasks/' + t.state + '/' + t.slug
    + '.md): read its Progress block and start on Next 1.';

/* Every mechanical task change goes through one place: POST, report, reload. The server
   drops its memo on a write, so the reload already sees the new state. */
async function taskAct(slug, action, extra, done) {
  const j = await post('/api/task', Object.assign({ slug, action }, extra || {}));
  toast(j.message || (j.ok ? action : 'failed'));
  if (j.ok && done) done();
  return j.ok;
}

/* ---------- triage ---------- */

function TriageRow({ item, onWrite, root }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const write = async action => {
    setBusy(true);
    const j = await post('/api/todo', { line: item.line, action, raw: item.raw });
    toast(j.message || (j.ok ? action : 'failed'));
    setBusy(false);
    if (j.ok) onWrite();
  };

  return html`
    <div class="triage-row">
      <div class="triage-main">
        <span class="triage-age" title=${'captured ' + (item.date || 'undated')}>
          ${item.age === null ? '—' : item.age + 'd'}</span>
        <span class=${'triage-text' + (open ? ' open' : '')}
              title="click to expand" onClick=${() => setOpen(o => !o)}>${item.text}</span>
      </div>
      <div class="triage-act">
        <button class="mini primary" disabled=${busy}
                title="open a session at the workspace root seeded with /task, which runs the routing interview"
                onClick=${() => launch(root, 'claude', '/task ' + item.text)}>Make it a task</button>
        <button class="mini" disabled=${busy} title="handled -- mark the line done in ops/TODO.md"
                onClick=${() => write('tick')}>Tick</button>
        <button class="mini" disabled=${busy} title="not doing it -- strike the line out in ops/TODO.md"
                onClick=${() => write('drop')}>Drop</button>
        <button class="mini" title="copy the /task line so you can paste it into a session yourself"
                onClick=${async () => {
          try { await navigator.clipboard.writeText('/task ' + item.text); toast('Copied /task line'); }
          catch (e) { toast('Clipboard blocked — select the text instead'); }
        }}>Copy</button>
      </div>
    </div>`;
}

function Triage({ todos, root, onWrite }) {
  return html`
    <section>
      <h2>Needs triage${todos.length ? ' — ' + plural(todos.length, 'raw item') + ' waiting to become a task' : ''}</h2>
      <div class="card capped">
        ${todos.length
          ? todos.map(t => html`<${TriageRow} key=${t.line} item=${t} root=${root} onWrite=${onWrite}/>`)
          : html`<${Empty}>Nothing unprocessed — every captured item has been routed.<//>`}
      </div>
    </section>`;
}

/* ---------- task lines ---------- */

function ageClass(task) {
  const a = task.progress_age;
  if (task.stalled) return 'agechip stalled';
  if (task.parked) return 'agechip parked';
  if (a === null) return 'agechip';
  return a <= 2 ? 'agechip' : a <= 7 ? 'agechip a2' : a <= 21 ? 'agechip a3' : 'agechip a4';
}

function TaskLine({ task, onOpen, onReload, pathOf }) {
  const stop = fn => e => { e.stopPropagation(); fn(); };
  return html`
    <tr class="clickable" onClick=${() => onOpen(task)}>
      <td class="age">
        <span class=${ageClass(task)} title=${'progress ' + ago(task.progress_age)}>
          ${task.progress_age === null ? '—' : task.progress_age + 'd'}</span>
      </td>
      <td class="slug">
        <b>${task.title || task.slug}</b>
        <div class="t">${task.slug}</div>
      </td>
      <td class="next">${task.now || html`<span class="muted">no progress note yet</span>`}</td>
      <td class="rowact">
        <button class="act primary" title="open a session on this task"
                onClick=${stop(() => launch(pathOf(task.project), 'claude', workPrompt(task)))}>Work</button>
        <button class="act" title="mark it done and move the file to ops/tasks/done"
                onClick=${stop(() => taskAct(task.slug, 'done', null, onReload))}>Done</button>
        <button class="act" title="status and notes"
                onClick=${stop(() => onOpen(task))}>More…</button>
      </td>
    </tr>`;
}

/* A stacked row, not a table row: these groups sit in the narrow column, where three
   columns squeeze the title until it breaks mid-word. Project, then title, then the
   latest progress note clamped to three lines. */
function Group({ title, tasks, onOpen, hint }) {
  if (!tasks.length) return null;
  return html`
    <section>
      <h2>${title} — ${tasks.length}</h2>
      <div class="card capped">
        ${hint ? html`<p class="sub" style="margin:0 0 10px">${hint}</p>` : null}
        ${tasks.map(t => html`
          <div class="stackrow" key=${t.slug} onClick=${() => onOpen(t)}>
            <div class="stackhead">
              <span class="chip">${t.project ? PROJECT_LABEL(t.project) : 'workspace'}</span>
              ${t.now_date ? html`<span class="sub">${t.now_date}</span>` : null}
            </div>
            <b class="stacktitle">${t.title || t.slug}</b>
            ${t.now || t.waiting
              ? html`<p class="stacknote">${t.now || t.waiting}</p>`
              : html`<p class="stacknote muted">no progress note yet</p>`}
          </div>`)}
      </div>
    </section>`;
}

/* An ask row shows the ask, not the progress note: the row's job is to say what has to
   go out. A task can hold several asks; the first is shown and the rest are counted. */
function AskRow({ task, onOpen, onReload }) {
  const stop = fn => e => { e.stopPropagation(); fn(); };
  const rest = task.needs.length - 1;
  return html`
    <div class="stackrow" onClick=${() => onOpen(task)}>
      <div class="stackhead">
        <span class="chip">${task.project ? PROJECT_LABEL(task.project) : 'workspace'}</span>
        <button class="mini" style="margin-left:auto"
                title="the ask has gone out -- writes customer_ask: sent <today> to the task file"
                onClick=${stop(() => taskAct(task.slug, 'ask-sent', null, onReload))}>Ask sent</button>
        <button class="mini"
                title="the ask is no longer relevant, or it was wrong -- writes customer_ask: dropped and a dated Log line"
                onClick=${stop(() => taskAct(task.slug, 'ask-dropped', null, onReload))}>Not relevant</button>
      </div>
      <b class="stacktitle">${task.title || task.slug}</b>
      ${task.needs.length
        ? html`<p class="stacknote">${task.needs[0]}${rest > 0
            ? html`<span class="sub"> and ${rest} more on this task</span>` : null}</p>`
        : html`<p class="stacknote muted">Marked customer_ask: open, but the task lists nothing under Needs from customer.</p>`}
    </div>`;
}

function Asks({ tasks, onOpen, onReload }) {
  if (!tasks.length) return null;
  return html`
    <section>
      <h2>Unsent asks — ${tasks.length}</h2>
      <div class="card capped">
        <p class="sub" style="margin:0 0 10px">Each task below has customer_ask: open. The line is the first entry under Needs from customer.</p>
        ${tasks.map(t => html`<${AskRow} key=${t.slug} task=${t} onOpen=${onOpen} onReload=${onReload}/>`)}
      </div>
    </section>`;
}

function InProgress({ groups, onOpen, onLaunch, onReload, pathOf }) {
  if (!groups.length) {
    return html`
      <section>
        <h2>In progress</h2>
        <div class="card"><${Empty}>Nothing in progress. Pick something up from Projects.<//></div>
      </section>`;
  }
  return html`
    <section>
      <h2>In progress</h2>
      ${groups.map(g => html`
        <article key=${g.key} style="margin-bottom:12px">
          <div class="phead">
            <h2 style="text-transform:none;letter-spacing:0;font-size:16px;color:var(--ink)">
              ${PROJECT_LABEL(g.key)}</h2>
            <span class="meta">${g.fno_code || 'UNSET'}</span>
            <span class="actions">
              <button class="act" onClick=${() => onLaunch(g.path, 'claude')}>Session</button>
              <button class="act" onClick=${() => onLaunch(g.path, 'code')}>VS Code</button>
            </span>
          </div>
          <table>${g.tasks.map(t => html`
            <${TaskLine} key=${t.slug} task=${t} onOpen=${onOpen} onReload=${onReload}
                         pathOf=${pathOf}/>`)}</table>
        </article>`)}
    </section>`;
}

/* ---------- detail ---------- */

/* Status and a note, in the drawer where there is room for the two inputs the old
   popovers had to float. Mechanical changes only -- writing a Progress block or a Next
   step is a session's job, not a button's. */
function TaskActions({ task, onDone, pathOf }) {
  const [note, setNote] = useState('');
  const [when, setWhen] = useState('');
  const [who, setWho] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => { setNote(''); setWhen(''); setWho(''); }, [task.slug]);

  const run = (action, extra) => async () => {
    setBusy(true);
    const ok = await taskAct(task.slug, action, extra, onDone);
    setBusy(false);
    if (ok && action === 'comment') setNote('');
    if (ok && action === 'park') setWhen('');
    if (ok && action === 'wait') setWho('');
  };

  return html`
    <div class="block">
      <h4>Status</h4>
      <div class="rowacts" style="justify-content:flex-start">
        <button class="act primary" disabled=${busy}
                onClick=${() => launch(pathOf(task.project), 'claude', workPrompt(task))}>Work on it</button>
        <button class="act" disabled=${busy} onClick=${run('done')}>Done</button>
        ${task.state === 'open'
          ? html`<button class="act" disabled=${busy} onClick=${run('in-progress')}>In progress</button>`
          : html`<button class="act" disabled=${busy} onClick=${run('open')}>Back to open</button>`}
        ${task.parked
          ? html`<button class="act" disabled=${busy} onClick=${run('resume')}>Resume</button>` : null}
        ${task.customer_ask === 'open'
          ? html`<button class="act" disabled=${busy} onClick=${run('ask-sent')}>Ask sent</button>` : null}
        ${task.customer_ask === 'open'
          ? html`<button class="act" disabled=${busy}
                         title="no longer relevant, or wrong -- customer_ask: dropped"
                         onClick=${run('ask-dropped', note.trim() ? { text: note.trim() } : null)}>Not relevant</button>`
          : null}
        ${task.customer_ask.startsWith('sent')
          ? html`<button class="act" disabled=${busy} onClick=${run('ask-answered')}>Ask answered</button>` : null}
      </div>

      <div class="actrow">
        <input type="date" value=${when} onInput=${e => setWhen(e.target.value)}
               aria-label="resume on"/>
        <button class="act" disabled=${busy || !when} onClick=${run('park', { date: when })}>
          Postpone until</button>
      </div>

      <div class="actrow">
        <input type="text" placeholder="waiting on whom…" value=${who}
               onInput=${e => setWho(e.target.value)} aria-label="waiting on"/>
        <button class="act" disabled=${busy || !who.trim()}
                onClick=${run('wait', { waiting_on: who.trim() })}>Wait</button>
        <button class="act" disabled=${busy}
                onClick=${run('wait', { waiting_on: 'customer' })}>Wait: customer</button>
      </div>
    </div>

    <div class="block">
      <h4>Add a note</h4>
      <textarea class="notebox" placeholder="one line, dated into the task's Log…"
                value=${note} onInput=${e => setNote(e.target.value)}
                onKeyDown=${e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) run('comment', { text: note.trim() })(); }}></textarea>
      <div class="rowacts">
        <span class="sub" style="margin-right:auto">Ctrl+Enter saves</span>
        <button class="act primary" disabled=${busy || !note.trim()}
                onClick=${run('comment', { text: note.trim() })}>Add note</button>
      </div>
    </div>`;
}

function TaskDetail({ task, onReload, pathOf }) {
  if (!task) return null;
  return html`
    <h3>${task.title || task.slug}</h3>
    <p class="sub">${task.slug}</p>
    <dl class="kv">
      <dt>Project</dt><dd>${task.project || 'workspace'}</dd>
      <dt>State</dt><dd>${task.state}${task.parked ? ' (parked)' : ''}</dd>
      <dt>Progress</dt><dd>${task.now_date || '—'}${task.progress_age === null ? '' : ' · ' + ago(task.progress_age)}</dd>
      <dt>DevOps</dt><dd>${task.devops === 'none' ? html`<span class="muted">none</span>` : task.devops}</dd>
      ${task.waiting ? html`<dt>Waiting on</dt><dd>${task.waiting}</dd>` : null}
      ${task.resume_on ? html`<dt>Resume on</dt><dd>${task.resume_on}</dd>` : null}
      ${task.customer_ask ? html`<dt>Customer ask</dt><dd>${task.customer_ask}</dd>` : null}
    </dl>
    ${task.now ? html`<div class="block"><h4>Now</h4><p class="ink2">${task.now}</p></div>` : null}
    ${task.next.length ? html`
      <div class="block"><h4>Next</h4>
        <ul class="tight">${task.next.map((n, i) => html`<li key=${i}>${n}</li>`)}</ul></div>` : null}
    ${task.needs.length ? html`
      <div class="block"><h4>Needs from customer</h4>
        <ul class="tight">${task.needs.map((n, i) => html`<li key=${i}>${n}</li>`)}</ul></div>` : null}
    <${TaskActions} task=${task} onDone=${onReload} pathOf=${pathOf}/>
    <div class="block"><code>${task.path}</code></div>`;
}

/* ---------- page ---------- */

/* What each session is producing, against what it started with.
 *
 * A session tags its time with the work-task it holds (ADR-003). When it holds none, or
 * holds one belonging to another customer, or wanders into a customer node, the turn is
 * still billed -- just without the dimension that customer requires. Nobody finds out
 * until the month is entered, which is weeks after the only moment the answer was cheap.
 *
 * The verdict is `ops/lib/attribution.drift`, the same call the time hook makes per turn,
 * so the page and the nudge cannot say different things.
 */
function Sessions({ D, onLaunch }) {
  const rows = (D.active_sessions || []).filter(s => s.turns > 0);
  if (!rows.length) return null;
  const bad = rows.filter(s => s.drift.length);
  const order = rows.slice().sort((a, b) =>
    (b.drift.length > 0) - (a.drift.length > 0) || b.turns - a.turns);

  return html`
    <section>
      <h2>Sessions today${bad.length
        ? html` — <b class="accentink">${bad.length} not billing cleanly</b>` : ' — all clean'}</h2>
      <div class="card">
        <p class="sub" style="margin:0 0 8px">What each session has tagged its time with,
          against what it started with. A row in accent will produce an F&O line that
          cannot be entered as it stands.</p>
        <div style="overflow-x:auto"><table class="autable">
          <thead><tr><th>Session</th><th>Started with</th><th>Landing on</th>
            <th class="r">Turns</th><th>State</th><th>Verdict</th></tr></thead>
          <tbody>${order.map(s => html`
            <tr key=${s.session} class=${s.drift.length ? 'short' : ''}>
              <td><code>${s.session}</code></td>
              <td>${s.slug
                ? html`<span title=${s.held_project}>${s.slug}</span>`
                : html`<span class="muted">no task held</span>`}</td>
              <td>${s.landed.map(l => html`
                <div key=${l.project}>${l.project}
                  <span class="muted">x${l.turns}</span></div>`)}</td>
              <td class="r">${s.turns}</td>
              <td>${s.state === 'live' ? html`<span class="pill warn">live</span>`
                : html`<span class="muted">${s.state}</span>`}</td>
              <td class="sub">${s.drift.length
                ? s.drift.map((d, i) => html`
                    <div key=${i}><b class="accentink">${d.why}</b><br/>${d.fix}</div>`)
                : html`<span class="muted">enterable as written</span>`}</td>
            </tr>`)}</tbody>
        </table></div>
      </div>
    </section>`;
}

function App() {
  const data = useData('/api/data');
  const brief = useData('/api/today');
  const [sel, setSel] = useState(null);

  const D = data.data;
  const B = brief.data;

  const model = useMemo(() => {
    if (!B) return { dueBack: [], asks: [], groups: [], inProgress: 0 };
    const byKey = {};
    (D ? D.projects : []).forEach(p => { byKey[p.key] = p; });
    const all = [];
    B.projects.forEach(p => p.tasks.forEach(t => all.push(t)));
    B.workspace_tasks.forEach(t => all.push(t));
    const groups = B.projects
      .map(p => ({
        key: p.key,
        fno_code: p.fno_code,
        path: (byKey[p.key] || {}).path || '',
        tasks: p.tasks.filter(t => t.state === 'in-progress' && !t.parked),
      }))
      .filter(g => g.tasks.length)
      .sort((a, b) => a.key.localeCompare(b.key));
    return {
      dueBack: all.filter(t => t.due_back),
      asks: all.filter(t => t.ask_unsent),
      groups,
      inProgress: groups.reduce((n, g) => n + g.tasks.length, 0),
    };
  }, [B, D]);

  /* project key -> folder on disk; a workspace task has no project, so it opens at the root */
  const pathOf = useMemo(() => {
    const m = {};
    (D ? D.projects : []).forEach(x => { m[x.key] = x.path; });
    return key => m[key] || (D ? D.root : '');
  }, [D]);

  const todos = D ? D.todos : [];
  /* Sessions that produced time today, and how many of them will produce a line that
     cannot be entered. The count on the tile is the second number, because the first is
     not a thing to act on. */
  const sessions = D ? (D.active_sessions || []).filter(s => s.turns > 0) : [];
  const drifting = sessions.filter(s => s.drift.length);

  const tiles = [
    html`<${Tile} key="h" label="Hours today" value=${D ? hrs(D.totals.today) : '—'}
                  foot=${D ? 'week ' + hrs(D.totals.week_billable + D.totals.week_internal) + ' h' : ''}/>`,
    html`<${Tile} key="s" label="Sessions today" value=${D ? sessions.length : '—'}
                  hot=${drifting.length > 0}
                  foot=${drifting.length
                    ? plural(drifting.length, 'not billing cleanly')
                    : 'all billing cleanly'}/>`,
    html`<${Tile} key="a" label="Unsent asks" value=${model.asks.length}
                  hot=${model.asks.length > 0} foot="customer_ask: open"/>`,
    html`<${Tile} key="t" label="Triage" value=${todos.length} hot=${todos.length > 0}
                  foot="raw captures"/>`,
  ];

  const reloadAll = () => { data.reload(); brief.reload(); };
  const toggleAuto = () => { data.setAuto(a => !a); brief.setAuto(a => !a); };

  return html`
    <${Shell} here="/" title="Today"
              sub=${B ? B.weekday + ' ' + B.today : 'loading the day brief…'}
              stamp=${data.stamp} auto=${data.auto} onAuto=${toggleAuto} onRefresh=${reloadAll}
              tiles=${tiles}>
      ${data.err || brief.err
        ? html`<div class="alert">Cannot reach the server: ${data.err || brief.err}</div>` : null}

      <div class="split">
        <${Triage} todos=${todos} root=${D ? D.root : ''} onWrite=${() => data.reload()}/>
        ${model.dueBack.length || model.asks.length ? html`
          <div>
            <${Group} title="Due back today" tasks=${model.dueBack} onOpen=${setSel}
                      hint="Parked until today. Clear resume_on once the task is moving again."/>
            <${Asks} tasks=${model.asks} onOpen=${setSel} onReload=${reloadAll}/>
          </div>` : null}
      </div>

      <${InProgress} groups=${model.groups} onOpen=${setSel} onReload=${reloadAll}
                     pathOf=${pathOf} onLaunch=${(p, mode) => p && launch(p, mode)}/>

      ${D ? html`<${Sessions} D=${D}/>` : null}

      <${Drawer} open=${!!sel} onClose=${() => setSel(null)}>
        <${TaskDetail} task=${sel} pathOf=${pathOf}
                       onReload=${() => { reloadAll(); setSel(null); }}/>
      <//>
    <//>`;
}

render(html`<${App}/>`, document.getElementById('root'));
