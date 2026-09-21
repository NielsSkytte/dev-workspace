/* Time — getting the month into F&O.
 *
 * The page answers one question in order: what do I type, is any of it missing something
 * F&O requires, and how do I fix that. Everything else on the page is evidence for those
 * three.
 *
 *   Enter   the entry surface. One block per internal company, because F&O takes one
 *           timesheet per company, with the readiness gate above it and the week's
 *           evidence below it. Copy rows or download the workbook.
 *   Review  the month's shape: hours, projects, internal position, hygiene.
 *
 * Hours are never invented here. A month block shows the timesheet as it stands; a week
 * block shows the F&O ENTRY figure, which sits in the band between work time and the value
 * model's ceiling (ADR-004), distributed per F&O dimension. Two numbers for one line is how
 * a month gets entered wrong, so the week is the one source for what gets typed.
 */
import {
  html, render, useState, useMemo, useEffect, useRef, Fragment,
  Shell, Tile, Drawer, Empty, useData, post, toast, hrs, label,
} from './app.js';

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'];
const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const pad = n => String(n).padStart(2, '0');

/* Field-wise, never through Date(string) — that reads the date as UTC and shifts it. */
const dowOf = ds => {
  const [y, m, d] = ds.split('-').map(Number);
  return new Date(y, m - 1, d).getDay();
};
const dowName = ds => DOW[dowOf(ds)];
const isWeekend = ds => dowOf(ds) === 0 || dowOf(ds) === 6;
const shortDay = ds => `${+ds.slice(8, 10)} ${MONTHS[+ds.slice(5, 7) - 1].slice(0, 3)}`;

/* Every date in the selected month, so an untracked day renders as an explicit 0
   rather than vanishing from the axis. */
function periodDays(today, back) {
  const [Y, M] = today.split('-').map(Number);
  const y = M - back > 0 ? Y : Y - 1;
  const m = ((M - 1 - back) % 12 + 12) % 12 + 1;
  const days = [];
  for (let d = 1; d <= new Date(y, m, 0).getDate(); d++) days.push(`${y}-${pad(m)}-${pad(d)}`);
  return { days, label: `${MONTHS[m - 1]} ${y}`, key: `${y}-${pad(m)}` };
}

const scopeOf = k => (k === 'Dev' ? 'dev' : k.startsWith('own/') ? 'own' : 'customers');
const nameOf = f => (f === 'INTERNAL' ? 'Internal' : f === '' ? 'No company' : f);
const custOf = r => r.customer || (r.firma === 'INTERNAL' ? '(internal)' : '(none)');
const shortProject = p => p.replace(/^customers\//, '');
/* The line as the server knows it, so an edit names exactly one row of one day file. */
const rowKey = r => [r.date, r.project, r.proj_id || '', r.activity || '',
                     r.fno_task || ''].join('|');
const sessKey = r => `${r.date}|${r.project}|${r.ws_activity || ''}|${r.ws_fno_task || ''}`.toLowerCase();

/* The server's own customer key, so the page can look a rule up by name. Kept in step with
   lib/fno.norm: fold the Danish letters, drop the separators. */
const normCust = s => (s || '').toLowerCase()
  .replace(/\u00e6/g, 'ae').replace(/\u00f8/g, 'oe').replace(/\u00e5/g, 'aa')
  .replace(/[\s\-_/.]/g, '');

/* UNSET, PENDING, `none`, a bare `?` -- the server blanks these on an entry row, but a
   project's fno_code and a task's fno_task are shown raw, and a placeholder in an input
   invites saving it back. */
const blankIfPlaceholder = v => {
  const s = (v || '').trim();
  return (!s || /\?/.test(s) || /^(unset|none)$/i.test(s) || /^pending/i.test(s)) ? '' : s;
};

/* ---------- the F&O entry figure ----------
   Work time is the floor, value time the ceiling, and turns+files decide how far up the band
   a line sits. Both counted PER WORK HOUR, not raw: raw counts rise with the length of the
   line, so a long quiet line would out-score a short dense one and the column would just
   re-measure duration. The saturating curve means more evidence always moves toward value
   time but never past it — value time stays the maximum that can ever be registered. */
const TURNS_PER_H = 10, FILES_PER_H = 8;   // the p90 densities: one unit of evidence each
const entryOf = l => {
  const work = l.claimed || 0, value = l.weighted || 0;
  if (!work || value <= work) return work;         // no band to sit in
  const x = l.turns / (TURNS_PER_H * work) + l.files / (FILES_PER_H * work);
  return Math.round((work + (1 - Math.exp(-x)) * (value - work)) * 4) / 4;  // F&O takes 0.25 h
};
const entrySum = ls => Math.round(ls.reduce((s, l) => s + entryOf(l), 0) * 100) / 100;

/* ---------- week helpers ---------- */

const auRange = w => {
  const end = w.friday || w.end;
  return w.start.slice(5, 7) === end.slice(5, 7)
    ? `${+w.start.slice(8, 10)}–${shortDay(end)}` : `${shortDay(w.start)} – ${shortDay(end)}`;
};

/* The entry range key for one ISO week inside one month. A week wholly in that month IS its
   own segment ('2026-W36'); a straddling one has a per-month segment ('2026-W31@2026-08'); a
   week that never touches the month has neither, and drops out of the picker. */
function auKey(D, wk, mkey) {
  const R = (D.entry && D.entry.ranges) || {};
  if (R[wk + '@' + mkey]) return wk + '@' + mkey;
  const days = R[wk];
  return (days && days[0].slice(0, 7) === mkey) ? wk : null;
}

/* A straddling week cut down to the days inside the selected month. The entry blocks are
   already clipped by their range key; without this the sections below them still showed the
   whole ISO week. Everything derived from days or lines is recomputed — a total that still
   counted the dropped days would be worse than not clipping at all. */
function clipWeek(w, allowed, today) {
  const days = w.days.filter(d => allowed.has(d.date));
  const lines = w.lines.filter(l => allowed.has(l.date));
  const sum = f => Math.round(days.reduce((s, d) => s + d[f], 0) * 100) / 100;
  const n = f => days.reduce((s, d) => s + d[f], 0);
  const target = Math.round(days.reduce((s, d) => s + d.target, 0) * 100) / 100;
  const claimed = sum('claimed');
  const ex = w.exceptions;
  return Object.assign({}, w, {
    days, lines, target,
    spill: (w.spill || []).filter(s => allowed.has(s.date)),
    running: days.some(d => d.date === today),
    totals: {
      keyboard: sum('keyboard'), measured: sum('measured'), claimed, weighted: sum('weighted'),
      turns: n('turns'), stretches: n('stretches'), t5: n('t5'),
      billable: Math.round(lines.filter(l => l.billable)
        .reduce((s, l) => s + l.claimed, 0) * 100) / 100,
      internal: Math.round(lines.filter(l => !l.billable)
        .reduce((s, l) => s + l.claimed, 0) * 100) / 100,
      coverage: target ? Math.round(1000 * claimed / target) / 10 : null,
      short: Math.round(Math.max(0, target - claimed) * 100) / 100,
    },
    exceptions: {
      under: (ex.under || []).filter(x => allowed.has(x.date)),
      unaccounted: (ex.unaccounted || []).filter(d => allowed.has(d)),
      unfinalized: (ex.unfinalized || []).filter(d => allowed.has(d)),
      overCap: (ex.overCap || []).filter(d => allowed.has(d)),
    },
  });
}

/* Distribute a dimension's F&O entry total across its rows in proportion to their work
   hours, rounded to the 0.25 h F&O step, with the last row absorbing the remainder so the
   block still sums to the entry total exactly. Consolidation only moves hours BETWEEN days
   within a dimension, so the dimension total is the thing that must survive. */
function scaleRows(rows, scale) {
  if (!scale) return rows;
  const dk = r => `${r.project}|${r.activity || ''}|${r.fno_task || ''}`;
  const out = rows.map(r => Object.assign({}, r, { work: r.hours }));
  const groups = {};
  out.forEach(r => { (groups[dk(r)] || (groups[dk(r)] = [])).push(r); });
  for (const k in groups) {
    const g = groups[k], s = scale[k];
    if (!s || !s.work) continue;
    const work = g.reduce((a, r) => a + r.hours, 0);
    if (!work) continue;
    let left = Math.round(s.entry * 4) / 4;
    g.forEach((r, i) => {
      if (i === g.length - 1) { r.hours = Math.round(left * 100) / 100; return; }
      const v = Math.round(s.entry * (r.hours / work) * 4) / 4;
      r.hours = v; left = Math.round((left - v) * 100) / 100;
    });
  }
  return out;
}

/* ---------- readiness ---------- */

function Ready({ rows, onPick, periodLabel }) {
  const short = rows.filter(r => (r.missing || []).length);
  const hours = Math.round(short.reduce((s, r) => s + (r.work || r.hours), 0) * 100) / 100;
  if (!short.length) {
    return html`
      <div class="card ausec">
        <h3>Ready to enter</h3>
        <p class="sub" style="margin:0">Every line in ${periodLabel} carries what F&O asks of
          it — company, Proj ID, and whatever the customer registers on.</p>
      </div>`;
  }
  const byWhat = {};
  short.forEach(r => (r.missing || []).forEach(m => {
    const k = r.project + '\u0000' + m.label;
    const g = byWhat[k] || (byWhat[k] = { project: r.project, label: m.label, why: m.why,
                                          hours: 0, rows: [] });
    g.hours = Math.round((g.hours + (r.work || r.hours)) * 100) / 100;
    g.rows.push(r);
  }));
  const groups = Object.values(byWhat).sort((a, b) => b.hours - a.hours);
  return html`
    <div class="card ausec">
      <h3>Not ready to enter — ${short.length} line${short.length === 1 ? '' : 's'}, ${hrs(hours)} h</h3>
      <p class="sub">What the customer's own registration rule asks for and the line cannot
        supply (<code>fno_requires</code> on the customer node; ops/time/README.md 4.1). Pick a
        line to fill it in.</p>
      <div style="overflow-x:auto"><table class="autable">
        <thead><tr><th>Project</th><th>Missing</th><th class="r">Hours</th>
          <th class="r">Lines</th><th>Why</th></tr></thead>
        <tbody>${groups.map(g => html`
          <tr key=${g.project + g.label} class="clickable" onClick=${() => onPick(g.rows[0])}>
            <td>${shortProject(g.project)}</td>
            <td><b class="accentink">${g.label}</b></td>
            <td class="r">${hrs(g.hours)}</td>
            <td class="r muted">${g.rows.length}</td>
            <td class="sub">${g.why}</td>
          </tr>`)}</tbody>
      </table></div>
    </div>`;
}

/* ---------- the line editor ----------
   Two grains, both offered. Correcting the day fixes the hours being entered now; setting
   the field on the project or the customer stops the gap coming back next month. */

/* One `key: value` on one file, with what it is worth saying about it. */
function FieldRow({ label: lab, value, onInput, onSave, busy, hint, placeholder, action }) {
  return html`
    <${Fragment}>
      <div class="actrow">
        <span class="flabel" style="min-width:104px">${lab}</span>
        <input type="text" value=${value} placeholder=${placeholder || ''}
               onInput=${e => onInput(e.target.value)} aria-label=${lab}/>
        <button class="act" disabled=${busy} onClick=${onSave}>${action || 'Set'}</button>
      </div>
      ${hint ? html`<p class="sub" style="margin:2px 0 0 112px">${hint}</p>` : null}
    <//>`;
}

/* Where an F&O dimension comes from, and setting it there.
 *
 * The day correction above fixes the hours being entered now. This fixes the reason, and
 * each field belongs to a different thing:
 *
 *   Proj ID      the project's `## Identity` fno_code
 *   Activity     the task's `activity:`, or the customer's fno_activity as the default
 *   Task         the task's `fno_task:` -- the linked ADO work item
 *   Beskrivelse  the project's fno_description, since it carries the engagement
 *
 * In F&O a Task carries its own Activity, so a customer registering on task wants only the
 * task and an invented activity there is noise at best (Carl Ras, ops/time/README.md 4.1).
 * A customer with activities and no tasks -- Aeven -- wants only the activity, and there is
 * no task to hang it on, so it goes on the customer as the default for every line.
 */
function SourceFixes({ row, D, onDone }) {
  const [code, setCode] = useState('');
  const [defAct, setDefAct] = useState('');
  const [req, setReq] = useState('');
  const [desc, setDesc] = useState('');
  const [dims, setDims] = useState({});
  const [busy, setBusy] = useState(false);

  const proj = (D.projects || []).find(p => p.key === row.project);
  const rule = row.customer ? ((D.entry.rules || {})[normCust(row.customer)] || null) : null;
  /* Every task that could carry this line's sub-dimensions: the project's open and
     in-progress ones, plus whatever the heartbeats behind this line were actually tagged
     with -- which may be a task that has since been closed. */
  const tagged = new Set((((D.lineSessions || {})[sessKey(row)] || {}).blocks || [])
    .map(b => b.task).filter(Boolean));
  const tasks = (D.targets || []).filter(x => x.project === row.project || tagged.has(x.slug));

  useEffect(() => {
    setCode(proj ? blankIfPlaceholder(proj.fno_code) : '');
    setDefAct(rule ? rule.activity : '');
    setReq((row.requires || []).join(', '));
    setDesc((proj && proj.fno_description) || (rule && rule.description) || '');
    const d = {};
    tasks.forEach(x => {
      d[x.slug] = { activity: blankIfPlaceholder(x.activity),
                    fno_task: blankIfPlaceholder(x.fno_task) };
    });
    setDims(d);
    setBusy(false);
  }, [rowKey(row)]);

  const run = async (body, url) => {
    setBusy(true);
    const j = await post(url || '/api/fno', body);
    setBusy(false);
    toast(j.message || (j.ok ? 'saved' : 'failed'));
    if (j.ok) onDone();
  };
  const field = (kind, target, f, value) => run({ kind, target, field: f, value });
  const edit = (slug, f, v) => setDims(d => ({ ...d, [slug]: { ...d[slug], [f]: v } }));

  const needs = new Set((row.missing || []).map(m => m.field));
  const onTask = (row.requires || []).includes('task');

  return html`
    <div class="block">
      <h4>Set it at the source</h4>
      <p class="sub" style="margin:0 0 10px">The day fix above covers the hours you are
        entering now; these fix the reason, so next month's lines carry it themselves.
        In F&O a <b>Task</b> brings its own <b>Activity</b> — set the task where the customer
        registers on tasks, and the activity where there are only activities.</p>

      ${proj ? html`
        <${Fragment}>
          <div class="srchead">Project <code>${row.project}</code></div>
          <${FieldRow} label="fno_code" value=${code} onInput=${setCode} busy=${busy}
                       placeholder="e.g. 230-02"
                       hint=${needs.has('proj_id') ? 'the Proj ID this line is missing' : null}
                       onSave=${() => field('project', row.project, 'fno_code', code.trim())}/>
          ${(row.requires || []).includes('description') ? html`
            <${FieldRow} label="fno_description" value=${desc} onInput=${setDesc} busy=${busy}
                         placeholder="&lt;number&gt; &lt;title&gt;"
                         hint="the Beskrivelse; it carries the engagement, so it lives on the project"
                         onSave=${() => field('project', row.project, 'fno_description', desc.trim())}/>`
            : null}
        <//>` : null}

      ${row.customer ? html`
        <${Fragment}>
          <div class="srchead">Customer <code>customers/${row.customer}</code></div>
          <${FieldRow} label="fno_activity" value=${defAct} onInput=${setDefAct} busy=${busy}
                       placeholder="e.g. 111749"
                       hint=${onTask
                         ? 'this customer registers on task, so F&O derives the activity — leave it blank'
                         : `the default Activity for every ${row.customer} line that has none of its own`}
                       onSave=${() => field('customer', row.customer, 'fno_activity', defAct.trim())}/>
          <${FieldRow} label="fno_requires" value=${req} onInput=${setReq} busy=${busy}
                       placeholder="task, activity, description"
                       hint="what a line for this customer must carry before it can be entered"
                       onSave=${() => field('customer', row.customer, 'fno_requires', req.trim())}/>
        <//>` : null}

      <div class="srchead">Tasks on this project</div>
      ${!tasks.length ? html`
        <p class="sub" style="margin:0">No open task on ${shortProject(row.project)}.
          ${onTask ? ' This customer registers on task, so the work needs one before its time can be entered — open one in Azure DevOps and put the id on a task file.' : ''}</p>`
        : tasks.map(x => html`
          <div key=${x.slug} class="srctask">
            <div class="srctitle">${x.title || x.slug}
              <span class="sub">${x.state}${tagged.has(x.slug) ? ' · tagged on this line' : ''}</span></div>
            <div class="actrow">
              <span class="flabel" style="min-width:56px">Task</span>
              <input type="text" value=${(dims[x.slug] || {}).fno_task || ''}
                     placeholder="ADO work item, or none"
                     onInput=${e => edit(x.slug, 'fno_task', e.target.value)}
                     aria-label="fno_task"/>
              <span class="flabel" style="min-width:56px">Activity</span>
              <input type="text" value=${(dims[x.slug] || {}).activity || ''}
                     placeholder=${onTask ? 'F&O derives it' : 'activity id'}
                     onInput=${e => edit(x.slug, 'activity', e.target.value)}
                     aria-label="activity"/>
              <button class="act" disabled=${busy} onClick=${() => run({
                slug: x.slug, action: 'set-dims',
                fno_task: ((dims[x.slug] || {}).fno_task || '').trim() || 'none',
                activity: ((dims[x.slug] || {}).activity || '').trim(),
              }, '/api/task')}>Save</button>
            </div>
          </div>`)}
      <p class="sub" style="margin:8px 0 0">A task's dimensions reach every line tagged with
        it, including today's, which is what makes this the fix and the correction above the
        stopgap. A line worked with no task tagged is not reached — correct its day.</p>
    </div>`;
}

function LineEditor({ row, raw, D, onDone }) {
  const [pid, setPid] = useState('');
  const [act, setAct] = useState('');
  const [task, setTask] = useState('');
  const [hours, setHours] = useState('');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);

  const k = row ? rowKey(row) : '';
  useEffect(() => {
    if (!row) return;
    setPid(row.proj_id || ''); setAct(row.activity || ''); setTask(row.fno_task || '');
    setHours(String(raw ? raw.hours : row.hours)); setNote('');
  }, [k]);
  if (!row) return null;

  const proj = (D.projects || []).find(p => p.key === row.project);
  const missing = row.missing || [];
  const scaled = row.work !== undefined && row.work !== row.hours;

  const changed = raw && (pid !== (raw.ws_proj_id || '') || act !== (raw.ws_activity || '')
    || task !== (raw.ws_fno_task || '') || String(raw.hours) !== hours.trim());

  const run = async (fn, ok) => {
    setBusy(true);
    const j = await fn();
    setBusy(false);
    toast(j.message || (j.ok ? ok : 'failed'));
    if (j.ok) onDone();
  };

  /* The row is named by what the timesheet FILE holds (`ws_*`), not by what the page shows:
     a Proj ID can have come from the sheet and an activity from the customer rule, and
     neither is in the file. */
  const correct = () => run(() => post('/api/timesheet', {
    date: raw.date,
    row: { project: raw.project, proj_id: raw.ws_proj_id, activity: raw.ws_activity,
           fno_task: raw.ws_fno_task },
    set: { proj_id: pid.trim(), activity: act.trim(), fno_task: task.trim(),
           hours: Number(hours) },
    note: note.trim(),
  }), 'corrected');

  /* What this line was: the sessions behind it and what the memory hook recorded being
     said in them. A line that reads "Carl-Ras / – / –" says nothing, and that is exactly
     where deciding which task it belongs to is hardest. */
  const sess = ((D.lineSessions || {})[sessKey(row)] || {}).blocks || [];

  return html`
    <h3>${shortProject(row.project)}</h3>
    <p class="sub" style="margin:2px 0 12px">
      ${dowName(row.date)} ${row.date} · ${nameOf(row.firma)}
      ${row.customer ? ' · ' + row.customer : ''} · <b>${hrs(row.hours)} h</b>
      ${scaled ? html` <span class="muted">(F&O entry; work time ${hrs(row.work)} h)</span>` : null}
      ${row.no_charge ? html` · <b class="accentink">No charge</b>` : null}</p>

    ${missing.length ? html`
      <div class="block">
        <h4>F&O will not take this line yet</h4>
        <ul class="tight">${missing.map(m => html`
          <li key=${m.field}><b class="accentink">${m.label}</b> — ${m.why}</li>`)}</ul>
      </div>` : null}

    ${row.live ? html`
      <div class="block">
        <h4>Correct the day</h4>
        <p class="sub" style="margin:0">${row.date} is still accruing — there is no finalized
          timesheet file to correct yet. Close it with <code>/log</code> (or
          <code>python ops/time/rollup.py</code>) and it becomes editable. The source fixes
          below apply now and will be picked up when the day is written.</p>
      </div>`
      : !raw ? html`
      <div class="block">
        <h4>Correct the day</h4>
        <p class="sub" style="margin:0">This line has been consolidated onto another date, so
          there is no single timesheet row behind it. Turn <b>Consolidated</b> off to correct
          it.</p>
      </div>`
      : raw.ambiguous ? html`
      <div class="block">
        <h4>Correct the day</h4>
        <p class="sub" style="margin:0">Two timesheet lines on ${raw.date} resolve to this
          one row, so there is no single line to change. Edit
          <code>ops/time/timesheet/${raw.date.slice(0, 7)}/${raw.date}.md</code> by hand.</p>
      </div>` : html`
      <div class="block">
        <h4>Correct ${raw.date}</h4>
        <p class="sub" style="margin:0 0 8px">Writes
          <code>ops/time/timesheet/${raw.date.slice(0, 7)}/${raw.date}.md</code> and records the
          correction underneath, the way the file says to.</p>
        <div class="actrow"><span class="flabel" style="min-width:64px">Proj ID</span>
          <input type="text" value=${pid} onInput=${e => setPid(e.target.value)}
                 placeholder="e.g. 230-02" aria-label="Proj ID"/></div>
        <div class="actrow"><span class="flabel" style="min-width:64px">Activity</span>
          <input type="text" value=${act} onInput=${e => setAct(e.target.value)}
                 placeholder="blank if F&O derives it" aria-label="Activity"/></div>
        <div class="actrow"><span class="flabel" style="min-width:64px">Task</span>
          <input type="text" value=${task} onInput=${e => setTask(e.target.value)}
                 placeholder="the linked ADO work item" aria-label="Task"/></div>
        <div class="actrow"><span class="flabel" style="min-width:64px">Hours</span>
          <input type="text" value=${hours} onInput=${e => setHours(e.target.value)}
                 aria-label="Hours"/>
          <span class="sub">work time, 0.25 h steps</span></div>
        <div class="actrow"><span class="flabel" style="min-width:64px">Why</span>
          <input type="text" value=${note} onInput=${e => setNote(e.target.value)}
                 placeholder="goes into the correction note" aria-label="Why"/></div>
        <div class="rowacts">
          <button class="act primary" disabled=${busy || !changed}
                  onClick=${correct}>Correct this day</button>
        </div>
      </div>`}

    <${SourceFixes} row=${row} D=${D} onDone=${onDone}/>

    <div class="block">
      <h4>What this line was</h4>
      ${sess.length ? sess.map((b, i) => html`
        <div key=${i} class="tsess"><b>${hrs(b.hours)} h</b> · ${b.turns} turn${b.turns === 1 ? '' : 's'}
          · <span class="muted">${b.task || 'no task tagged'}</span>
          ${(b.lines || []).map((t, j) => html`<div key=${j} class="tturn">${t}</div>`)}
        </div>`)
        : html`<p class="sub" style="margin:0">No session evidence for this line.</p>`}
    </div>

    <div class="block"><code>${row.project}</code></div>`;
}

/* ---------- the entry surface ---------- */

function EntryBlocks({ D, rows, periodLabel, fileName, scaled, lead, gate,
                       off, setOff, custOff, setCustOff, onPick }) {
  const allFirmas = [...new Set(rows.map(r => r.firma))]
    .sort((a, b) => (a === 'INTERNAL') - (b === 'INTERNAL') || (a === '') - (b === '')
      || a.localeCompare(b));
  const allCusts = [...new Set(rows.filter(r => !off.has(r.firma)).map(custOf))].sort();
  const visible = r => !off.has(r.firma) && !custOff.has(custOf(r));
  const hoursOf = f => rows.filter(r => r.firma === f).reduce((s, r) => s + r.hours, 0);
  const custHours = c => rows.filter(r => custOf(r) === c).reduce((s, r) => s + r.hours, 0);
  /* A company whose every customer is filtered out drops out too — an empty block reads
     as a bug. */
  const firmas = allFirmas.filter(f => !off.has(f) && rows.some(r => r.firma === f && visible(r)));
  const shown = rows.filter(visible).reduce((s, r) => s + r.hours, 0);
  const total = rows.reduce((s, r) => s + r.hours, 0);
  const E = D.entry;

  /* MUST match block()'s filter exactly, customer chips included — what you take away is
     what you see. Filtering on firma alone put deselected customers on the clipboard
     invisibly, which is an over-registration straight into a production ERP. */
  const rowsFor = f => rows.filter(r => r.firma === f && !custOff.has(custOf(r)));

  const copy = async f => {
    const rs = rowsFor(f);
    const txt = ['Date\tCustomer\tProject\tProj ID\tActivity\tTask\tDescription\tHours']
      .concat(rs.map(r => [r.date, r.customer || '', shortProject(r.project), r.proj_id || '',
        r.activity || '', r.fno_task || '', r.description || '', hrs(r.hours)].join('\t')))
      .join('\n');
    try {
      await navigator.clipboard.writeText(txt);
      toast(`Copied ${rs.length} rows for ${nameOf(f)}`);
    } catch (e) { toast('Copy failed: ' + e.message); }
  };

  const excel = async f => {
    const rs = f === null ? rows.filter(visible) : rowsFor(f);
    const name = `${fileName}-${f === null ? 'all' : (nameOf(f) || 'none')}`;
    try {
      const r = await fetch('/api/xlsx', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, title: periodLabel, rows: rs }),
      });
      if (!r.ok) { toast((await r.json()).message || 'export failed'); return; }
      const url = URL.createObjectURL(await r.blob());
      const a = document.createElement('a');
      a.href = url; a.download = name + '.xlsx';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 4000);
      toast(`${rs.length} rows to ${name}.xlsx`);
    } catch (e) { toast('Export failed: ' + e.message); }
  };

  /* Per-company totals, deliberately covering EVERY company in the period regardless of the
     filter — this is the reconciliation figure (one F&O timesheet per company), not a view of
     the current selection. Line counts follow the Consolidated toggle, so they say how many
     lines you will actually type. */
  const enterable = allFirmas.filter(f => f !== 'INTERNAL');
  const nOf = f => rows.filter(r => r.firma === f).length;
  const totRow = (l, n, v, note, strong) => html`
    <tr key=${l} class=${strong ? 'autot grand' : ''}>
      <td>${l}</td><td class="muted">${n} line${n === 1 ? '' : 's'}</td>
      <td class="r">${hrs(v)} h</td><td class="sub">${note || ''}</td></tr>`;

  const block = f => {
    const rs = rowsFor(f);
    const tot = rs.reduce((s, r) => s + r.hours, 0);
    const title = f === 'INTERNAL' ? 'Internal (Dev / own) — not entered in F&O'
      : f === '' ? 'No company — customer not in TidsregInfo.xlsx and no fno_firma' : f;
    const warn = f === 'INTERNAL'
      ? 'Tracked here only. Shown so the month reconciles.'
      : f === '' ? 'These hours cannot go on a company timesheet until the customer is named.' : '';
    return html`
      <div class="card" style="margin-bottom:14px" key=${f}>
        <div class="blockhead">
          <h3>${title}</h3><b>${hrs(tot)} h</b>
          <span class="grow"></span>
          ${f === 'INTERNAL' ? html`<span class="sub">not entered</span>` : html`
            <${Fragment}>
              <button class="mini" onClick=${() => copy(f)}>Copy rows</button>
              <button class="mini" onClick=${() => excel(f)}>Excel</button>
            <//>`}
        </div>
        ${warn ? html`<p class="sub" style="color:var(--accent);margin:6px 0 0">${warn}</p>` : null}
        <!-- overflow-y MUST be explicit: with only overflow-x set, the other axis computes to
             'auto', making every table a vertical scroll container that swallows the wheel. -->
        <div style="overflow-x:auto;overflow-y:hidden;margin-top:10px">
          <table class="autable entry">
            <thead><tr>
              <th>Date</th><th>Customer</th><th>Project</th><th>Proj ID</th><th>Activity</th>
              <th>Task</th><th>Description</th><th class="r">${scaled ? 'F&O entry' : 'Hours'}</th>
            </tr></thead>
            <tbody>${rs.map(r => html`
              <tr key=${rowKey(r) + r.hours} class=${'clickable' + ((r.missing || []).length ? ' short' : '')}
                  onClick=${() => onPick(r)}>
                <td style="white-space:nowrap">${r.date}${r.live
                  ? html` <span class="pill warn" title="still accruing; finalize at /log">live</span>` : null}</td>
                <td>${r.customer || '-'}</td>
                <td>${shortProject(r.project)}</td>
                <td>${r.proj_id || html`<b class="accentink">missing</b>`}${
                  r.from_sheet ? html` <span class="sub"
                    title="filled from TidsregInfo.xlsx; the project CLAUDE.md has no fno_code">(sheet)</span>` : null}${
                  r.conflict ? html` <span class="accentink"
                    title=${'the sheet says ' + r.xl_proj_id + ', the workspace says ' + r.ws_proj_id}>conflict</span>` : null}</td>
                <td>${r.activity || '-'}</td>
                <td>${r.fno_task || ((r.requires || []).includes('task')
                  ? html`<b class="accentink">needed</b>` : '-')}</td>
                <td>${r.description || (r.no_charge ? html`<span class="pill">No charge</span>` : '-')}</td>
                <td class="r">${hrs(r.hours)}</td>
              </tr>`)}</tbody>
          </table>
        </div>
      </div>`;
  };

  const flags = [];
  if (E.unmapped && E.unmapped.length) {
    flags.push(`Customers with tracked time but no row in the sheet: `
      + E.unmapped.map(u => `${u.customer} (${hrs(u.hours)} h)`).join(', '));
  }
  if (E.no_project && E.no_project.length) {
    flags.push('In the sheet with no workspace project: ' + E.no_project.join(', '));
  }

  return html`
    <${Fragment}>
      <div class="stickybar"><div class="filterbar">
        ${lead}
        <span class="flabel">Companies</span>
        ${allFirmas.map(f => html`
          <button key=${f} class=${'chip' + (off.has(f) ? '' : ' on')}
                  onClick=${() => setOff(f)}>${nameOf(f)} · ${hrs(hoursOf(f))} h</button>`)}
        <span class="fsep"></span>
        <span class="flabel">Customers</span>
        ${allCusts.map(c => html`
          <button key=${c} class=${'chip' + (custOff.has(c) ? '' : ' on')}
                  onClick=${() => setCustOff(c)}>${c} · ${hrs(custHours(c))} h</button>`)}
        <span class="grow"></span>
        <b>${hrs(shown)} h</b>${shown !== total
          ? html` <span class="muted">of ${hrs(total)} h</span>` : null}
        <button class="mini" onClick=${() => excel(null)}
                title="one workbook of every visible line">Excel</button>
      </div></div>

      ${gate}

      ${!rows.length ? html`<div class="card"><${Empty}>No time in this period.<//></div>` : html`
        <${Fragment}>
          <div class="card" style="margin-bottom:14px">
            <h3>Totals per company — ${periodLabel}${scaled
              ? html` <span class="sub" style="font-weight:400">· F&O entry hours</span>` : null}</h3>
            <table class="autable totals"><tbody>
              ${allFirmas.map(f => totRow(nameOf(f), nOf(f), hoursOf(f),
                f === 'INTERNAL' ? 'not entered in F&O' : off.has(f) ? 'hidden below' : ''))}
              ${totRow('To enter in F&O', enterable.reduce((s, f) => s + nOf(f), 0),
                enterable.reduce((s, f) => s + hoursOf(f), 0),
                `across ${enterable.length} timesheet${enterable.length === 1 ? '' : 's'}`, true)}
              ${allFirmas.includes('INTERNAL')
                ? totRow('Period total', rows.length, total, 'incl. internal') : null}
            </tbody></table>
          </div>
          ${flags.length ? html`
            <div class="card" style="margin-bottom:14px"><div class="sub">
              ${flags.map((f, i) => html`<div key=${i}>${f}</div>`)}</div></div>` : null}
          ${firmas.map(block)}
        <//>`}
    <//>`;
}

/* ---------- the week behind the numbers ----------
   Read-only: every number comes from ops/time/ via the collector, and closing a short
   period is still `/time topup`. */

const auN = v => (v === null || v === undefined || v === 0)
  ? html`<span class="muted">–</span>` : hrs(v);
const auX = (a, b) => (b ? (Math.round(10 * a / b) / 10) + '×' : '–');
const TIERS = ['T1', 'T2', 'T3', 'T4', 'T5'];
/* Tier colour runs cool -> warm with the tier: the warm end is where the multiplier is
   largest and least tested (ADR-004), so it should catch the eye. */
const tierColor = t => ({
  T1: 'color-mix(in srgb, var(--cta) 35%, var(--surface-2))',
  T2: 'color-mix(in srgb, var(--cta) 65%, var(--surface-2))',
  T3: 'var(--cta)',
  T4: 'color-mix(in srgb, var(--accent) 70%, var(--surface-2))',
  T5: 'var(--accent)',
}[t]);

function TierBar({ tiers }) {
  const tot = TIERS.reduce((s, t) => s + (tiers[t] || 0), 0);
  if (!tot) return html`<span class="muted">–</span>`;
  return html`
    <span class="tierbar" title=${TIERS.filter(t => tiers[t])
      .map(t => `${t} ${Math.round(tiers[t])}m`).join(' · ')}>
      ${TIERS.filter(t => tiers[t]).map(t => html`
        <i key=${t} style=${`width:${(100 * tiers[t] / tot).toFixed(1)}%;background:${tierColor(t)}`}></i>`)}
    </span>`;
}

function Evidence({ D, w, onReassign }) {
  const T = w.totals;
  const stat = d => {
    if (d.absence) return html`<span class="pill">${d.absence}</span>`;
    if (d.status === 'empty') return html`<span class="pill bad">unaccounted</span>`;
    if (d.status === 'today') return html`<span class="pill">today</span>`;
    if (d.status === 'live') return html`<span class="pill warn">live</span>`;
    if (d.status === 'weekend') return html`<span class="muted">weekend</span>`;
    return html`<span class="muted">final</span>`;
  };

  /* 1 — the F&O lines with their evidence. Grouped by customer, then by date: F&O is
     entered one customer at a time, so the table is ordered the way the typing is done. */
  const ctrl = l => (!l.measured ? null
    : html` <span class="muted">${Math.round(100 * l.claimed / l.measured)}%</span>`);
  const ofValue = (e, v) => (!v ? null
    : html` <span class="muted">${Math.round(100 * e / v)}%</span>`);
  const ofEntry = (x, e) => ((!e || !x) ? null
    : html` <span class="muted">${Math.round(100 * x / e)}%</span>`);
  const lineRow = l => html`
    <tr key=${l.date + l.project + l.activity + l.fno_task}>
      <td>${shortDay(l.date)}</td>
      <td>${l.project}${l.live ? html` <span class="pill warn">live</span>` : null}${
        l.project === 'Dev' && !l.live ? html`
          <button class="mini" title="Move this Dev row to the project it was really for."
                  onClick=${() => onReassign(l)}>→</button>` : null}</td>
      <td class="muted">${l.proj_id}</td>
      <td>${l.activity || html`<span class="muted">–</span>`}</td>
      <td>${l.fno_task || html`<span class="muted">–</span>`}</td>
      <td class="r">${auN(l.keyboard)}${ofEntry(l.keyboard, entryOf(l))}</td>
      <td class="r">${auN(l.claimed)}${ctrl(l)}</td>
      <td class="r"><b>${auN(entryOf(l))}</b>${ofValue(entryOf(l), l.weighted)}</td>
      <td class="r">${auN(l.weighted)}${ofEntry(l.weighted, entryOf(l))}</td>
      <td class="r muted">${l.turns}/${l.stretches}</td>
      <td class="r muted">${l.files || '–'}</td>
      <td class="r">${l.t5 ? html`<b class="accentink">${l.t5}</b>` : '–'}</td>
    </tr>`;
  const sum = (ls, f) => ls.reduce((s, l) => s + (l[f] || 0), 0);
  const totRow = (lab, ls, cls) => (!ls.length ? null : html`
    <tr key=${lab} class=${'autot' + (cls ? ' ' + cls : '')}>
      <td colspan="5">${lab} <span class="muted">· ${ls.length} line${ls.length === 1 ? '' : 's'}</span></td>
      <td class="r">${auN(Math.round(sum(ls, 'keyboard') * 100) / 100)}${ofEntry(sum(ls, 'keyboard'), entrySum(ls))}</td>
      <td class="r">${auN(Math.round(sum(ls, 'claimed') * 100) / 100)}${sum(ls, 'measured')
        ? html` <span class="muted">${Math.round(100 * sum(ls, 'claimed') / sum(ls, 'measured'))}%</span>` : null}</td>
      <td class="r"><b>${auN(entrySum(ls))}</b>${ofValue(entrySum(ls), sum(ls, 'weighted'))}</td>
      <td class="r">${auN(Math.round(sum(ls, 'weighted') * 100) / 100)}${ofEntry(sum(ls, 'weighted'), entrySum(ls))}</td>
      <td class="r">${sum(ls, 'turns')}/${sum(ls, 'stretches')}</td>
      <td class="r">${sum(ls, 'files') || '–'}</td>
      <td class="r">${sum(ls, 't5') || '–'}</td>
    </tr>`);
  const custOfLine = p => (p.toLowerCase().startsWith('customers/')
    ? (p.split('/')[1] || 'No customer') : 'Internal');
  const byCust = {};
  w.lines.forEach(l => (byCust[custOfLine(l.project)] || (byCust[custOfLine(l.project)] = [])).push(l));
  const custOrder = Object.keys(byCust)
    .sort((a, b) => (a === 'Internal') - (b === 'Internal') || a.localeCompare(b));
  const bill = w.lines.filter(l => l.billable), intern = w.lines.filter(l => !l.billable);

  const cover = T.coverage === null ? '–' : Math.round(T.coverage) + '%';
  const tile = (lab, val, sub, role) => html`
    <div key=${lab} class=${'autile' + (role ? ' ' + role : '')}>
      <div class="autile-l">${lab}</div><div class="autile-v">${val}</div>
      <div class="autile-s">${sub}</div></div>`;

  return html`
    <${Fragment}>
      <div class="autiles">
        ${tile('Keyboard', hrs(T.keyboard) + ' h', 'measured production time')}
        ${tile('Measured', hrs(T.measured) + ' h', 'the 15+5 model')}
        ${tile('Work time', hrs(T.claimed) + ' h', T.measured
          ? Math.round(100 * T.claimed / T.measured) + '% of measured' : 'what gets registered', 'strong')}
        ${tile('Value time', hrs(T.weighted) + ' h', 'what the value model supports')}
        ${tile('Coverage', cover, `of ${hrs(w.target)} h target`,
          T.coverage === null ? '' : T.coverage >= 100 ? 'ok' : 'warn')}
      </div>
      <p class="sub" style="margin:8px 2px 16px">
        Work time / keyboard <b>${auX(T.claimed, T.keyboard)}</b> ·
        value time / keyboard <b>${auX(T.weighted, T.keyboard)}</b> ·
        billable <b>${hrs(T.billable)} h</b> · internal <b>${hrs(T.internal)} h</b> ·
        ${T.turns} turns in ${T.stretches} stretches${T.t5
          ? html` · <b>${T.t5} T5 event${T.t5 === 1 ? '' : 's'}</b>` : null}
        <br/>Target ${hrs(w.target)} h — 7.5 h × workdays, less absence${
          w.running ? ' — today joins tomorrow' : ''}</p>

      <div class="card ausec"><h3>1 · F&O lines</h3>
        <p class="sub">One row per date and F&O dimension. Every hours column carries a %:
          <b>keyboard</b> and <b>value time</b> read against F&O entry, so the row scans as one
          scale — what was typed, what is billed, and how much ceiling is left. <b>Work time</b>
          is measured time, and the % beside it is that against the 15+5 model — a control, not
          a number to bill on. <b>F&O entry</b> sits in the band between work and value time:
          turns and files per work hour decide how far up, saturating so more evidence always
          moves toward value time and never past it.</p>
        <div style="overflow-x:auto"><table class="autable">
          <thead><tr>
            <th>Date</th><th>Project</th><th>Proj ID</th><th>Activity</th><th>Task</th>
            <th class="r">Keyboard</th><th class="r">Work time</th><th class="r">F&O entry</th>
            <th class="r">Value time</th><th class="r">Turns/str</th><th class="r">Files</th>
            <th class="r">T5</th></tr></thead>
          <tbody>
            ${custOrder.map(c => html`
              <${Fragment} key=${c}>
                <tr class="augrp"><td colspan="12">${c}</td></tr>
                ${byCust[c].slice().sort((x, y) => x.date.localeCompare(y.date)
                  || x.project.localeCompare(y.project)
                  || (x.activity || '').localeCompare(y.activity || '')).map(lineRow)}
                ${totRow(c + ' total', byCust[c])}
              <//>`)}
            ${totRow('Billable', bill)}${totRow('Internal', intern)}
            ${totRow('Week total', w.lines, 'grand')}
          </tbody>
        </table></div>
      </div>

      <div class="card ausec"><h3>2 · Effort profile</h3>
        <p class="sub">Keyboard minutes by tier (ADR-004, provisional). T4 and T5 are where the
          multiplier is largest and least tested — a week leaning on them is a week whose claim
          rests on the weakest part of the model.</p>
        <div style="overflow-x:auto"><table class="autable">
          <thead><tr><th>Date</th><th>Mix</th>${TIERS.map(t => html`
            <th key=${t} class="r">${t}</th>`)}<th class="r">Turns/str</th>
            <th class="r">T5 ev.</th><th class="r">Files</th></tr></thead>
          <tbody>${w.days.filter(d => d.turns).map(d => html`
            <tr key=${d.date}>
              <td>${shortDay(d.date)} <span class="muted">${d.dow}</span></td>
              <td style="min-width:180px"><${TierBar} tiers=${d.tiers}/></td>
              ${TIERS.map(t => html`<td key=${t} class="r muted">${d.tiers[t]
                ? Math.round(d.tiers[t]) + 'm' : '–'}</td>`)}
              <td class="r muted">${d.turns}/${d.stretches}</td>
              <td class="r">${d.t5 ? html`<b class="accentink">${d.t5}</b>` : '–'}</td>
              <td class="r muted">${d.files || '–'}</td>
            </tr>`)}</tbody>
        </table></div>
      </div>

      <${Exceptions} w=${w} dayCap=${(D.audit || {}).dayCap}/>

      <div class="card ausec"><h3>4 · Coverage</h3>
        <p class="sub">Measured time against 7.5 h a workday. Nothing here is topped up
          automatically (ADR-005 v2) — a short <i>week</i> is closed deliberately with
          <code>/time topup ${w.week}</code>.</p>
        <div style="overflow-x:auto"><table class="autable">
          <thead><tr><th>Date</th><th>Day</th><th>Status</th><th class="r">Work time</th>
            <th class="r">Target</th><th class="r">Short</th><th class="r">Value time</th>
            <th>Note</th></tr></thead>
          <tbody>${w.days.map(d => {
            const shortish = d.target && d.claimed < d.target
              && d.status !== 'empty' && d.status !== 'today';
            return html`
              <tr key=${d.date} class=${d.workday ? '' : 'wk'}>
                <td>${shortDay(d.date)}</td><td class="muted">${d.dow}</td>
                <td>${stat(d)}</td>
                <td class="r">${auN(d.claimed)}</td>
                <td class="r muted">${d.target ? hrs(d.target) : '–'}</td>
                <td class=${'r' + (shortish ? ' warnink' : '')}>${shortish
                  ? '−' + hrs(d.short) : auN(0)}</td>
                <td class="r muted">${auN(d.weightedBillable)}</td>
                <td class="sub">${d.detail || (d.status === 'empty'
                  ? 'no keyboard time and no absence entry'
                  : d.status === 'today' ? 'still running'
                  : shortish ? 'under a full day — the week is the unit, not the day' : '')}</td>
              </tr>`;
          })}</tbody>
        </table></div>
        <p class="sub" style="margin:10px 0 0"><b>${hrs(T.claimed)} h</b> of
          <b>${hrs(w.target)} h</b>${T.short
            ? html` — <b class="warnink">${hrs(T.short)} h short</b>`
            : html` — <b class="okink">whole</b>`}</p>
      </div>

      <div class="card ausec"><h3>5 · The funnel, per day</h3>
        <p class="sub">Keyboard time is what was typed; value time is what the tiers say it was
          worth; measured is the 15+5 model; work time is the timesheet. Top-up is non-zero only
          where someone ran <code>--topup</code>.</p>
        <div style="overflow-x:auto"><table class="autable">
          <thead><tr><th>Date</th><th class="r">Keyboard</th><th class="r">Value time</th>
            <th class="r">Eff.</th><th class="r">Measured</th><th class="r">Work time</th>
            <th class="r">Top-up</th><th class="r">Work/kb</th></tr></thead>
          <tbody>${w.days.filter(d => d.keyboard || d.measured || d.claimed
            || d.status === 'today').map(d => html`
            <tr key=${d.date} class=${d.workday ? '' : 'wk'}>
              <td>${shortDay(d.date)} <span class="muted">${d.dow}</span></td>
              <td class="r">${auN(d.keyboard)}</td>
              <td class="r">${auN(d.weighted)}</td>
              <td class="r muted">${auX(d.weighted, d.keyboard)}</td>
              <td class="r">${auN(d.measured)}</td>
              <td class="r"><b>${auN(d.claimed)}</b></td>
              <td class="r">${d.topup ? html`<span class="okink">+${hrs(d.topup)}</span>` : auN(0)}</td>
              <td class="r muted">${auX(d.claimed, d.keyboard)}</td>
            </tr>`)}</tbody>
        </table></div>
      </div>
    <//>`;
}

function Exceptions({ w, dayCap }) {
  const ex = w.exceptions, blocks = [];
  if (ex.unaccounted.length) {
    blocks.push(html`
      <div class="block" key="u"><h4>Unaccounted workdays</h4>
        <p class="ink2" style="margin:4px 0">${ex.unaccounted.join(', ')} — no keyboard time and
          no absence entry. Answer them in <code>ops/time/absence.md</code>: vacation, holiday,
          sick, or offline.</p></div>`);
  }
  if (ex.under.length) {
    blocks.push(html`
      <div class="block" key="s"><h4>Days under a full day</h4>
        <table class="autable"><thead><tr><th>Date</th><th class="r">Work time</th>
          <th class="r">Short</th><th class="r">Value time supports</th></tr></thead>
          <tbody>${ex.under.map(u => html`
            <tr key=${u.date}><td>${shortDay(u.date)}</td><td class="r">${hrs(u.claimed)}</td>
              <td class="r warnink">−${hrs(u.short)}</td>
              <td class="r">${u.weighted === null ? html`<span class="muted">not derived</span>`
                : u.weighted < u.claimed ? html`<b class="accentink">${hrs(u.weighted)} h</b>`
                : hrs(u.weighted) + ' h'}</td></tr>`)}</tbody></table>
        <p class="sub" style="margin:6px 0 0">A single short day is not a problem — the week is
          the unit. Red means the value model supports <i>less</i> than what is already
          claimed.</p></div>`);
  }
  if (ex.unfinalized.length) {
    blocks.push(html`
      <div class="block" key="f"><h4>Not finalized</h4>
        <p class="ink2" style="margin:4px 0">${ex.unfinalized.join(', ')} — run <code>/log</code>
          or <code>ops/time/rollup.py</code>. A day that is not finalized cannot be corrected
          from this page either.</p></div>`);
  }
  if (ex.overCap.length) {
    blocks.push(html`
      <div class="block" key="c"><h4>Over the ${hrs(dayCap)} h day cap</h4>
        <p class="ink2" style="margin:4px 0">${ex.overCap.join(', ')} — more than ${hrs(dayCap)} h
          claimed for one customer on one date.</p></div>`);
  }
  if (w.spill.length) {
    blocks.push(html`
      <div class="block" key="p"><h4>Weighted-hour spill</h4>
        <p class="ink2" style="margin:4px 0">${w.spill.map((s, i) => html`
          <span key=${i}>${shortDay(s.date)} ← ${shortDay(s.from)} (${s.project}${
            s.activity ? ' / ' + s.activity : ''}, ${hrs(s.hours)} h)<br/></span>`)}</p>
        <p class="sub" style="margin:2px 0 0">Value-model hours moved off a capped date. Hours
          are moved, never dropped; period totals are unchanged.</p></div>`);
  }
  return html`
    <div class="card ausec"><h3>3 · Exceptions</h3>
      ${blocks.length ? blocks
        : html`<p class="sub" style="margin:0">Nothing outstanding for this week.</p>`}</div>`;
}

/* ---------- Dev -> project reassignment ----------
   Only Dev rows carry the control and the server refuses anything else: time on a named
   project stays there (ops/time/README.md sec.2). */

function Reassign({ line, projects, onDone }) {
  const [busy, setBusy] = useState(false);
  if (!line) return null;
  const opts = projects.filter(p => p.key !== 'Dev')
    .sort((x, y) => (!x.key.startsWith('customers/')) - (!y.key.startsWith('customers/'))
      || x.key.localeCompare(y.key));
  const move = async to => {
    if (!to) return;
    setBusy(true);
    const j = await post('/api/reassign', { date: line.date, to,
      activity: line.activity || '', fno_task: line.fno_task || '' });
    setBusy(false);
    toast(j.message || (j.ok ? 'moved' : 'failed'));
    if (j.ok) onDone();
  };
  return html`
    <h3>Move Dev time</h3>
    <p class="sub" style="margin:2px 0 12px">${shortDay(line.date)} · ${hrs(line.claimed)} h
      on <code>Dev</code>${line.activity ? ' / ' + line.activity : ''}. Dev → project only;
      time on a named project stays there.</p>
    <div class="block">
      <select class="mini" disabled=${busy} onChange=${e => move(e.target.value)}>
        <option value="">move to…</option>
        ${opts.map(p => html`<option key=${p.key} value=${p.key}>${p.key}${
          p.fno_code && p.fno_code !== 'UNSET' ? ' · ' + p.fno_code : ''}</option>`)}
      </select>
    </div>`;
}

/* ---------- Review: the month's shape ---------- */

function HoursChart({ data, tip }) {
  const W = 720, H = 200, PB = 22, PL = 30;
  const max = Math.max(4, ...data.map(d => d.billable + d.internal));
  const step = (W - PL) / data.length;
  const bw = Math.max(2, step - 3);
  const y = v => (H - PB) - (v / max) * (H - PB - 8);
  const grid = [0, 1, 2].map(i => max * i / 2);
  return html`
    <svg width="100%" viewBox=${`0 0 ${W} ${H}`} role="img"
         aria-label="Daily hours, billable and internal, weekends shaded">
      ${data.map((d, i) => isWeekend(d.date) ? html`
        <rect key=${'w' + d.date} x=${PL + i * step} y="0" width=${step} height=${H - PB}
              fill="var(--band)"/>` : null)}
      ${grid.map(v => html`
        <${Fragment} key=${'g' + v}>
          <line x1=${PL} x2=${W} y1=${y(v)} y2=${y(v)} stroke="var(--grid)" stroke-width="1"/>
          <text x="0" y=${y(v) + 4} fill="var(--muted)" font-size="10">${hrs(v)}</text>
        <//>`)}
      ${data.map((d, i) => {
        const x = PL + i * step + (step - bw) / 2;
        const tb = d.billable + d.internal;
        return html`
          <${Fragment} key=${d.date}>
            ${d.billable > 0 ? html`
              <rect x=${x} y=${y(d.billable)} width=${bw} height=${(H - PB) - y(d.billable)}
                    rx=${d.internal > 0 ? 0 : 4} fill="var(--s1)"/>` : null}
            ${d.internal > 0 ? html`
              <rect x=${x} y=${y(tb)} width=${bw}
                    height=${Math.max(2, (d.billable > 0 ? y(d.billable) - 2 : H - PB) - y(tb))}
                    rx="4" fill="var(--s2)"/>` : null}
            ${tb === 0 ? html`
              <rect x=${x} y=${H - PB - 2} width=${bw} height="2" rx="1" fill="var(--grid)"/>` : null}
            <rect x=${PL + i * step} y="0" width=${step} height=${H - PB} fill="transparent"
                  onMouseMove=${e => tip(e, d)} onMouseLeave=${() => tip(null)}/>
            <text x=${x + bw / 2} y=${H - 6} font-size="9" text-anchor="middle"
                  font-weight=${isWeekend(d.date) ? '700' : '400'}
                  fill=${isWeekend(d.date) ? 'var(--ink-2)' : 'var(--muted)'}>
              ${+d.date.slice(8)}</text>
          <//>`;
      })}
      <line x1=${PL} x2=${W} y1=${H - PB} y2=${H - PB} stroke="var(--axis)"/>
    </svg>`;
}

function ProjectBars({ rows }) {
  if (!rows.length) return html`<${Empty}>Nothing tracked in this period.<//>`;
  const max = Math.max(...rows.map(r => r.hrs));
  return html`
    <div>
      ${rows.map(({ p, hrs: v }) => html`
        <div key=${p.key} style="margin:0 0 11px">
          <div style="display:flex;justify-content:space-between;gap:10px;font-size:12.5px;margin:0 0 3px">
            <span class="ink2" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
              ${label(p)}</span>
            <span class="num">${hrs(v)} h</span>
          </div>
          <div style="height:9px;background:var(--surface-2);border-radius:4px;overflow:hidden">
            <div style=${`width:${Math.max(2, (v / max) * 100)}%;height:100%;background:var(--seq);border-radius:0 4px 4px 0`}></div>
          </div>
        </div>`)}
    </div>`;
}

function Internal({ D, per }) {
  const inP = new Set(per.days);
  const all = (D.internal || []).filter(r => inP.has(r.date));
  const rows = all.filter(r => !r.applied);
  const done = all.length - rows.length;
  const tot = rows.reduce((s, r) => s + r.hours, 0);
  const cand = rows.filter(r => r.co.length);
  const ch = cand.reduce((s, r) => s + r.hours, 0);
  const byProj = {};
  rows.forEach(r => { byProj[r.project] = (byProj[r.project] || 0) + r.hours; });
  return html`
    <section>
      <h2>Internal hours — ${per.label} · ${hrs(tot)} h across Dev and own/</h2>
      <div class="card">
        ${!rows.length ? html`
          <${Empty}>${done
            ? `All ${done} internal stretch${done === 1 ? '' : 'es'} in this period have been reassigned.`
            : 'No internal time in this period.'}<//>` : html`
          <${Fragment}>
            <p class="sub" style="margin:0 0 8px">
              ${cand.length} of ${rows.length} stretches were worked in a session that also touched
              a customer project — <b>${hrs(ch)} h</b> worth. Those are the candidates to move; the
              rest look genuinely internal.</p>
            <p class="sub" style="margin:0 0 8px">
              Split per session to stay traceable, which adds a buffer and a 0.5 h floor per
              fragment, so this runs above the ${hrs(D.totals.month_internal)} h on the tile.
              Decide <i>what</i> moves here; move it on the week's F&O lines.</p>
            ${Object.entries(byProj).sort((a, b) => b[1] - a[1]).map(([p, v]) => html`
              <div key=${p} style="display:flex;justify-content:space-between;gap:8px;padding:3px 0">
                <span>${p}</span><b>${hrs(v)} h</b></div>`)}
          <//>`}
      </div>
    </section>`;
}

function Hygiene({ hy }) {
  const clean = !hy.unset.length && !hy.orphans.length && !hy.unfinalized.length;
  return html`
    <section>
      <h2>Hygiene</h2>
      <div class="card">
        ${clean ? html`<${Empty}>Clean. Every line has a project id, a live folder and a finalized day.<//>` : null}
        ${hy.unset.length ? html`
          <div class="block">
            <h4>No F&O project id — ${hrs(hy.unset_total)} h</h4>
            <ul class="tight">${hy.unset.map(u => html`
              <li key=${u.project}>${u.project} — <b>${hrs(u.hours)} h</b></li>`)}</ul>
          </div>` : null}
        ${hy.orphans.length ? html`
          <div class="block">
            <h4>Time on folders that no longer exist</h4>
            <ul class="tight">${hy.orphans.map(o => html`
              <li key=${o.project}>${o.project} — <b>${hrs(o.hours)} h</b></li>`)}</ul>
          </div>` : null}
        ${hy.unfinalized.length ? html`
          <div class="block">
            <h4>Unfinalized days — ${hy.unfinalized.length}</h4>
            <p class="ink2" style="margin:4px 0">${hy.unfinalized.join(', ')}</p>
            <p class="sub" style="margin:4px 0 0">
              <code>python ops/time/rollup.py</code> writes every complete past day.</p>
          </div>` : null}
      </div>
    </section>`;
}

function Review({ D, per, scope, setScope, tipRef, tip, setTip }) {
  const daily = useMemo(() => {
    const src = {};
    D.daily.forEach(d => { src[d.date] = d; });
    return per.days.map(date => {
      const v = src[date] || { customers: 0, own: 0, dev: 0 };
      return { date,
        billable: scope.customers ? v.customers : 0,
        internal: (scope.own ? v.own : 0) + (scope.dev ? v.dev : 0) };
    });
  }, [D, per, scope]);

  const byProject = useMemo(() => {
    const inPeriod = new Set(per.days);
    return D.projects
      .filter(p => scope[scopeOf(p.key)])
      .map(p => ({ p, hrs: Object.entries(p.by_date)
        .reduce((s, [d, v]) => s + (inPeriod.has(d) ? v : 0), 0) }))
      .filter(r => r.hrs > 0).sort((a, b) => b.hrs - a.hrs).slice(0, 9);
  }, [D, per, scope]);

  const total = daily.reduce((s, d) => s + d.billable + d.internal, 0);
  const onTip = (e, d) => {
    if (!d) { setTip(null); return; }
    setTip(d);
    const n = tipRef.current;
    if (n) {
      n.style.left = Math.min(e.clientX + 14, innerWidth - 220) + 'px';
      n.style.top = Math.max(e.clientY - 70, 8) + 'px';
    }
  };

  return html`
    <${Fragment}>
      <div class="filterbar">
        <span class="flabel">Scope</span>
        ${[['customers', 'Customers'], ['own', 'Own'], ['dev', 'Dev']].map(([k, t]) => html`
          <button key=${k} class=${'chip' + (scope[k] ? ' on' : '')}
                  onClick=${() => setScope(s => ({ ...s, [k]: !s[k] }))}>${t}</button>`)}
      </div>
      <section class="cols">
        <div class="card chartbox">
          <h2>Hours — ${per.label}${total ? ' · ' + hrs(total) + ' h' : ''}</h2>
          <div class="legend" style="margin-bottom:10px">
            ${daily.some(d => d.billable > 0) ? html`
              <span><i class="swatch" style="background:var(--s1)"></i>Billable</span>` : null}
            ${daily.some(d => d.internal > 0) ? html`
              <span><i class="swatch" style="background:var(--s2)"></i>Internal</span>` : null}
            <span class="muted">
              <i class="swatch" style="background:var(--band);border:1px solid var(--grid)"></i>Weekend</span>
          </div>
          <${HoursChart} data=${daily} tip=${onTip}/>
        </div>
        <div class="card chartbox">
          <h2>By project — ${per.label}</h2>
          <div class="legend" style="margin-bottom:10px">
            <span class="muted">Active hours per project, top 9</span>
          </div>
          <${ProjectBars} rows=${byProject}/>
        </div>
      </section>
      <${Internal} D=${D} per=${per}/>
      <${Hygiene} hy=${D.hygiene}/>
    <//>`;
}

/* ---------- page ---------- */

function App() {
  const { data: D, err, stamp, reload, auto, setAuto } = useData('/api/data');
  const [mode, setMode] = useState('enter');
  const [back, setBack] = useState(0);          // 0 = this month, 1 = last
  const [week, setWeek] = useState('');         // '' = the whole month
  const [merge, setMerge] = useState(true);
  const [off, setOffSet] = useState(() => new Set());
  const [custOff, setCustOffSet] = useState(() => new Set());
  const [scope, setScope] = useState({ customers: true, own: true, dev: true });
  const [sel, setSel] = useState(null);
  const [dev, setDev] = useState(null);
  const [tip, setTip] = useState(null);
  const tipRef = useRef(null);

  const per = useMemo(() => (D ? periodDays(D.today, back) : null), [D, back]);

  /* The weeks the month filter leaves standing. F&O closes a month at a time, so entering
     hours is always "this month" — or "last month" when you are late. */
  const weeks = useMemo(() => {
    if (!D) return [];
    return ((D.audit || {}).weeks || []).filter(k => auKey(D, k, per.key));
  }, [D, per]);

  useEffect(() => { if (week && !weeks.includes(week)) setWeek(''); }, [weeks, week]);

  /* One clip, applied before anything is derived: the entry blocks and the sections below
     them then see exactly the same days. */
  const view = useMemo(() => {
    if (!D) return null;
    const E = D.entry;
    if (!week) {
      const rkey = 'month' + back;
      return { rkey, label: per.label, w: null, scale: null,
               file: 'fno-' + per.key, split: false };
    }
    const raw = (D.audit.byWeek || {})[week];
    const rkey = auKey(D, week, per.key) || week;
    const split = rkey !== week;
    const w = split ? clipWeek(raw, new Set((E.ranges || {})[rkey] || []), D.today) : raw;
    /* The blocks carry the F&O ENTRY figure, derived per dimension from the same lines
       section 1 shows. */
    const scale = {};
    w.lines.forEach(l => {
      const k = `${l.project}|${l.activity || ''}|${l.fno_task || ''}`;
      const s = scale[k] || (scale[k] = { work: 0, entry: 0 });
      s.work += l.claimed || 0; s.entry += entryOf(l);
    });
    return { rkey, w, scale, split, file: 'fno-' + week,
             label: split ? `${week} in ${per.label}` : `${week} · ${auRange(w)}` };
  }, [D, week, per, back]);

  /* The rows the page is showing, and the raw timesheet row behind each one. Consolidation
     moves a line to another date, so a consolidated row has no single row behind it and
     cannot be corrected — the editor says so rather than writing to the wrong day. */
  const { rows, rawByKey } = useMemo(() => {
    if (!D || !view) return { rows: [], rawByKey: {} };
    const E = D.entry;
    const inR = new Set((E.ranges || {})[view.rkey] || []);
    const base = merge ? ((E.merged || {})[view.rkey] || [])
      : (E.rows || []).filter(r => inR.has(r.date));
    const raws = {};
    (E.rows || []).forEach(r => { raws[rowKey(r)] = r; });
    return { rows: scaleRows(base, view.scale), rawByKey: merge ? {} : raws };
  }, [D, view, merge]);

  const toggle = (setter) => v => setter(s => {
    const n = new Set(s);
    if (n.has(v)) n.delete(v); else n.add(v);
    return n;
  });

  const reloadAll = () => { reload(); setSel(null); setDev(null); };

  useEffect(() => {
    const n = tipRef.current;
    if (n) n.style.display = tip ? 'block' : 'none';
  }, [tip]);

  /* View, Month, Week and Consolidated. They lead the same bar the company and customer
     chips are in, because picking the week is the first step of the same act as picking the
     company -- and that bar is sticky, so the pickers stay reachable down a 40-row block. */
  const lead = !D ? null : html`
    <${Fragment}>
      <span class="flabel">View</span>
      ${[['enter', 'Enter'], ['review', 'Review']].map(([k, tx]) => html`
        <button key=${k} class=${'chip' + (mode === k ? ' on' : '')}
                onClick=${() => setMode(k)}>${tx}</button>`)}
      <span class="fsep"></span>
      <span class="flabel">Month</span>
      ${[0, 1].map(n => html`
        <button key=${n} class=${'chip' + (back === n ? ' on' : '')}
                onClick=${() => setBack(n)}>${periodDays(D.today, n).label}</button>`)}
      ${mode !== 'enter' ? null : html`
        <${Fragment}>
          <span class="fsep"></span>
          <span class="flabel">Week</span>
          <button class=${'chip' + (week ? '' : ' on')}
                  title="the timesheet as it stands; a week shows the F&O entry figure instead"
                  onClick=${() => setWeek('')}>Whole month</button>
          ${weeks.map(k => {
            const b = D.audit.byWeek[k];
            const kk = auKey(D, k, per.key);
            const allowed = kk === k ? null : new Set((D.entry.ranges || {})[kk] || []);
            const ls = allowed ? b.lines.filter(l => allowed.has(l.date)) : b.lines;
            const e = entrySum(ls);
            const c = b.target ? Math.round(100 * e / b.target) : null;
            return html`
              <button key=${k} class=${'chip' + (week === k ? ' on' : '')}
                      title=${`${auRange(b)} · F&O entry ${hrs(e)} h of ${hrs(b.target)} h normal hours`}
                      onClick=${() => setWeek(k)}>${k.slice(5)}
                <span class="sub">${auRange(b)}</span>${c === null ? '' : ` · ${c}%`}</button>`;
          })}
          <span class="fsep"></span>
          <button class=${'chip' + (merge ? ' on' : '')} onClick=${() => setMerge(m => !m)}
                  title="Fewest lines: per F&O line, day-entries under 5 h are summed within an ISO week and packed onto as few days as possible, max 9 h a day. Totals never change — only how many lines you type. A consolidated line cannot be corrected, because its date has moved.">
            Consolidated</button>
        <//>`}
    <//>`;

  const shortNow = rows.filter(r => (r.missing || []).length).length;
  const tiles = D ? [
    html`<${Tile} key="1" label="Billable this month" value=${hrs(D.totals.month_billable)} foot="h"/>`,
    html`<${Tile} key="2" label="Internal this month" value=${hrs(D.totals.month_internal)} foot="Dev and own/"/>`,
    html`<${Tile} key="3" label="Not ready to enter" value=${shortNow} hot=${shortNow > 0}
                  foot=${view ? view.label : ''}/>`,
    html`<${Tile} key="4" label="Unfinalized" value=${D.hygiene.unfinalized.length}
                  hot=${D.hygiene.unfinalized.length > 0} foot="days without a timesheet"/>`,
  ] : [];

  return html`
    <${Shell} here="/time" title="Time" sub=${view ? view.label : 'loading…'}
              stamp=${stamp} auto=${auto} onAuto=${() => setAuto(a => !a)} onRefresh=${reload}
              tiles=${tiles}>
      ${err ? html`<div class="alert">Cannot reach the server: ${err}</div>` : null}
      ${!D ? null : html`
        <${Fragment}>
          ${mode === 'review' ? html`
            <${Fragment}>
              <div class="filterbar">${lead}</div>
              <${Review} D=${D} per=${per} scope=${scope} setScope=${setScope}
                         tipRef=${tipRef} tip=${tip} setTip=${setTip}/>
            <//>`
            : html`
              <${Fragment}>
                <${EntryBlocks} D=${D} rows=${rows} lead=${lead}
                                gate=${html`<${Ready} rows=${rows} periodLabel=${view.label}
                                                      onPick=${setSel}/>`}
                                periodLabel=${view.label} fileName=${view.file}
                                scaled=${!!view.scale}
                                off=${off} setOff=${toggle(setOffSet)}
                                custOff=${custOff} setCustOff=${toggle(setCustOffSet)}
                                onPick=${setSel}/>
                ${view.split ? html`
                  <p class="sub" style="margin:0 2px 14px"><b>${week}</b> spans two months. This
                    page shows only its ${(D.entry.ranges[view.rkey] || []).length} day(s) in
                    <b>${per.label}</b> — entry blocks and every section below — consolidated
                    within that stretch, so no hours cross the month.</p>` : null}
                ${!view.w ? html`
                  <div class="card ausec"><h3>The week behind the numbers</h3>
                    <p class="sub" style="margin:0">Pick a week above. The month view shows the
                      timesheet as it stands; a week shows the F&O entry figure and the evidence
                      each line rests on.</p></div>`
                  : html`
                    <${Fragment}>
                      <h2 class="ausplit">The week behind the numbers</h2>
                      <${Evidence} D=${D} w=${view.w} onReassign=${setDev}/>
                    <//>`}
              <//>`}
        <//>`}

      <${Drawer} open=${!!sel} onClose=${() => setSel(null)}>
        <${LineEditor} row=${sel} raw=${sel ? rawByKey[rowKey(sel)] : null} D=${D}
                       onDone=${reloadAll}/>
      <//>
      <${Drawer} open=${!!dev} onClose=${() => setDev(null)}>
        <${Reassign} line=${dev} projects=${(D && D.projects) || []} onDone=${reloadAll}/>
      <//>

      <div class="tip" ref=${tipRef}>
        ${tip ? html`
          <${Fragment}>
            <b>${dowName(tip.date)} ${tip.date}</b>${isWeekend(tip.date) ? ' · weekend' : ''}
            <br/>Billable <b>${hrs(tip.billable)} h</b>
            <br/>Internal <b>${hrs(tip.internal)} h</b>
          <//>` : null}
      </div>
    <//>`;
}

render(html`<${App}/>`, document.getElementById('root'));
