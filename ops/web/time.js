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
const isPlaceholder = v => {
  const s = (v || '').trim();
  return !s || /\?/.test(s) || /^(unset|none)$/i.test(s) || /^pending/i.test(s);
};
const blankIfPlaceholder = v => (isPlaceholder(v) ? '' : (v || '').trim());

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
   within a dimension, so the dimension total is the thing that must survive.

   The measurements the figure rests on are distributed the same way and ride along on the
   row (`measured`, `work`, `value`). They are not another opinion about the hours -- they
   are the same dimension total, split by the same proportion -- so a row can show what was
   measured beside what will be typed without the two being able to disagree. */
function scaleRows(rows, scale) {
  if (!scale) return rows;
  const dk = r => `${r.project}|${r.activity || ''}|${r.fno_task || ''}`;
  const out = rows.map(r => Object.assign({}, r, { work: r.hours }));
  const groups = {};
  out.forEach(r => { (groups[dk(r)] || (groups[dk(r)] = [])).push(r); });
  const share = (total, part, whole) => Math.round(total * (part / whole) * 100) / 100;
  for (const k in groups) {
    const g = groups[k], s = scale[k];
    if (!s || !s.work) continue;
    const work = g.reduce((a, r) => a + r.hours, 0);
    if (!work) continue;
    let left = Math.round(s.entry * 4) / 4;
    g.forEach((r, i) => {
      const part = r.hours;
      r.measured = share(s.measured, part, work);
      r.value = share(s.value, part, work);
      r.work = share(s.work, part, work);
      if (i === g.length - 1) { r.hours = Math.round(left * 100) / 100; return; }
      const v = Math.round(s.entry * (part / work) * 4) / 4;
      r.hours = v; left = Math.round((left - v) * 100) / 100;
    });
  }
  return out;
}

/* Every audit line in one calendar month. The weeks do not overlap, and a line is per
   date, so a week straddling the boundary contributes only its own days -- which is what
   makes a month total exact rather than clipped. */
function linesInMonth(D, monthKey) {
  const out = [];
  ((D.audit || {}).weeks || []).forEach(k => {
    (((D.audit.byWeek || {})[k] || {}).lines || []).forEach(l => {
      if (l.date.slice(0, 7) === monthKey) out.push(l);
    });
  });
  return out;
}

/* Per F&O dimension: what was measured, what is registered, what the value model supports,
   and what goes into F&O. The entry blocks distribute these across their rows. */
function scaleFrom(lines) {
  const scale = {};
  lines.forEach(l => {
    const k = `${l.project}|${l.activity || ''}|${l.fno_task || ''}`;
    const s = scale[k] || (scale[k] = { work: 0, entry: 0, measured: 0, value: 0 });
    s.work += l.claimed || 0;
    s.entry += entryOf(l);
    s.measured += l.measured || 0;
    s.value += l.weighted || 0;
  });
  return scale;
}

/* ---------- readiness ---------- */

/* The sessions behind one line.
 *
 * The exact key is date + project + the two sub-dimensions AS THE TIMESHEET HOLDS THEM. It
 * misses whenever the dimension has moved since the day was written -- an activity filled
 * in later, a task renamed -- and a miss reads as "nothing happened", which is the one
 * thing it never means. So a miss falls back to every session on that date and project,
 * merged, and says that is what it did. */
function lineEvidence(D, row) {
  const all = D.lineSessions || {};
  const rec = all[sessKey(row)];
  if (rec && (rec.blocks || []).length) {
    return { blocks: rec.blocks, more: rec.more || 0, wide: false };
  }
  const prefix = `${row.date}|${row.project}|`.toLowerCase();
  const merged = {};
  Object.keys(all).forEach(k => {
    if (!k.startsWith(prefix)) return;
    (all[k].blocks || []).forEach(b => {
      const m = merged[b.session] || (merged[b.session] =
        { session: b.session, turns: 0, hours: 0, task: b.task, lines: [] });
      m.turns += b.turns;
      m.hours = Math.round((m.hours + b.hours) * 100) / 100;
      if (b.task && !m.task) m.task = b.task;
      (b.lines || []).forEach(x => { if (!m.lines.includes(x)) m.lines.push(x); });
    });
  });
  const blocks = Object.values(merged).sort((a, b) => b.hours - a.hours).slice(0, 6)
    .sort((a, b) => (a.from || '').localeCompare(b.from || ''));
  return { blocks, more: 0, wide: blocks.length > 0 };
}

/* The line's hours shared out between the sessions behind it, in 0.25 h steps and
   summing to EXACTLY the line -- a split moves hours between lines, it never invents a
   quarter. The session evidence hours are the weight, not the figure: each session is
   measured on its own there, so it earns its own 5 min buffer and 0.5 h floor and the
   three of them add up to more than the line they came from. */
function quarters(total, blocks) {
  const units = Math.max(0, Math.round((total || 0) / 0.25));
  const w = blocks.map(b => (b.hours > 0 ? b.hours : 1));
  const sum = w.reduce((a, b) => a + b, 0);
  const exact = w.map(x => units * x / sum);
  const base = exact.map(Math.floor);
  let left = units - base.reduce((a, b) => a + b, 0);
  exact.map((x, i) => [x - base[i], i]).sort((a, b) => b[0] - a[0])
    .forEach(([, i]) => { if (left > 0) { base[i]++; left--; } });
  const out = {};
  blocks.forEach((b, i) => { out[b.session] = base[i] * 0.25; });
  return out;
}

/* The first thing said about a line. A timesheet row reads "Carl-Ras / – / –" and says
   nothing, which is worst exactly where it matters: deciding which task an untagged line
   belongs to. Until a line carries a written description this is the closest thing to one,
   and it is free -- the memory hook already recorded it. */
function lineGist(D, row, n) {
  const said = [];
  lineEvidence(D, row).blocks.forEach(b => (b.lines || []).forEach(x => {
    if (x && !said.includes(x)) said.push(x);
  }));
  return said.slice(0, n || 1);
}

/* The readiness gate.
 *
 * Grouped by project and by what is missing, because that is the grain a fix is made at --
 * one `fno_requires`, one `fno_code`, one task id usually answers the whole group. But the
 * group is not the thing you correct: expanding it lists its lines with the date, the hours
 * and what was said in the sessions behind each, so the one you open is the one you meant.
 */
function Ready({ rows, onPick, periodLabel, scaled, D }) {
  const [open, setOpen] = useState(() => new Set());
  const short = rows.filter(r => (r.missing || []).length);
  const unit = scaled ? 'work time' : 'timesheet hours';
  const hoursOf = r => (r.work !== undefined ? r.work : r.hours);
  const hours = Math.round(short.reduce((s, r) => s + hoursOf(r), 0) * 100) / 100;

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
    const g = byWhat[k] || (byWhat[k] = { id: k, project: r.project, label: m.label,
                                          why: m.why, hours: 0, entry: 0, rows: [] });
    g.hours = Math.round((g.hours + hoursOf(r)) * 100) / 100;
    g.entry = Math.round((g.entry + r.hours) * 100) / 100;
    g.rows.push(r);
  }));
  const groups = Object.values(byWhat).sort((a, b) => b.hours - a.hours);
  const toggle = id => setOpen(s => {
    const n = new Set(s);
    if (n.has(id)) n.delete(id); else n.add(id);
    return n;
  });

  return html`
    <div class="card ausec">
      <h3>Not ready to enter — ${short.length} line${short.length === 1 ? '' : 's'}
        ${' \u00b7 ' + hrs(hours)} h ${unit}</h3>
      <p class="sub">What the customer's own registration rule asks for and the line cannot
        supply (<code>fno_requires</code> on the customer node; ops/time/README.md 4.1).
        Open a group to see its lines, then pick the one to fix.</p>
      <div style="overflow-x:auto"><table class="autable">
        <thead><tr><th></th><th>Project</th><th>Missing</th>
          <th class="r">${scaled ? 'Work' : 'Hours'}</th>
          <th class="r">${scaled ? 'F&O entry' : 'Lines'}</th>
          <th class="r">Lines</th><th>Why</th></tr></thead>
        <tbody>${groups.map(g => html`
          <${Fragment} key=${g.id}>
            <tr class="clickable augrp" onClick=${() => toggle(g.id)}>
              <td class="fold">${open.has(g.id) ? '\u25be' : '\u25b8'}</td>
              <td>${shortProject(g.project)}</td>
              <td><b class="accentink">${g.label}</b></td>
              <td class="r">${hrs(g.hours)}</td>
              <td class="r">${scaled ? hrs(g.entry) : ''}</td>
              <td class="r muted">${g.rows.length}</td>
              <td class="sub">${g.why}</td>
            </tr>
            ${open.has(g.id) ? g.rows.slice().sort((a, b) => a.date.localeCompare(b.date))
              .map(r => {
                const gist = r.summary || lineGist(D, r)[0] || '';
                return html`
                  <tr key=${rowKey(r) + g.label} class="clickable"
                      onClick=${() => onPick(r)}>
                    <td></td>
                    <td style="white-space:nowrap">${r.date}${r.live
                      ? html` <span class="pill warn">live</span>` : null}</td>
                    <td class="muted">${r.fno_task || r.activity
                      || html`<span class="muted">nothing tagged</span>`}</td>
                    <td class="r">${hrs(hoursOf(r))}</td>
                    <td class="r">${scaled ? hrs(r.hours) : ''}</td>
                    <td class="r"></td>
                    <td class=${'sub gist' + (r.summary ? '' : ' verbatim')}>${gist
                      || html`<span class="muted">no description and no session evidence</span>`}</td>
                  </tr>`;
              }) : null}
          <//>`)}</tbody>
      </table></div>
      <p class="sub" style="margin:8px 0 0">The right-hand column is the line's written
        description where it has one, and otherwise <i>italic</i>: the first thing said in
        the sessions behind it, verbatim from the memory hook. Descriptions are written at
        <code>/log</code>; <code>python ops/bin/linedesc.py --check ${periodLabel.length === 8
          ? periodLabel : ''}</code> says what is still missing.</p>
    </div>`;
}

/* ---------- the line panel ----------
 *
 * Two words are doing one job in this workspace, and keeping them apart is the whole point
 * of how this panel is laid out:
 *
 *   a WORK-TASK   `ops/tasks/<state>/<slug>.md` -- a unit of work you open a session on
 *   an F&O TASK   the Azure DevOps work-item id that goes in the Task column of a time line
 *
 * A work-task carries an F&O task (and an activity) so that every line worked under it is
 * already complete. That mapping is customer-level hygiene and lives on the Projects page,
 * not here -- from a timesheet line it reads as though editing it would fix the line, and
 * it would not: it reaches the next session, never the day already written.
 *
 * So this panel does two things and says which is which:
 *   1. set the F&O dimensions on the timesheet line(s) behind this row -- the entry act
 *   2. set the defaults that stop the gap recurring -- the project's fno_code, the
 *      customer's activity and rule
 */

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

/* What a customer already registers on, from the lines already entered.
 *
 * Not the project's open work-tasks: every open Carl Ras one carries `fno_task: none`,
 * because the convention is id-or-none and the ids are opened in DevOps as the work goes.
 * The ids actually in use are on the lines, so that is where the list comes from -- ranked
 * by how much time is on them, with the most recent date beside each. A work-task that does
 * carry an id joins them. */
function knownValues(D, row, field) {
  const seen = {};
  (D.entry.rows || []).forEach(r => {
    if (!r.customer || r.customer !== row.customer) return;
    const v = blankIfPlaceholder(r[field]);
    if (!v) return;
    const s = seen[v] || (seen[v] = { value: v, hours: 0, n: 0, last: '', mine: false });
    s.hours = Math.round((s.hours + r.hours) * 100) / 100;
    s.n += 1;
    if (r.date > s.last) s.last = r.date;
    if (r.project === row.project) s.mine = true;
  });
  const out = Object.values(seen).sort((a, b) => (b.mine - a.mine) || (b.hours - a.hours));
  if (field === 'fno_task') {
    const have = new Set(out.map(u => u.value));
    (D.targets || []).forEach(x => {
      const id = blankIfPlaceholder(x.fno_task);
      if (x.project === row.project && id && !have.has(id)) {
        out.push({ value: id, hours: 0, n: 0, last: '', mine: true, title: x.title });
      }
    });
  }
  return out;
}

/* An id alone -- `CarlRData-555` -- is the least informative thing on the page, and the
   one you have to pick correctly out of ten. So the option leads with what it IS: the name
   from `ops/time/fno-tasks.md` if it has been recorded, else the title of the work-task
   carrying it. The usage follows, because "17 lines, last 2026-08-31" is what tells you
   this is the live one rather than the one you closed in July. Only the id is ever
   written. */
const clip = (s, n) => (!s ? '' : s.length > n ? s.slice(0, n - 1) + '\u2026' : s);

const knownLabel = (u, names) => {
  const rec = (names || {})[u.value] || {};
  const bits = [u.value];
  if (rec.name) bits.push(clip(rec.name, 52));
  if (!rec.ok) bits.push('F&O would reject this');
  if (u.n) bits.push(`${u.n} line${u.n === 1 ? '' : 's'}, last ${u.last}`);
  else if (!rec.name) bits.push('from a work-task');
  return bits.join(' · ');
};

/* "Do not invoice this, under any circumstances."
 *
 * Some work happens inside a customer folder and is not that customer's to pay for:
 * registering the time, fixing the setup, building this page. The folder cannot know
 * that, so it has to be said -- once, per line, and it has to stick.
 *
 * It goes on `ops/time/not-invoiced.md` first, which the rollup and the entry page both
 * honour, so the decision survives the day being re-derived, the file being hand-edited
 * and the line being moved. Then, if the day is finalized, the timesheet line is moved
 * and/or set `Billable: no` so the file agrees with the register. On a day still running
 * there is no file yet -- the register still takes it, and the rollup applies it when the
 * day closes. That is the case this exists for: the work you are doing right now.
 *
 * Where it goes is a separate question from whether it is invoiced, and both are answered
 * in one click: leave it where it is, move it to the client overall, or move it to the
 * workspace or an own/ project.
 */
function NeverInvoice({ raw, D, onDone }) {
  const [why, setWhy] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => { setWhy(''); setBusy(false); }, [rowKey(raw)]);

  if (!raw.project.startsWith('customers/')) return null;
  const cust = raw.project.split('/')[1];
  const node = 'customers/' + cust;
  const own = (D.projects || []).filter(p => p.key.startsWith('own/'));

  const mark = async to => {
    setBusy(true);
    const j = await post('/api/noinvoice', {
      date: raw.date,
      row: { project: raw.project, proj_id: raw.ws_proj_id, activity: raw.ws_activity,
             fno_task: raw.ws_fno_task },
      to, note: why.trim(),
    });
    setBusy(false);
    toast(j.message || (j.ok ? 'marked' : 'failed'));
    if (j.ok) onDone();
  };

  if (raw.no_entry) {
    return html`
      <div class="never on">
        <b>Not invoiced.</b> <span class="sub">On the register, so it stays that way however
        the day is re-derived. Remove the row in
        <code>ops/time/not-invoiced.md</code> to undo it.</span>
      </div>`;
  }

  return html`
    <div class="never">
      <div class="neverhead"><b>Do not invoice this</b>
        <span class="sub">${hrs(raw.hours)} h — goes on the register, so it sticks</span></div>
      <div class="actrow">
        <input type="text" value=${why} onInput=${e => setWhy(e.target.value)}
               placeholder="why — registering time, fixing my setup, the dashboard…"
               aria-label="why not invoiced"/>
      </div>
      <div class="rowacts">
        <button class="act" disabled=${busy} title=${'leave it on ' + raw.project}
                onClick=${() => mark('')}>${raw.live ? 'Do not invoice it' : 'Keep it here'}</button>
        ${raw.live ? null : html`
          <${Fragment}>
            ${raw.project !== node ? html`
              <button class="act" disabled=${busy}
                      title=${'move it to the ' + cust + ' customer node, which has no F&O code'}
                      onClick=${() => mark(node)}>${cust} overall</button>` : null}
            <button class="act" disabled=${busy} title="move it to the workspace"
                    onClick=${() => mark('Dev')}>Dev</button>
            ${own.length ? html`
              <select class="mini" value="" disabled=${busy}
                      onChange=${e => { if (e.target.value) mark(e.target.value); }}>
                <option value="">own/…</option>
                ${own.map(o => html`<option key=${o.key} value=${o.key}>${o.key}</option>`)}
              </select>` : null}
          <//>`}
      </div>
      ${raw.live ? html`
        <p class="sub" style="margin:6px 0 0">The decision is taken now and the rollup
          applies it when the day closes. <b>Where</b> it belongs instead is a change to a
          timesheet line, so that waits for the file to exist — come back after
          <code>/log</code>.</p>` : null}
    </div>`;
}

/* What the picked id is, and the one place to say it.
 *
 * The name comes from `ops/time/fno-tasks.md` when it has been recorded, and otherwise
 * from the work-task carrying the id -- which describes the same work from our side but
 * is not what DevOps calls it. Saying it once here is how the register gets filled: at
 * the moment the id is in front of you, not in a sitting set aside for it. */
function TaskName({ id, rec, customer, onDone }) {
  const [name, setName] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => { setName(''); setBusy(false); }, [id]);

  const save = async () => {
    setBusy(true);
    const j = await post('/api/fnotask', { id, name: name.trim(), customer });
    setBusy(false);
    toast(j.message || (j.ok ? 'named' : 'failed'));
    if (j.ok) { setName(''); onDone(); }
  };

  if (rec && !rec.ok) {
    return html`
      <p class="sub" style="margin:2px 0 6px 72px"><b class="accentink">F&O will reject
        <code>${id}</code></b> — a Task id is letters, digits and dashes. This looks like a
        work-task slug or an id with a note after it.</p>`;
  }
  if (rec && rec.source === 'register') {
    return html`
      <p class="sub" style="margin:2px 0 6px 72px"><b>${rec.name}</b></p>`;
  }
  return html`
    <${Fragment}>
      ${rec && rec.name ? html`
        <p class="sub" style="margin:2px 0 2px 72px">${rec.name}
          <span class="muted">— our work-task's title, not the DevOps name</span></p>` : null}
      <div class="actrow">
        <span class="flabel" style="min-width:64px">is called</span>
        <input type="text" value=${name} onInput=${e => setName(e.target.value)}
               placeholder=${'what ' + id + ' is called in DevOps'}
               aria-label="name this F&O task"/>
        <button class="act" disabled=${busy || !name.trim()} onClick=${save}>Name it</button>
      </div>
    <//>`;
}

/* The sessions behind one line, and the split that gives each its own F&O task.

 * A timesheet day groups by DIMENSION, so three sessions on one customer with nothing
 * tagged are one line of 0.75 h -- and one line takes one task. But the three were a
 * cluster error, a deployment and the Marketo work, and they belong under three
 * different tasks. So the line is shown as what it is made of: each session with when it
 * ran and the first thing said in it, and a destination of its own.
 *
 * Split writes them as separate lines of the same day. Hours are shared OUT of the line
 * -- what is not assigned stays where it is and the day's total never moves. The Proj ID
 * is not a session's to change: it belongs to the project, so Save above still sets it
 * for all of them.
 */
function SessionSplit({ raw, row, D, onDone }) {
  const ev = lineEvidence(D, raw);
  const blocks = ev.blocks;
  const onTask = (row.requires || []).includes('task');
  const field = onTask ? 'fno_task' : 'activity';
  const names = (D.entry || {}).task_names || {};
  const known = knownValues(D, row, field);
  const [to, setTo] = useState({});
  const [share, setShare] = useState({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setTo({});
    setShare(quarters(raw.hours, blocks));
    setBusy(false);
  }, [rowKey(raw), blocks.map(b => b.session).join()]);

  if (blocks.length < 2) return null;

  const set = (m, s, v) => m(o => Object.assign({}, o, { [s]: v }));
  const parts = blocks.map(b => ({
    session: b.session,
    hours: Number(share[b.session] || 0),
    activity: onTask ? '' : (to[b.session] || '').trim(),
    fno_task: onTask ? (to[b.session] || '').trim() : '',
  })).filter(p => (p.activity || p.fno_task) && p.hours > 0);
  const moving = Math.round(parts.reduce((s, p) => s + p.hours, 0) * 100) / 100;
  const left = Math.round((raw.hours - moving) * 100) / 100;

  const split = async () => {
    setBusy(true);
    const j = await post('/api/tssplit', {
      date: raw.date,
      row: { project: raw.project, proj_id: raw.ws_proj_id, activity: raw.ws_activity,
             fno_task: raw.ws_fno_task },
      parts,
    });
    setBusy(false);
    toast(j.message || (j.ok ? 'split' : 'failed'));
    if (j.ok) onDone();
  };

  return html`
    <div class="split">
      <div class="neverhead"><b>${blocks.length} work sessions are on this one line</b>
        <span class="sub">${hrs(raw.hours)} h between them</span></div>
      <p class="sub" style="margin:0 0 2px">${ev.wide
        ? html`This line's own dimensions matched no session, so these are <b>every
            session on ${raw.date} for ${shortProject(raw.project)}</b> — check the times
            before splitting.`
        : html`Give any of them ${onTask ? 'an F&O task' : 'an activity'} of its own and
            Split writes it as a separate line of the same day. Unassigned hours stay
            here.`}</p>
      ${ev.more ? html`<p class="sub" style="margin:2px 0 0"><b class="accentink">${ev.more}
        more session${ev.more === 1 ? '' : 's'}</b> on this line are not shown.</p>` : null}
      ${blocks.map(b => html`
        <div class="splitrow" key=${b.session}>
          <div class="splitwhen"><b>${b.from || '--:--'}–${b.to || '--:--'}</b>
            <span class="muted">${b.turns} turn${b.turns === 1 ? '' : 's'} · ${b.session}</span>
            ${b.task ? html` <span class="muted">· ${b.task}</span>` : null}</div>
          <div class="tturn">${(b.lines || [])[0]
            || 'no memory record for this session'}</div>
          <div class="actrow">
            <input class="qin" type="text" value=${String(share[b.session] === undefined
                     ? '' : share[b.session])}
                   onInput=${e => set(setShare, b.session, e.target.value)}
                   aria-label=${'hours for ' + b.session}/>
            <span class="sub">h</span>
            ${known.length ? html`
              <select class="mini" value=${to[b.session] || ''}
                      aria-label=${'line for ' + b.session}
                      onChange=${e => set(setTo, b.session, e.target.value)}>
                <option value="">leave it here…</option>
                ${known.map(u => html`
                  <option key=${u.value} value=${u.value}>${knownLabel(u, onTask ? names : {})}</option>`)}
              </select>` : null}
            <input type="text" value=${to[b.session] || ''}
                   onInput=${e => set(setTo, b.session, e.target.value)}
                   placeholder=${onTask ? 'or type a task id' : 'or type an activity'}
                   aria-label=${'id for ' + b.session}/>
          </div>
        </div>`)}
      <div class="rowacts">
        <span class="sub" style="margin-right:auto">${parts.length
          ? `${hrs(moving)} h moves off this line, ${hrs(left)} h stays`
          : 'nothing assigned yet'}</span>
        <button class="act primary"
                disabled=${busy || !parts.length || left < -0.001}
                onClick=${split}>Split into ${parts.length + (left > 0 ? 1 : 0)} lines</button>
      </div>
      ${left < -0.001 ? html`<p class="sub" style="margin:6px 0 0"><b class="accentink">That
        is ${hrs(-left)} h more than the line has.</b> A split moves hours, it cannot add
        them.</p>` : null}
    </div>`;
}

/* One timesheet line: its F&O dimensions, and the write that puts them there.
 *
 * This is the entry act. It rewrites one row of one finalized day file and records the
 * correction underneath, the way ops/time/README.md says to. A day still accruing has no
 * file yet and says so. */
function DayFix({ raw, row, D, onDone, only }) {
  const [pid, setPid] = useState('');
  const [act, setAct] = useState('');
  const [task, setTask] = useState('');
  const [hours, setHours] = useState('');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setPid(blankIfPlaceholder(raw.proj_id) || blankIfPlaceholder(row.proj_id));
    setAct(blankIfPlaceholder(raw.activity));
    setTask(blankIfPlaceholder(raw.fno_task));
    setHours(String(raw.hours));
    setNote('');
    setBusy(false);
  }, [rowKey(raw)]);

  const onTask = (row.requires || []).includes('task');
  const tasks = knownValues(D, row, 'fno_task');
  const acts = knownValues(D, row, 'activity');
  const names = (D.entry || {}).task_names || {};
  const picked = names[task.trim()] || null;
  const changed = pid !== (raw.ws_proj_id || '') || act !== (raw.ws_activity || '')
    || task !== (raw.ws_fno_task || '') || String(raw.hours) !== hours.trim();

  const correct = async () => {
    setBusy(true);
    const j = await post('/api/timesheet', {
      date: raw.date,
      row: { project: raw.project, proj_id: raw.ws_proj_id, activity: raw.ws_activity,
             fno_task: raw.ws_fno_task },
      set: { proj_id: pid.trim(), activity: act.trim(), fno_task: task.trim(),
             hours: Number(hours) },
      note: note.trim(),
    });
    setBusy(false);
    toast(j.message || (j.ok ? 'corrected' : 'failed'));
    if (j.ok) onDone();
  };

  if (raw.live) {
    return html`
      <div class="daycard">
        <div class="dayhead"><b>${raw.date}</b> · ${hrs(raw.hours)} h
          <span class="pill warn">live</span></div>
        <p class="sub" style="margin:4px 0 8px">Still accruing, so there is no timesheet
          file to correct yet — close the day with <code>/log</code> and the fields appear.
          The defaults below, and the decision underneath, apply to it now.</p>
        <${NeverInvoice} raw=${raw} D=${D} onDone=${onDone}/>
      </div>`;
  }
  if (raw.ambiguous) {
    return html`
      <div class="daycard">
        <div class="dayhead"><b>${raw.date}</b> · ${hrs(raw.hours)} h</div>
        <p class="sub" style="margin:4px 0 0">Two timesheet lines on ${raw.date} resolve to
          this one row, so there is no single line to change. Edit
          <code>ops/time/timesheet/${raw.date.slice(0, 7)}/${raw.date}.md</code> by hand.</p>
      </div>`;
  }

  return html`
    <div class="daycard">
      <div class="dayhead"><b>${raw.date}</b> · ${hrs(raw.hours)} h
        ${raw.no_entry ? html`<span class="pill">not registered</span>` : null}
        ${only ? null : html`<span class="sub">${dowName(raw.date)}</span>`}</div>

      ${tasks.length ? html`
        <div class="actrow">
          <span class="flabel" style="min-width:64px">F&O task</span>
          <select class="mini" value=${task}
                  onChange=${e => setTask(e.target.value)}>
            <option value="">${task ? '(clear it)' : 'pick one already in use…'}</option>
            ${tasks.map(u => html`
              <option key=${u.value} value=${u.value}>${knownLabel(u, names)}</option>`)}
            ${task && !tasks.some(u => u.value === task)
              ? html`<option value=${task}>${task}</option>` : null}
          </select>
        </div>` : null}
      <div class="actrow">
        <span class="flabel" style="min-width:64px">${tasks.length ? '…or type' : 'F&O task'}</span>
        <input type="text" value=${task} onInput=${e => setTask(e.target.value)}
               placeholder="the linked DevOps work item" aria-label="F&O task"/>
      </div>
      ${task.trim() ? html`
        <${TaskName} id=${task.trim()} rec=${picked} customer=${row.customer}
                     onDone=${onDone}/>` : null}

      ${acts.length ? html`
        <div class="actrow">
          <span class="flabel" style="min-width:64px">Activity</span>
          <select class="mini" value=${act} onChange=${e => setAct(e.target.value)}>
            <option value="">${act ? '(clear it)' : 'pick one already in use…'}</option>
            ${acts.map(u => html`
              <option key=${u.value} value=${u.value}>${knownLabel(u, {})}</option>`)}
            ${act && !acts.some(u => u.value === act)
              ? html`<option value=${act}>${act}</option>` : null}
          </select>
        </div>` : null}
      <div class="actrow">
        <span class="flabel" style="min-width:64px">${acts.length ? '…or type' : 'Activity'}</span>
        <input type="text" value=${act} onInput=${e => setAct(e.target.value)}
               placeholder=${onTask ? 'F&O derives it from the task — leave blank' : 'activity id'}
               aria-label="Activity"/>
      </div>

      <details class="daymore">
        <summary>Proj ID, hours and a reason</summary>
        <div class="actrow"><span class="flabel" style="min-width:64px">Proj ID</span>
          <input type="text" value=${pid} onInput=${e => setPid(e.target.value)}
                 placeholder="e.g. 230-02" aria-label="Proj ID"/></div>
        <div class="actrow"><span class="flabel" style="min-width:64px">Hours</span>
          <input type="text" value=${hours} onInput=${e => setHours(e.target.value)}
                 aria-label="Hours"/>
          <span class="sub">work time, 0.25 h steps</span></div>
        <div class="actrow"><span class="flabel" style="min-width:64px">Why</span>
          <input type="text" value=${note} onInput=${e => setNote(e.target.value)}
                 placeholder="goes into the correction note" aria-label="Why"/></div>
      </details>

      <div class="rowacts">
        <span class="sub" style="margin-right:auto">writes
          <code>timesheet/${raw.date.slice(0, 7)}/${raw.date}.md</code></span>
        <button class="act primary" disabled=${busy || !changed}
                onClick=${correct}>Save ${raw.date}</button>
      </div>

      <${SessionSplit} raw=${raw} row=${row} D=${D} onDone=${onDone}/>
      <${NeverInvoice} raw=${raw} D=${D} onDone=${onDone}/>
    </div>`;
}

/* The defaults behind a line, on the files that own them.
 *
 *   Proj ID      the project's `## Identity` fno_code
 *   Beskrivelse  the project's fno_description, since it carries the engagement
 *   Activity     the customer's fno_activity, the default for every line with none
 *   the rule     the customer's fno_requires
 *
 * The work-task mapping is NOT here. It is customer-level hygiene -- every open work-task
 * should carry an F&O task or activity before any time is logged to it -- and it lives on
 * the Projects page, where the customer does.
 */
function SourceFixes({ row, D, onDone }) {
  const [code, setCode] = useState('');
  const [defAct, setDefAct] = useState('');
  const [req, setReq] = useState('');
  const [desc, setDesc] = useState('');
  const [busy, setBusy] = useState(false);

  const proj = (D.projects || []).find(p => p.key === row.project);
  const rule = row.customer ? ((D.entry.rules || {})[normCust(row.customer)] || null) : null;

  useEffect(() => {
    setCode(proj ? blankIfPlaceholder(proj.fno_code) : '');
    setDefAct(rule ? rule.activity : '');
    setReq((row.requires || []).join(', '));
    setDesc((proj && proj.fno_description) || (rule && rule.description) || '');
    setBusy(false);
  }, [rowKey(row)]);

  const field = async (kind, target, f, value) => {
    setBusy(true);
    const j = await post('/api/fno', { kind, target, field: f, value });
    setBusy(false);
    toast(j.message || (j.ok ? 'saved' : 'failed'));
    if (j.ok) onDone();
  };

  const needs = new Set((row.missing || []).map(m => m.field));
  const onTask = (row.requires || []).includes('task');

  return html`
    <div class="block">
      <h4>Defaults, so it stops recurring</h4>
      <p class="sub" style="margin:0 0 10px">These do not touch the lines above — they set
        what future lines inherit.</p>

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
          <p class="sub" style="margin:10px 0 0">Every open work-task for ${row.customer}
            should carry an F&O task or activity of its own, so a session tagged with it
            produces a line that is already complete. That check is on
            <a href="/projects">Projects</a>, under the customer.</p>
        <//>` : null}
    </div>`;
}

function LineEditor({ row, behind, D, onDone }) {
  if (!row) return null;
  const missing = row.missing || [];
  const scaled = row.work !== undefined && row.work !== row.hours;
  const ev = lineEvidence(D, row);
  const sess = ev.blocks;

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

    <div class="block">
      <h4>${behind.length > 1
        ? `The ${behind.length} timesheet lines behind this row`
        : 'The timesheet line'}</h4>
      ${behind.length > 1 ? html`
        <p class="sub" style="margin:0 0 8px">Consolidated packs a week's hours onto as few
          days as possible, so the row above stands for these. Each is its own line in its
          own day file and is tagged on its own.</p>` : null}
      ${behind.length ? behind.map(r => html`
        <${DayFix} key=${rowKey(r)} raw=${r} row=${row} D=${D} onDone=${onDone}
                   only=${behind.length === 1}/>`)
        : html`<p class="sub" style="margin:0">No timesheet row matches this line any more —
          the day has moved under the page. Refresh.</p>`}
    </div>

    <${SourceFixes} row=${row} D=${D} onDone=${onDone}/>

    <div class="block">
      <h4>What this line was</h4>
      ${row.summary ? html`<p style="margin:0 0 8px">${row.summary}</p>` : null}
      <p class="sub" style="margin:0 0 6px">${ev.wide
        ? html`No session matched this line's exact dimensions — its activity or task has
               moved since the day was written — so this is <b>every session on
               ${row.date} for ${shortProject(row.project)}</b>.`
        : 'The sessions behind this one date and dimension.'}
        What the memory hook recorded being said in them; not a written description, the
        first turns verbatim.</p>
      ${sess.length ? sess.map((b, i) => html`
        <div key=${i} class="tsess">
          <b>${hrs(b.hours)} h</b> · ${b.turns} turn${b.turns === 1 ? '' : 's'}
          · <span class="muted">${b.session}</span>
          · <span class="muted">${b.task || 'no work-task tagged'}</span>
          ${(b.lines || []).map((t, j) => html`<div key=${j} class="tturn">${t}</div>`)}
          ${(b.lines || []).length ? null
            : html`<div class="tturn muted">no memory records for this session</div>`}
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
  /* Only Element Logic requires a Beskrivelse, so the column is dead weight everywhere
     else -- and on a week view the measurement columns need the room. Decided per COMPANY:
     one customer needing it must not put an empty column on every other company's block. */
  const wantsDesc = rs => rs.some(r => r.description || (r.requires || []).includes('description'));

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
    const anyDesc = wantsDesc(rs);
    const tot = rs.reduce((s, r) => s + r.hours, 0);
    const title = f === 'INTERNAL' ? 'Not entered in F&O — Dev, own/, and customer work that is not invoiced'
      : f === '' ? 'No company — customer not in TidsregInfo.xlsx and no fno_firma' : f;
    const notReg = rs.filter(r => r.no_entry);
    const warn = f === 'INTERNAL'
      ? 'Tracked here only. Shown so the month reconciles.'
        + (notReg.length
          ? ` ${notReg.length} line${notReg.length === 1 ? '' : 's'} sit under a customer and are marked not for registration.`
          : '')
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
              <th>Task</th>${anyDesc ? html`<th>Description</th>` : null}
              ${scaled ? html`
                <${Fragment}>
                  <th class="r" title="the 15+5 model: what the meter says was worked">Measured</th>
                  <th class="r" title="what the timesheet registers">Work</th>
                <//>` : null}
              <th class="r">${scaled ? 'F&O entry' : 'Hours'}</th>
            </tr></thead>
            <tbody>${rs.map(r => html`
              <tr key=${rowKey(r) + r.hours} title=${r.summary || ''}
                  class=${'clickable' + ((r.missing || []).length ? ' short' : '')
                    + (r.summary ? ' described' : '')}
                  onClick=${() => onPick(r)}>
                <td style="white-space:nowrap">${r.date}${r.live
                  ? html` <span class="pill warn" title="still accruing; finalize at /log">live</span>` : null}</td>
                <td>${r.customer || '-'}${r.no_entry
                  ? html` <span class="pill" title="marked not for registration in the timesheet">not billed</span>` : null}</td>
                <td>${shortProject(r.project)}</td>
                <td>${r.proj_id || html`<b class="accentink">missing</b>`}${
                  r.from_sheet ? html` <span class="sub"
                    title="filled from TidsregInfo.xlsx; the project CLAUDE.md has no fno_code">(sheet)</span>` : null}${
                  r.conflict ? html` <span class="accentink"
                    title=${'the sheet says ' + r.xl_proj_id + ', the workspace says ' + r.ws_proj_id}>conflict</span>` : null}</td>
                <td>${r.activity || '-'}${!anyDesc && r.no_charge
                  ? html` <span class="pill">No charge</span>` : null}</td>
                <td>${r.fno_task || ((r.requires || []).includes('task')
                  ? html`<b class="accentink">needed</b>` : '-')}</td>
                ${anyDesc ? html`<td>${r.description
                  || (r.no_charge ? html`<span class="pill">No charge</span>` : '-')}</td>` : null}
                ${scaled ? html`
                  <${Fragment}>
                    <td class="r muted">${hrs(r.measured || 0)}</td>
                    <td class="r muted">${hrs(r.work || 0)}</td>
                  <//>` : null}
                <td class="r"><b>${hrs(r.hours)}</b>${r.work
                  ? html` <span class="muted" title="F&O entry against work time"
                          >${Math.round(100 * r.hours / r.work)}%</span>` : null}</td>
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
      <td class="r">${auN(l.measured)}${l.shared
        ? html` <span class="muted"
                title="a correction moved this line after the day was written, so the evidence was recorded against another dimension of the same project. It is split across that project's lines in proportion to their hours -- a share of the day, not this line's own measurement.">\u2248</span>`
        : null}</td>
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
      <td class="r">${auN(Math.round(sum(ls, 'measured') * 100) / 100)}</td>
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
        <p class="sub">One row per date and F&O dimension. <b>Measured</b> is the 15+5
          model's own figure, sitting between what was typed and what is registered — the
          control that says the rules and the meter have not drifted apart. A
          <b>\u2248</b> beside it means a correction moved this line after the day was written,
          so its evidence is a share of the project's day rather than the line's own.
          Every other hours column carries a %:
          <b>keyboard</b> and <b>value time</b> read against F&O entry, so the row scans as one
          scale — what was typed, what is billed, and how much ceiling is left. <b>Work time</b>
          is measured time, and the % beside it is that against the 15+5 model — a control, not
          a number to bill on. <b>F&O entry</b> sits in the band between work and value time:
          turns and files per work hour decide how far up, saturating so more evidence always
          moves toward value time and never past it.</p>
        <div style="overflow-x:auto"><table class="autable">
          <thead><tr>
            <th>Date</th><th>Project</th><th>Proj ID</th><th>Activity</th><th>Task</th>
            <th class="r">Keyboard</th><th class="r">Measured</th><th class="r">Work time</th>
            <th class="r">F&O entry</th>
            <th class="r">Value time</th><th class="r">Turns/str</th><th class="r">Files</th>
            <th class="r">T5</th></tr></thead>
          <tbody>
            ${custOrder.map(c => html`
              <${Fragment} key=${c}>
                <tr class="augrp"><td colspan="13">${c}</td></tr>
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
  const [why, setWhy] = useState('');
  useEffect(() => { setWhy(''); setBusy(false); }, [line && line.date, line && line.project]);
  if (!line) return null;
  /* Dev onto a customer is the direction that over-bills, so it stays what it has always
     been: one line at a time, chosen deliberately at the review gate. The other direction
     -- a customer line that was really workspace work -- is on the line's own panel, where
     the line is. */
  const opts = projects.filter(p => p.key !== 'Dev')
    .sort((x, y) => (!x.key.startsWith('customers/')) - (!y.key.startsWith('customers/'))
      || x.key.localeCompare(y.key));
  const move = async to => {
    if (!to) return;
    setBusy(true);
    const j = await post('/api/reassign', {
      date: line.date,
      row: { project: line.project, proj_id: line.proj_id,
             activity: line.activity || '', fno_task: line.fno_task || '' },
      to, note: why.trim(),
    });
    setBusy(false);
    toast(j.message || (j.ok ? 'moved' : 'failed'));
    if (j.ok) onDone();
  };
  return html`
    <h3>Move Dev time</h3>
    <p class="sub" style="margin:2px 0 12px">${shortDay(line.date)} · ${hrs(line.claimed)} h
      on <code>Dev</code>${line.activity ? ' / ' + line.activity : ''}. This is the
      direction that <i>adds</i> to an invoice, so it is one line and one decision.</p>
    <div class="block">
      <div class="actrow">
        <span class="flabel" style="min-width:48px">Why</span>
        <input type="text" value=${why} onInput=${e => setWhy(e.target.value)}
               placeholder="goes into the day file with the move" aria-label="why"/>
      </div>
      <div class="actrow">
        <select class="mini" disabled=${busy} onChange=${e => move(e.target.value)}>
          <option value="">move to…</option>
          ${opts.map(p => html`<option key=${p.key} value=${p.key}>${p.key}${
            p.fno_code && p.fno_code !== 'UNSET' ? ' · ' + p.fno_code : ''}</option>`)}
        </select>
      </div>
      <p class="sub" style="margin:8px 0 0">The reverse — a customer line that was really
        workspace work — is on that line's own panel, under
        <b>This work cannot be invoiced</b>.</p>
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
      /* The month carries the same F&O entry figure as a week. It used to show plain work
         time, which meant the same Copy rows button meant two different things depending
         on which chip was lit -- and getting that wrong is an over- or under-registration
         into a live financial system. */
      const rkey = 'month' + back;
      return { rkey, label: per.label, w: null, split: false, file: 'fno-' + per.key,
               scale: scaleFrom(linesInMonth(D, per.key)) };
    }
    const raw = (D.audit.byWeek || {})[week];
    const rkey = auKey(D, week, per.key) || week;
    const split = rkey !== week;
    const w = split ? clipWeek(raw, new Set((E.ranges || {})[rkey] || []), D.today) : raw;
    return { rkey, w, scale: scaleFrom(w.lines), split, file: 'fno-' + week,
             label: split ? `${week} in ${per.label}` : `${week} · ${auRange(w)}` };
  }, [D, week, per, back]);

  /* Three sets, from one range.
   *
   * `rows` is what the blocks show: consolidated when the toggle is on, which packs the
   * hours onto as few days as possible so there are fewer lines to type. A consolidated row
   * is marked, because its date has moved and there is no single timesheet row behind it to
   * correct -- writing to the date it now shows would correct a different day.
   *
   * `gateRows` is what the readiness gate reads, and it is never consolidated. The gate
   * exists to fix lines, and a line you cannot correct is not one you can fix. It carries
   * the same scale, so its hours agree with the blocks even though its rows do not.
   */
  const { rows, gateRows, rawRows, rawByKey } = useMemo(() => {
    if (!D || !view) return { rows: [], gateRows: [], rawRows: [], rawByKey: {} };
    const E = D.entry;
    const inR = new Set((E.ranges || {})[view.rkey] || []);
    const raw = (E.rows || []).filter(r => inR.has(r.date));
    const base = merge
      ? ((E.merged || {})[view.rkey] || []).map(r => Object.assign({}, r, { merged: true }))
      : raw;
    const raws = {};
    raw.forEach(r => { raws[rowKey(r)] = r; });
    return { rows: scaleRows(base, view.scale), rawByKey: raws, rawRows: raw,
             gateRows: merge ? scaleRows(raw, view.scale) : null };
  }, [D, view, merge]);

  /* The timesheet line(s) a displayed row stands for. An ordinary row is one line on one
     day. A consolidated row is a whole week of one dimension packed onto a single date, so
     it stands for several -- and each of those is what actually gets corrected. Matching on
     the dimensions AS THE FILE HOLDS THEM, because consolidation moves the date and the
     hours and nothing else. */
  const behind = useMemo(() => {
    if (!sel) return [];
    const dim = r => [r.project, r.ws_proj_id || '', r.ws_activity || '',
                      r.ws_fno_task || ''].join('|');
    if (!sel.merged) {
      const one = rawByKey[rowKey(sel)];
      return one ? [one] : [];
    }
    return rawRows.filter(r => dim(r) === dim(sel))
      .slice().sort((x, y) => x.date.localeCompare(y.date));
  }, [sel, rawRows, rawByKey]);

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
                  title="the whole month at the same F&O entry figure a week gives; pick a week for the evidence behind it"
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

  const shortNow = (gateRows || rows).filter(r => (r.missing || []).length).length;
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
                                gate=${html`<${Ready} rows=${gateRows || rows}
                                                      periodLabel=${view.label}
                                                      scaled=${!!view.scale} D=${D}
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
                    <p class="sub" style="margin:0">The month and a week carry the same three
                      figures. Pick a week above to see the evidence each line rests on — the
                      funnel per day, the effort profile, and what is still open.</p></div>`
                  : html`
                    <${Fragment}>
                      <h2 class="ausplit">The week behind the numbers</h2>
                      <${Evidence} D=${D} w=${view.w} onReassign=${setDev}/>
                    <//>`}
              <//>`}
        <//>`}

      <${Drawer} open=${!!sel} onClose=${() => setSel(null)}>
        <${LineEditor} row=${sel} behind=${behind} D=${D} onDone=${reloadAll}/>
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
