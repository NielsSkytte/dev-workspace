// Reads ops/time: the timesheet (measured hours, what is billed) and the value record
// (keyboard hours and weighted hours). Pure functions; register.tsx does the file IO.

export type Line = { project: string; keyboard: number; measured: number; weighted: number }
export type Day = { date: string; lines: Line[] }

const num = (s: string): number => {
  const n = Number(String(s).trim().replace(',', '.'))
  return Number.isFinite(n) ? n : 0
}

// The first markdown table of a file whose header names `cols`, as rows keyed by header.
export function table(text: string, cols: string[]): Record<string, string>[] {
  const rows = text.split(/\r?\n/).filter(l => l.trim().startsWith('|'))
  for (let i = 0; i < rows.length; i++) {
    const head = cells(rows[i])
    if (!cols.every(c => head.includes(c))) continue
    const out: Record<string, string>[] = []
    for (let j = i + 2; j < rows.length; j++) {
      const c = cells(rows[j])
      if (c.length !== head.length) break
      out.push(Object.fromEntries(head.map((h, k) => [h, c[k]])))
    }
    return out
  }
  return []
}

const cells = (row: string): string[] => row.trim().replace(/^\||\|$/g, '').split('|').map(s => s.trim())

// One day: timesheet rows joined to value rows on project (summed per project).
export function day(date: string, timesheet: string | null, value: string | null): Day {
  const by = new Map<string, Line>()
  const get = (p: string) => by.get(p) ?? by.set(p, { project: p, keyboard: 0, measured: 0, weighted: 0 }).get(p)!
  for (const r of timesheet ? table(timesheet, ['Project', 'Hours']) : []) get(r.Project).measured += num(r.Hours)
  for (const r of value ? table(value, ['Project', 'Keyboard h', 'Weighted h']) : []) {
    const l = get(r.Project)
    l.keyboard += num(r['Keyboard h'])
    l.weighted += num(r['Weighted h'])
  }
  return { date, lines: [...by.values()].sort((a, b) => a.project.localeCompare(b.project)) }
}

export type Segments = { keyboard: number; measured: number; addon: number; below: number }

// Bar parts in cells: keyboard, measured beyond keyboard, weighted beyond measured.
// `below` > 0 when weighted is under measured (the value model supports less than billed).
export function segments(l: Line, cellsPerHour: number): Segments {
  const k = Math.min(l.keyboard, l.measured || l.keyboard)
  const m = Math.max(l.measured - k, 0)
  const a = Math.max(l.weighted - Math.max(l.measured, k), 0)
  const r = (h: number) => Math.round(h * cellsPerHour)
  return { keyboard: r(k), measured: r(m), addon: r(a), below: Math.max(l.measured - l.weighted, 0) }
}

export const short = (project: string): string => {
  const p = project.split('/')
  return p.length > 2 ? `${p[1]}/${p[p.length - 1]}` : project
}

export const fmt = (h: number): string => h.toFixed(2)

// Dates from `from` to `to`, inclusive, as YYYY-MM-DD (UTC calendar arithmetic).
export function dates(from: string, to: string): string[] {
  const out: string[] = []
  const d = new Date(`${from}T00:00:00Z`)
  const end = new Date(`${to}T00:00:00Z`)
  while (d <= end && out.length < 62) {
    out.push(d.toISOString().slice(0, 10))
    d.setUTCDate(d.getUTCDate() + 1)
  }
  return out
}

// "/hours" args: empty = last 7 days; "week" = Mon..today; "month" = 1st..today;
// "YYYY-MM-DD" = that day; "YYYY-MM-DD YYYY-MM-DD" = a range.
export function period(args: string, today: string): { from: string; to: string } {
  const a = args.trim().split(/\s+/).filter(Boolean)
  const iso = /^\d{4}-\d{2}-\d{2}$/
  if (a.length === 2 && iso.test(a[0]) && iso.test(a[1])) return { from: a[0], to: a[1] }
  if (a.length === 1 && iso.test(a[0])) return { from: a[0], to: a[0] }
  const t = new Date(`${today}T00:00:00Z`)
  if (a[0] === 'month') return { from: `${today.slice(0, 8)}01`, to: today }
  if (a[0] === 'week') {
    const back = (t.getUTCDay() + 6) % 7
    t.setUTCDate(t.getUTCDate() - back)
    return { from: t.toISOString().slice(0, 10), to: today }
  }
  t.setUTCDate(t.getUTCDate() - 6)
  return { from: t.toISOString().slice(0, 10), to: today }
}
