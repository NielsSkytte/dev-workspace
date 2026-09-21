/* Time -- what gets invoiced.
 *
 * The hours chart and the by-project chart for a chosen month, the internal-hours
 * position, and the hygiene that stops a number reaching F&O wrong.
 *
 * The week timesheet and the month overview are NOT here yet: they carry the F&O entry
 * blocks and the reassignment write path, and porting those unverified would put the
 * billing surface at risk. They stay on the page they are on, linked below, until they
 * are ported with the same care. See ops/dashboard-plan.md.
 */
import {
  html, render, useState, useMemo, useRef, useEffect,
  Shell, Tile, Empty, Fragment, useData, hrs, label,
} from './app.js';

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'];
const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const pad = n => String(n).padStart(2, '0');

/* Field-wise, never through Date(string) -- that reads the date as UTC and shifts it. */
const dowOf = ds => {
  const [y, m, d] = ds.split('-').map(Number);
  return new Date(y, m - 1, d).getDay();
};
const dowName = ds => DOW[dowOf(ds)];
const isWeekend = ds => dowOf(ds) === 0 || dowOf(ds) === 6;

/* Every date in the selected month, so an untracked day renders as an explicit 0
   rather than vanishing from the axis. */
function periodDays(today, period) {
  const [Y, M] = today.split('-').map(Number);
  const y = period === 'last' ? (M === 1 ? Y - 1 : Y) : Y;
  const m = period === 'last' ? (M === 1 ? 12 : M - 1) : M;
  const days = [];
  for (let d = 1; d <= new Date(y, m, 0).getDate(); d++) days.push(`${y}-${pad(m)}-${pad(d)}`);
  return { days, label: `${MONTHS[m - 1]} ${y}`, prefix: `${y}-${pad(m)}` };
}

const scopeOf = k => (k === 'Dev' ? 'dev' : k.startsWith('own/') ? 'own' : 'customers');

/* ---------- hours chart ---------- */

function HoursChart({ data, tip }) {
  const W = 720, H = 200, PB = 22, PL = 30;
  const max = Math.max(4, ...data.map(d => d.billable + d.internal));
  const iw = W - PL;
  const step = iw / data.length;
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

/* ---------- by project ---------- */

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

/* ---------- internal hours ---------- */

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
              ${cand.length} of ${rows.length} stretches were worked in a session that also touched a
              customer project — <b>${hrs(ch)} h</b> worth. Those are the candidates to move; the
              rest look genuinely internal.</p>
            <p class="sub" style="margin:0 0 8px">
              Split per session to stay traceable, which adds a buffer and a 0.5 h floor per fragment,
              so this runs above the ${hrs(D.totals.month_internal)} h on the tile. Decide <i>what</i>
              moves here; take the figures from the day's timesheet.</p>
            ${Object.entries(byProj).sort((a, b) => b[1] - a[1]).map(([p, v]) => html`
              <div key=${p} style="display:flex;justify-content:space-between;gap:8px;padding:3px 0">
                <span>${p}</span><b>${hrs(v)} h</b></div>`)}
            <p class="sub" style="margin:10px 0 0">
              Tracing a stretch to a project, task and activity is on the week timesheet below.</p>
          <//>`}
      </div>
    </section>`;
}

/* ---------- hygiene ---------- */

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

/* ---------- page ---------- */

function App() {
  const { data: D, err, stamp, reload, auto, setAuto } = useData('/api/data');
  const [period, setPeriod] = useState('this');
  const [scope, setScope] = useState({ customers: true, own: true, dev: true });
  const [tip, setTip] = useState(null);
  const tipRef = useRef(null);

  const per = useMemo(() => (D ? periodDays(D.today, period) : null), [D, period]);

  const daily = useMemo(() => {
    if (!D) return [];
    const src = {};
    D.daily.forEach(d => { src[d.date] = d; });
    return per.days.map(date => {
      const v = src[date] || { customers: 0, own: 0, dev: 0 };
      return {
        date,
        billable: scope.customers ? v.customers : 0,
        internal: (scope.own ? v.own : 0) + (scope.dev ? v.dev : 0),
      };
    });
  }, [D, per, scope]);

  const byProject = useMemo(() => {
    if (!D) return [];
    const inPeriod = new Set(per.days);
    return D.projects
      .filter(p => scope[scopeOf(p.key)])
      .map(p => ({
        p,
        hrs: Object.entries(p.by_date).reduce((s, [d, v]) => s + (inPeriod.has(d) ? v : 0), 0),
      }))
      .filter(r => r.hrs > 0)
      .sort((a, b) => b.hrs - a.hrs)
      .slice(0, 9);
  }, [D, per, scope]);

  const total = daily.reduce((s, d) => s + d.billable + d.internal, 0);

  useEffect(() => {
    const n = tipRef.current;
    if (!n) return;
    n.style.display = tip ? 'block' : 'none';
  }, [tip]);

  const onTip = (e, d) => {
    if (!d) { setTip(null); return; }
    setTip(d);
    const n = tipRef.current;
    if (n) {
      n.style.left = Math.min(e.clientX + 14, innerWidth - 220) + 'px';
      n.style.top = Math.max(e.clientY - 70, 8) + 'px';
    }
  };

  const tiles = D ? [
    html`<${Tile} key="1" label="Billable this month" value=${hrs(D.totals.month_billable)} foot="h"/>`,
    html`<${Tile} key="2" label="Internal this month" value=${hrs(D.totals.month_internal)} foot="Dev and own/"/>`,
    html`<${Tile} key="3" label="This week" value=${hrs(D.totals.week_billable + D.totals.week_internal)} foot=${D.week}/>`,
    html`<${Tile} key="4" label="Unfinalized" value=${D.hygiene.unfinalized.length}
                  hot=${D.hygiene.unfinalized.length > 0} foot="days without a timesheet"/>`,
  ] : [];

  return html`
    <${Shell} here="/time" title="Time" sub=${per ? per.label : 'loading…'}
              stamp=${stamp} auto=${auto} onAuto=${() => setAuto(a => !a)} onRefresh=${reload}
              tiles=${tiles}>
      ${err ? html`<div class="alert">Cannot reach the server: ${err}</div>` : null}
      ${!D ? null : html`
        <${Fragment}>
          <div class="filterbar">
            <span class="flabel">Period</span>
            ${[['this', 'This month'], ['last', 'Last month']].map(([k, t]) => html`
              <button key=${k} class=${'chip' + (period === k ? ' on' : '')}
                      onClick=${() => setPeriod(k)}>${t}</button>`)}
            <span class="fsep"></span>
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

          <section>
            <h2>Timesheet</h2>
            <div class="card">
              <p style="margin:0 0 10px">The F&O entry blocks, the week audit and the
                reassignment path have not moved yet — they are the surface that produces an
                invoice, and they move once they can be verified the same way as the rest.</p>
              <div style="display:flex;gap:10px;flex-wrap:wrap">
                <a class="chip" href="/overview#timesheet/audit">Week timesheet →</a>
                <a class="chip" href="/overview#timesheet/month">Month overview →</a>
              </div>
            </div>
          </section>
        <//>`}

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
