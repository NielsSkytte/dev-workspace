import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Ask, Board, Job, Last, Step } from '../types'

const last = atom({ plugin: 'quiet-transcript', key: 'last' } as const, null as Last | null)

const jobs = atom({ plugin: 'quiet-transcript', key: 'jobs' } as const, [] as Job[])
const plans = atom({ plugin: 'quiet-transcript', key: 'plans' } as const, {} as Record<string, Step[]>)
const carried = atom({ plugin: 'quiet-transcript', key: 'carried' } as const, {} as Record<string, { done: number; total: number }>)
const names = atom({ plugin: 'quiet-transcript', key: 'names' } as const, {} as Record<string, string>)
const tick = atom({ plugin: 'quiet-transcript', key: 'tick' } as const, 0)
const done = atom({ plugin: 'quiet-transcript', key: 'done' } as const, 0)
const board = atom({ plugin: 'quiet-transcript', key: 'board' } as const, {} as Record<string, Board>)
const turn = atom({ plugin: 'quiet-transcript', key: 'turn' } as const, 0)

const EDIT_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit']
const SHELL_TOOLS = ['Bash', 'PowerShell']
const AGENT_TOOLS = ['Agent', 'Task']
const PLAN_TOOL = 'mcp__quiet-transcript__plan'
const HIDDEN_TOOLS = [...SHELL_TOOLS, ...AGENT_TOOLS, PLAN_TOOL]
const FENCE = /```[^\n]*\n([\s\S]*?)```/g
const WIDTH = 24
const MAIN = 'main'

const RULE = [
  'Reply format for this user: the transcript hides shell commands, edits and code and instead shows a live',
  'progress band, so write no narration, status or description text around tool calls (leave a Bash/PowerShell',
  'description empty or a few words) and do not report results that need no action. Answer a direct question briefly.',
  'Keep ONE master plan for the whole objective: call ' + PLAN_TOOL + ' once with 3 to 8 main steps, each with 2 to 5',
  'children (the concrete substeps), and afterwards only update statuses by calling it with the same steps. Never',
  'shrink or restart the plan between turns; replace it only when the objective itself changes. Exactly one leaf',
  'is in_progress. When you dispatch an agent, tell it to keep its own plan the same way.',
  'THE BAND IS THE USER CONTROL PANEL, so EVERY turn call ' + PLAN_TOOL + ' once more before your last reply, even when no',
  'step changed, and fill the three board fields: next = the one immediate step; you = what you are waiting for from the',
  'user, each {kind: approve | do, text} (approve = a go for a named action, do = something only they can do; a',
  'question to the user is never put in you, it goes only in the Next for you block); claude = what the user is waiting',
  'for from you (a run, a build, a delivery) with its reason if it is held. An approval or action that needs the user must',
  'be in you, never only in prose. Leave you empty only when nothing is pending; remove an item when it is done.',
  'Do not stop to ask permission for work inside the plan that stays on this machine, in DEV or is reversible: keep',
  'working until the plan is done or a step needs the user (a decision, an action only they can take, a customer-facing',
  'or PROD-changing step). Stop only for that, and say what you need in the Next for you block.',
  'Volunteer information only when it is a showstopper that needs the user to act: then end the reply with a',
  'block that starts with the exact line "## ▶ Next for you", followed by a numbered list of at most 5 items,',
  'each one action with the concrete command, value or choice: the items of the you field plus any questions. Questions',
  'to the user go only in that block.',
  'If nothing needs the user, say nothing beyond the answer. Keep file contents and code out of replies.',
].join(' ')

const baseName = (input: unknown): string => {
  const i = input as { file_path?: string; notebook_path?: string } | undefined
  const path = String(i?.file_path ?? i?.notebook_path ?? '')
  return path.split(new RegExp('[' + String.fromCharCode(92) + '/]')).pop() || path
}

const bar = (frac: number, width: number): { on: number; off: number } => {
  const on = Math.max(0, Math.min(width, Math.round(frac * width)))
  return { on, off: width - on }
}

const leavesOf = (steps: Step[]): { title: string; status: string }[] =>
  steps.flatMap(s => (s.children && s.children.length > 0 ? s.children : [s]))

const jobPct =(secs: number, est: number): number => {
  const r = secs / est
  return Math.min(99, Math.round(r <= 0.9 ? r * 90 : 90 + 9 * (1 - Math.exp(-(r - 0.9) * 2))))
}

export const register: Register = (on, options) => {
  let timer: { cancel: () => void } | undefined

  on('session.start', async ($, e, next) => {
    await $.tool.register({
      name: 'plan',
      isDeferred: false,
      description:
        'One master plan for the whole job: 3-8 main steps, each with 2-5 children, a status each. Call again with the same steps to update statuses; do not restart it. Also carries the board: next step, what you wait for from the user, what the user waits for from you.',
      inputSchema: {
        type: 'object',
        properties: {
          next: { type: 'string', description: 'The one immediate next step.' },
          you: {
            type: 'array',
            description: 'What waits for the user: approve (a go for a named action), do (an action only they can take). Questions go in the reply only.',
            items: {
              type: 'object',
              properties: { kind: { type: 'string', enum: ['approve', 'do'] }, text: { type: 'string' } },
              required: ['kind', 'text'],
            },
          },
          claude: { type: 'array', description: 'What the user waits for from you, with the reason if it is held.', items: { type: 'string' } },
          steps: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                title: { type: 'string' },
                status: { type: 'string', enum: ['pending', 'in_progress', 'completed'] },
                children: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      title: { type: 'string' },
                      status: { type: 'string', enum: ['pending', 'in_progress', 'completed'] },
                    },
                    required: ['title', 'status'],
                  },
                },
              },
              required: ['title', 'status'],
            },
          },
        },
        required: ['steps'],
      },
    })
    return next(e)
  })

  // The plan tool: replaces this loop's step list.
  on('tool.call', { tool: PLAN_TOOL }, async ($, e) => {
    const loop = (e as { agentId?: string }).agentId ?? MAIN
    const call = e as unknown as { steps?: Step[]; next?: string; you?: Ask[]; claude?: string[] }
    const steps = (call.steps ?? []).slice(0, 12)
    const prev = (await read($, plans))[loop] ?? []
    const prevLeaves = leavesOf(prev)
    const sameJob = prevLeaves.some(l => leavesOf(steps).some(n => n.title === l.title))
    if (prevLeaves.length > 0 && !sameJob && prevLeaves.every(l => l.status === 'completed')) {
      await update($, carried, c => ({ ...c, [loop]: { done: (c[loop]?.done ?? 0) + prevLeaves.length, total: (c[loop]?.total ?? 0) + prevLeaves.length } }))
    }
    await update($, plans, p => ({ ...p, [loop]: steps }))
    const at = await $.clock.now()
    const nowTurn = await read($, turn)
    await update($, board, b => ({
      ...b,
      [loop]: { next: String(call.next ?? ''), you: (call.you ?? []).filter(a => a.kind !== ('answer' as string)).slice(0, 5), claude: (call.claude ?? []).slice(0, 5), at, turn: nowTurn },
    }))
    return { result: 'ok', text: 'Plan shown to the user.' } as never
  })

  // Every shell command and agent is a job with an estimated duration learned from earlier runs.
  on('tool.call', async ($, e, next) => {
    const tool = e.tool as string
    const isShell = SHELL_TOOLS.includes(tool)
    const isAgent = AGENT_TOOLS.includes(tool)
    if (!isShell && !isAgent) return next(e)
    const loop = (e as { agentId?: string }).agentId ?? MAIN
    const input = e as unknown as { subagent_type?: string; description?: string; command?: string }
    const id = e.tool_use_id as string
    const label = isAgent ? `agent ${input.subagent_type ?? ''}`.trim() : tool === 'PowerShell' ? 'powershell' : 'shell'
    const startedAt = await $.clock.now()
    const raw = isAgent ? (input.subagent_type ?? 'agent') : String(input.command ?? '').trim().split(/\s+/)[0]
    const key = `${isAgent ? 'a' : 's'}:${raw.slice(0, 40)}`
    const hist = ((await $.store.get('dur')) ?? {}) as Record<string, number[]>
    const past = (hist[key] ?? []).slice().sort((a, b) => a - b)
    const est = past.length >= 2 ? past[Math.floor(past.length / 2)] : isAgent ? 120 : 8
    await update($, jobs, js => [...js, { id, loop, label, key, startedAt, est }])
    if (isShell && loop === MAIN) {
      await update($, last, () => ({ tool: label, cmd: String(input.command ?? ''), startedAt, endedAt: 0, state: 'running' }))
    }

    if (loop !== MAIN) {
      const known = await read($, names)
      if (!known[loop]) {
        const list = await $.agent.list()
        const a = list.find(x => x.id === loop)
        if (a) await update($, names, n => ({ ...n, [loop]: `${a.agentType ?? 'agent'}: ${a.description}`.slice(0, 48) }))
      }
    }

    const out = await next(e)
    const failed = out.deny !== undefined || out.isError === true
    const took = Math.max(1, ((await $.clock.now()) - startedAt) / 1000)
    if (!failed) {
      const fresh = ((await $.store.get('dur')) ?? {}) as Record<string, number[]>
      fresh[key] = [...(fresh[key] ?? []), Math.round(took)].slice(-12)
      await $.store.set('dur', fresh)
    }
    await update($, jobs, js => js.filter(j => j.id !== id))
    await update($, done, n => n + 1)
    if (isShell && loop === MAIN) {
      const endedAt = await $.clock.now()
      await update($, last, l => (l && l.startedAt === startedAt ? { ...l, endedAt, state: failed ? 'failed' : 'done' } : l))
    }
    // the failure line stays until a later call succeeds, so it does not sit there for the rest of the session
    if (failed) $.ui.status(`${label} failed`)
    else $.ui.status(undefined)
    return out
  })

  on('turn.start', async ($, e, next) => {
    // A plan that finished last turn is cleared now; an unfinished one carries on.
    const before = await read($, plans)
    const kept: Record<string, Step[]> = {}
    for (const [k, v] of Object.entries(before)) {
      if (leavesOf(v).some(l => l.status !== 'completed')) kept[k] = v
      else if (v.length > 0) {
        await update($, carried, c => ({ ...c, [k]: { done: (c[k]?.done ?? 0) + leavesOf(v).length, total: (c[k]?.total ?? 0) + leavesOf(v).length } }))
      }
    }
    await update($, plans, () => kept)
    timer?.cancel()
    timer = $.clock.every(400, () => { void update($, tick, n => n + 1) })
    void update($, done, () => 0)
    await update($, turn, n => n + 1)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    timer?.cancel()
    timer = undefined
    await update($, jobs, () => [])
    return next(e)
  })

  // Hidden rows: shell, agent, plan and edit calls draw nothing unless they failed.
  on('ui.render', { component: 'ToolUse', surface: 'terminal' }, ($, e, next) => {
    const p = e.props
    const { Box, Text } = $.ui.resolve(e)
    if (EDIT_TOOLS.includes(p.tool)) {
      const verb = p.isErrored ? 'failed' : p.isRunning ? 'editing' : 'edited'
      return <Text dimColor>{`✎ ${verb} ${baseName(p.input)} (code hidden)`}</Text>
    }
    if (!HIDDEN_TOOLS.includes(p.tool)) return next(e)
    if (p.isErrored || p.isInterrupted) return <Text color="red">{`✘ ${p.tool} ${p.isInterrupted ? 'stopped' : 'failed'}`}</Text>
    return <Box />
  })

  on('ui.render', { component: 'ToolResult', surface: 'terminal' }, ($, e, next) => {
    const p = e.props
    if (!EDIT_TOOLS.includes(p.tool) && !HIDDEN_TOOLS.includes(p.tool)) return next(e)
    if (p.isErrored && !EDIT_TOOLS.includes(p.tool)) return next(e)
    const { Box } = $.ui.resolve(e)
    return <Box />
  })

  // "Ran 2 shell commands" fold lines carry nothing now that the band shows the latest command.
  on('ui.render', { component: 'ToolGroup', surface: 'terminal' }, ($, e, next) => {
    const calls = e.props.calls
    const isQuiet = calls.length > 0 && calls.every(c => SHELL_TOOLS.includes(c.tool) && !c.isErrored)
    if (!isQuiet) return next(e)
    const { Box } = $.ui.resolve(e)
    return <Box />
  })

  // Fenced code blocks in replies fold to a one-line marker; ctrl+o still shows the stored message.
  on('ui.render', { component: 'AssistantMessage' }, ($, e, next) => {
    const text = e.props.text
    if (!text.includes('```')) return next(e)
    const folded = text.replace(FENCE, (_m, body: string) => {
      const lines = body.replace(/\n$/, '').split('\n').length
      return `▸ code hidden (${lines} lines)`
    })
    return next({ ...e, props: { ...e.props, text: folded } })
  })

  // Your own prompts: bold, coloured, with a marker, so they are easy to find when scrolling.
  on('ui.render', { component: 'UserMessage', surface: 'terminal' }, ($, e, next) => {
    if (e.props.origin.kind !== 'composer' || e.props.isExpanded) return next(e)
    const { Text } = $.ui.resolve(e)
    return <Text bold color="yellow">{`▌ ${e.props.text}`}</Text>
  })

  // The progress band: one section per agent/thread, each with its plan and its running jobs.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const running = await read($, jobs)
    const allPlans = await read($, plans)
    const loops = [...new Set([MAIN, ...running.map(j => j.loop), ...Object.keys(allPlans)])].filter(
      l => running.some(j => j.loop === l) || (allPlans[l] ?? []).length > 0,
    )
    const lastCmd = await read($, last)
    if (e.props.hasSurvey || (loops.length === 0 && !lastCmd)) return next(e)
    await read($, tick)
    const label = await read($, names)
    const finished = await read($, done)
    const before = await read($, carried)
    const boards = await read($, board)
    const thisTurn = await read($, turn)
    const now = await $.clock.now()
    const { Box, Text } = $.ui.resolve(e)
    const rowsLeft = Math.max(6, e.props.maxRows - 2)
    let used = 0

    const jobRow = (j: Job) => {
      const secs = Math.max(0, (now - j.startedAt) / 1000)
      const pct = jobPct(secs, j.est)
      const b = bar(pct / 100, WIDTH)
      const color = pct < 40 ? 'yellow' : pct < 80 ? 'cyan' : 'greenBright'
      used += 1
      return (
        <Box key={j.id}>
          <Text color="cyan">{`  ${j.label.padEnd(16)} `}</Text>
          <Text color={color}>{'█'.repeat(b.on)}</Text>
          <Text dimColor>{'░'.repeat(b.off)}</Text>
          <Text bold>{` ${String(pct).padStart(2)}%`}</Text>
          <Text dimColor>{` ${Math.round(secs)}s of ~${Math.round(j.est)}s`}</Text>
        </Box>
      )
    }

    // The control panel: next step, what waits for the user, what the user waits for. Flagged when no recent turn updated it.
    const KIND: Record<string, string> = { approve: 'approve', do: 'do     ' }
    const boardRows = (loop: string, b: Board | undefined, nowTurn: number, nowMs: number) => {
      if (!b || (!b.next && b.you.length === 0 && b.claude.length === 0)) return null
      const age = Math.max(0, Math.round((nowMs - b.at) / 60000))
      const stale = nowTurn - b.turn >= 2
      const room = Math.max(40, e.props.bodyColumns - 14)
      const cut = (t: string) => (t.length > room ? t.slice(0, room - 1) + '…' : t)
      used += (b.next ? 1 : 0) + b.you.length + b.claude.length + (stale ? 1 : 0)
      return (
        <Box key={`b-${loop}`} flexDirection="column">
          {b.next ? <Text color="greenBright" bold>{`  ▶ Next   ${cut(b.next)}`}</Text> : null}
          {b.you.map((a, i) => (
            <Text key={`y${i}`} color="yellow" bold>{`  ▌ You ${KIND[a.kind] ?? a.kind}  ${cut(a.text)}`}</Text>
          ))}
          {b.claude.map((c, i) => (
            <Text key={`c${i}`} color="cyan">{`  ◌ Me     ${cut(c)}`}</Text>
          ))}
          {stale ? <Text color="red">{`  ! board not updated for ${nowTurn - b.turn} turns (${age} min): ask for a refresh`}</Text> : null}
        </Box>
      )
    }

    const sections = loops.map(loop => {
      const steps = allPlans[loop] ?? []
      const mine = running.filter(j => j.loop === loop)
      const title = loop === MAIN ? 'main' : (label[loop] ?? `agent ${loop.slice(0, 6)}`)
      const leaves = leavesOf(steps)
      const prior = before[loop] ?? { done: 0, total: 0 }
      const doneN = prior.done + leaves.filter(s => s.status === 'completed').length
      const active = mine[0]
      const partial = active ? jobPct((now - active.startedAt) / 1000, active.est) / 100 : 0
      const total = prior.total + leaves.length
      const frac = total ? Math.min(1, (doneN + (leaves.some(s => s.status === 'in_progress') ? partial : 0)) / total) : 0
      const b = bar(frac, WIDTH)
      used += 1
      return (
        <Box key={loop} flexDirection="column">
          <Box>
            <Text bold color="magenta">{`${title} `}</Text>
            {steps.length > 0 && <Text color="greenBright">{'█'.repeat(b.on)}</Text>}
            {steps.length > 0 && <Text dimColor>{'░'.repeat(b.off)}</Text>}
            {steps.length > 0 && <Text bold>{` ${Math.round(frac * 100)}%  ${doneN}/${total} steps`}</Text>}
          </Box>
          {steps.map((s, i) => {
            const kids = s.children ?? []
            const kDone = kids.filter(k => k.status === 'completed').length
            const status =
              kids.length > 0
                ? kDone === kids.length ? 'completed' : kids.some(k => k.status !== 'pending') ? 'in_progress' : 'pending'
                : s.status
            const open = status === 'in_progress'
            if (used >= rowsLeft && status === 'completed') return null
            used += 1
            const mark = status === 'completed' ? '✔' : status === 'in_progress' ? '▶' : '○'
            const color = status === 'completed' ? 'green' : status === 'in_progress' ? 'cyan' : undefined
            return (
              <Box key={i} flexDirection="column">
                <Text color={color} dimColor={status === 'pending'} bold={open}>
                  {`  ${mark} ${s.title}${kids.length > 0 ? `  ${kDone}/${kids.length}` : ''}`}
                </Text>
                {open && used < rowsLeft && kids.map((k, j) => {
                  used += 1
                  const km = k.status === 'completed' ? '✔' : k.status === 'in_progress' ? '▸' : '·'
                  const kc = k.status === 'completed' ? 'green' : k.status === 'in_progress' ? 'cyan' : undefined
                  return (
                    <Text key={j} color={kc} dimColor={k.status === 'pending'} bold={k.status === 'in_progress'}>
                      {`      ${km} ${k.title}`}
                    </Text>
                  )
                })}
              </Box>
            )
          })}
          {boardRows(loop, boards[loop], thisTurn, now)}
          {mine.slice(0, 3).map(jobRow)}
        </Box>
      )
    })

    const cmdBox = (l: Last) => {
      const secs = Math.max(0, Math.round(((l.state === 'running' ? now : l.endedAt) - l.startedAt) / 1000))
      const room = Math.max(20, e.props.bodyColumns - 6)
      const flat = l.cmd.split(/\s*\n\s*/).filter(x => x.length > 0).join('  ⏎  ')
      const shown = flat.length > room * 2 ? flat.slice(0, room * 2 - 1) + '…' : flat
      const mark = l.state === 'running' ? '▶' : l.state === 'done' ? '✔' : '✘'
      const color = l.state === 'running' ? 'cyan' : l.state === 'done' ? 'green' : 'red'
      return (
        <Box key="last" flexDirection="column" borderStyle="round" borderColor={color} paddingX={1}>
          <Text color={color} bold>{`${mark} latest ${l.tool}  ${secs}s`}</Text>
          <Text dimColor wrap="truncate-end">{shown}</Text>
        </Box>
      )
    }

    return (
      <Box flexDirection="column">
        {sections}
        {lastCmd && cmdBox(lastCmd)}
        <Text dimColor>{`${running.length} running · ${finished} done`}</Text>
      </Box>
    )
  })

  // Every reply that needs you ends with a "Next for you" block; the plan rule rides along.
  on('prompt.compose', async ($, e, next) => {
    const out = await next(e)
    return { sections: [...out.sections, { id: 'quiet-transcript:next', text: RULE, scope: 'session' }] }
  })
}
