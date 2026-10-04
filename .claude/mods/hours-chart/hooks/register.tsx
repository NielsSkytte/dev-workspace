import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Period } from '../types'
import { argv, byDate, fmt, segments, short } from './data'
import type { Line } from './data'

const PANE = 'hours-chart'
const HOURS = 'C:/Dev/ops/bin/hours.py'
const shown = atom({ plugin: 'hours-chart', key: 'period' } as const, { from: '', to: '' } as Period)

// The rollup and the value derivation are what "showing hours" runs; the pane follows them.
const SHOWS_HOURS = /ops[\\/]+(time[\\/]+(rollup|value)|bin[\\/]+hours)\.py/

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'hours',
      description: 'Hours as bars: keyboard, registered, weighted add-on. Args: last | month | YYYY-MM-DD [YYYY-MM-DD]',
    })
    return next(e)
  })

  on('command.run', { command: 'hours' }, async ($, e) => {
    // `from` carries the raw args; hours.py resolves the period itself.
    await update($, shown, () => ({ from: e.args.trim() || 'week', to: '' }))
    const opened = await $.ui.open({ id: PANE, title: `Hours ${e.args.trim() || 'this week'}` })
    return { text: opened.isPlaced ? 'Hours pane opened.' : 'Hours pane waits for a wider terminal.' }
  })

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    const cmd = String((e.input as { command?: unknown }).command ?? '')
    if (SHOWS_HOURS.test(cmd)) {
      await update($, shown, () => ({ from: 'week', to: '' }))
      void $.ui.open({ id: PANE, title: 'Hours this week' })
    }
    return ran
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const p = await read($, shown)
    const args = p.from && p.from !== 'week' ? argv(p.from) : []
    let data: { from: string; to: string; lines: Line[] } | null = null
    let error = ''
    try {
      const r = await $.process.run(['python', HOURS, ...args, '--json'], { timeoutMs: 120000 })
      if (r.exitCode === 0) data = JSON.parse(r.stdout)
      else error = r.stderr.split('\n').filter(Boolean).slice(-1)[0] ?? `exit ${r.exitCode}`
    } catch (err) {
      error = String(err)
    }
    if (!data) return <Text color="red">hours.py failed: {error}</Text>

    const days = byDate(data.lines)
    const LABEL = 24
    const NUMS = 36
    const cols = Math.max(40, e.viewport?.columns ?? 100)
    const peak = Math.max(0.5, ...data.lines.map(l => Math.max(l.claimed, l.weighted, l.keyboard)))
    const perHour = Math.max(1, cols - LABEL - NUMS - 2) / peak
    const sum = (ls: Line[], k: 'keyboard' | 'measured' | 'claimed' | 'weighted') => ls.reduce((s, l) => s + l[k], 0)

    return (
      <Box flexDirection="column">
        <Text>
          <Text color="cyan">█ keyboard</Text>  <Text color="blue">▓ registered</Text>  <Text color="green">░ weighted add-on</Text>  <Text color="yellow">◂ weighted below registered</Text>  <Text dimColor>kb / measured / registered / weighted</Text>
        </Text>
        {days.length === 0 && <Text dimColor>No time in {data.from} .. {data.to}.</Text>}
        {days.map(([date, ls]) => (
          <Box flexDirection="column">
            <Text bold>
              {date}{ls.some(l => l.live) ? ' (live)' : ''}  kb {fmt(sum(ls, 'keyboard'))}  meas {fmt(sum(ls, 'measured'))}  reg {fmt(sum(ls, 'claimed'))}  wtd {fmt(sum(ls, 'weighted'))}
            </Text>
            {ls.map(l => {
              const s = segments(l, perHour)
              const label = `${short(l.project)}${l.task ? ` ${l.task}` : ''}`
              return (
                <Text wrap="truncate">
                  {label.padEnd(LABEL).slice(0, LABEL)}
                  <Text color="cyan">{'█'.repeat(s.keyboard)}</Text>
                  <Text color="blue">{'▓'.repeat(s.registered)}</Text>
                  <Text color="green">{'░'.repeat(s.addon)}</Text>
                  <Text dimColor> {fmt(l.keyboard)} / {fmt(l.measured)} / {fmt(l.claimed)} / {fmt(l.weighted)}{l.shared ? ' shared' : ''}</Text>
                  {s.below > 0 && <Text color="yellow"> ◂ -{fmt(s.below)}</Text>}
                </Text>
              )
            })}
          </Box>
        ))}
        {days.length > 1 && (
          <Text bold>
            {data.from} .. {data.to}  kb {fmt(sum(data.lines, 'keyboard'))}  meas {fmt(sum(data.lines, 'measured'))}  reg {fmt(sum(data.lines, 'claimed'))}  wtd {fmt(sum(data.lines, 'weighted'))}
          </Text>
        )}
        <Text dimColor>Source: ops/bin/hours.py = the dashboard Time page. F&O entry figure: dashboard entry page.</Text>
      </Box>
    )
  })
}
