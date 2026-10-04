// Pure helpers. The numbers themselves come from `python C:/Dev/ops/bin/hours.py --json`: the
// dashboard Time page's own lines (timesheet + measurement + value records, with the /log
// corrections applied), so the chart never disagrees with the Time page.

export type Line = {
  date: string; project: string; activity: string; task: string
  keyboard: number; measured: number; claimed: number; weighted: number
  shared: boolean; billable: boolean; live: boolean
}

export type Segments = { keyboard: number; registered: number; addon: number; below: number }

// Bar parts in cells: keyboard, registered beyond keyboard, weighted beyond registered.
// `below` > 0 when weighted is under the registered hours.
export function segments(l: Line, cellsPerHour: number): Segments {
  const k = Math.min(l.keyboard, l.claimed || l.keyboard)
  const reg = Math.max(l.claimed - k, 0)
  const add = Math.max(l.weighted - Math.max(l.claimed, k), 0)
  const r = (h: number) => Math.round(h * cellsPerHour)
  return { keyboard: r(k), registered: r(reg), addon: r(add), below: Math.max(l.claimed - l.weighted, 0) }
}

export const short = (project: string): string => {
  const p = project.split('/')
  return p.length > 2 ? `${p[1]}/${p[p.length - 1]}` : project
}

export const fmt = (h: number): string => h.toFixed(2)

export function byDate(lines: Line[]): [string, Line[]][] {
  const m = new Map<string, Line[]>()
  for (const l of lines) (m.get(l.date) ?? m.set(l.date, []).get(l.date)!).push(l)
  return [...m.entries()].sort(([a], [b]) => a.localeCompare(b))
}

// "/hours" args are passed to hours.py as they are: empty = this week, "last", "month",
// "YYYY-MM-DD" or "YYYY-MM-DD YYYY-MM-DD".
export const argv = (args: string): string[] => args.trim().split(/\s+/).filter(Boolean)
