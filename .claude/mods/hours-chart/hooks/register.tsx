import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Period } from '../types'
import { dates, day, fmt, period, segments, short } from './data'
import type { Day } from './data'

const PANE = 'hours-chart'
const TIME = 'C:/Dev/ops/time'
const shown = atom({ plugin: 'hours-chart', key: 'period' } as const, { from: '', to: '' } as Period)

const today = (): string => {
  const d = new Date()
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

// The rollup and the value derivation are what "showing hours" runs; the pane follows them.
const SHOWS_HOURS = /ops[\\/]+time[\\/]+(rollup|value)\.py/

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'hours',
      description: 'Hours as bars: keyboard, measured, weighted add-on. Args: week | month | YYYY-MM-DD [YYYY-MM-DD]',
    })
    return next(e)
  })

  on('command.run', { command: 'hours' }, async ($, e) => {
    const p = period(e.args, today())
    await update($, shown, () => p)
    const opened = await $.ui.open({ id: PANE, title: `Hours ${p.from} .. ${p.to}` })
    return { text: opened.isPlaced ? `Hours pane: ${p.from} .. ${p.to}.` : 'Hours pane waits for a wider terminal.' }
  })

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    const cmd = String((e.input as { command?: unknown }).command ?? '')
    if (SHOWS_HOURS.test(cmd)) {
      const p = period('week', today())
      await update($, shown, () => p)
      void $.ui.open({ id: PANE, title: `Hours ${p.from} .. ${p.to}` })
    }
    return ran
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const p = await read($, shown)
    const range = p.from ? p : period('', today())
    const days: Day[] = []
    for (const d of dates(range.from, range.to)) {
      const ts = await $.fs.read(`${TIME}/timesheet/${d.slice(0, 7)}/${d}.md`).catch(() => null)
      const val = await $.fs.read(`${TIME}/value/${d}.md`)
        .catch(() => $.fs.read(`${TIME}/value/${d.slice(0, 7)}/${d}.md`)).catch(() => null)
      const one = day(d, ts as string | null, val as string | null)
      if (one.lines.length) days.push(one)
    }

    const LABEL = 22
    const NUMS = 30
    const cols = Math.max(40, e.viewport?.columns ?? 100)
    const peak = Math.max(0.5, ...days.flatMap(d => d.lines.map(l => Math.max(l.measured, l.weighted, l.keyboard))))
    const perHour = Math.max(1, cols - LABEL - NUMS - 2) / peak

    const sum = (d: Day, k: 'keyboard' | 'measured' | 'weighted') => d.lines.reduce((s, l) => s + l[k], 0)
    const tot = { keyboard: 0, measured: 0, weighted: 0 }
    for (const d of days) for (const k of ['keyboard', 'measured', 'weighted'] as const) tot[k] += sum(d, k)

    return (
      <Box flexDirection="column">
        <Text>
          <Text color="cyan">█ keyboard</Text>  <Text color="blue">▓ measured</Text>  <Text color="green">░ weighted add-on</Text>  <Text color="yellow">◂ weighted below measured</Text>
        </Text>
        {days.length === 0 && <Text dimColor>No timesheet or value record in {range.from} .. {range.to}.</Text>}
        {days.map(d => (
          <Box flexDirection="column">
            <Text bold>
              {d.date}  kb {fmt(sum(d, 'keyboard'))}  meas {fmt(sum(d, 'measured'))}  wtd {fmt(sum(d, 'weighted'))}
            </Text>
            {d.lines.map(l => {
              const s = segments(l, perHour)
              return (
                <Text wrap="truncate">
                  {short(l.project).padEnd(LABEL).slice(0, LABEL)}
                  <Text color="cyan">{'█'.repeat(s.keyboard)}</Text>
                  <Text color="blue">{'▓'.repeat(s.measured)}</Text>
                  <Text color="green">{'░'.repeat(s.addon)}</Text>
                  <Text dimColor> {fmt(l.keyboard)} / {fmt(l.measured)} / {fmt(l.weighted)}</Text>
                  {s.below > 0 && <Text color="yellow"> ◂ -{fmt(s.below)}</Text>}
                </Text>
              )
            })}
          </Box>
        ))}
        {days.length > 1 && (
          <Text bold>
            Period  kb {fmt(tot.keyboard)}  meas {fmt(tot.measured)}  wtd {fmt(tot.weighted)}  (weighted {tot.measured ? Math.round((tot.weighted / tot.measured) * 100) : 0}% of measured)
          </Text>
        )}
      </Box>
    )
  })
}
