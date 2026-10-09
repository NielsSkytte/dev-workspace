import { atom, read, update } from 'claude-code'
import type { Register, AgentInfo } from 'claude-code'

import type { Step, StepState, Thread } from '../types'

const PANE = 'work-view'
const MAIN = 'main'
const threads = atom({ plugin: 'work-view', key: 'threads' } as const, [] as Thread[])
const showCode = atom({ plugin: 'work-view', key: 'showCode' } as const, false)
const mainBusy = atom({ plugin: 'work-view', key: 'mainBusy' } as const, false)

const base = (p: unknown) => String(p ?? '').split(/[\\/]/).pop() || 'a file'

// One plain sentence per tool call: what is being done, never the code or the command.
export function describe(tool: string, input: unknown): string {
  const i = (input ?? {}) as Record<string, unknown>
  switch (tool) {
    case 'Bash':
    case 'PowerShell':
      return String(i.description || 'Running a command')
    case 'Edit':
    case 'MultiEdit':
      return `Editing ${base(i.file_path)}`
    case 'Write':
      return `Writing ${base(i.file_path)}`
    case 'NotebookEdit':
      return `Editing ${base(i.notebook_path)}`
    case 'Read':
      return `Reading ${base(i.file_path)}`
    case 'Grep':
    case 'Glob':
      return 'Searching files'
    case 'WebSearch':
      return `Searching the web: ${String(i.query ?? '')}`
    case 'WebFetch':
      return `Reading ${String(i.url ?? 'a web page').replace(/^https?:\/\//, '').split('/')[0]}`
    case 'Agent':
      return `Delegated to ${String(i.subagent_type || 'an agent')}: ${String(i.description ?? '')}`
    case 'Skill':
      return `Using skill ${String(i.skill ?? '')}`
    case 'AskUserQuestion':
      return 'Asking you a question'
    case 'Artifact':
      return 'Publishing a page'
    case 'ToolSearch':
      return 'Loading tools'
    case 'Workflow':
      return 'Running a workflow'
    default:
      return tool.startsWith('mcp__') ? tool.split('__').pop() ?? tool : tool
  }
}

// Display state only: a failed write must never hold up a prompt or a tool call.
const quietly = (p: Promise<unknown>) => p.catch(() => undefined)

const mark = (s: StepState) => (s === 'running' ? '›' : s === 'done' ? '✓' : '✗')

function setStep(list: Thread[], threadId: string, step: Step): Thread[] {
  const found = list.find(t => t.id === threadId)
  const steps = (found?.steps ?? []).filter(s => s.id !== step.id)
  const next: Thread = { id: threadId, steps: [...steps, step].slice(-50) }
  return found ? list.map(t => (t.id === threadId ? next : t)) : [...list, next]
}

function agentState(info: AgentInfo | undefined): string {
  if (!info) return 'finished'
  const s = info.status
  if (s === 'running' || s === 'pending' || s === 'waiting') return 'working'
  if (s === 'completed') return 'done'
  if (s === 'failed' || s === 'killed') return 'failed'
  return 'idle'
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'work', description: 'Open the work view: what Claude is doing, per thread and agent' })
    await $.command.register({ name: 'work-code', description: 'Show or hide code and tool output in the transcript' })
    void $.ui.open({ id: PANE, title: 'Work' })
    return next(e)
  })

  on('command.run', { command: 'work' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Work' })
    return { text: 'Work view opened.' }
  })

  on('command.run', { command: 'work-code' }, async $ => {
    const now = await update($, showCode, v => !v)
    return { text: now ? 'Code and tool output shown.' : 'Code and tool output hidden.' }
  })

  on('prompt.submit', async ($, e, next) => {
    await quietly(update($, mainBusy, () => true))
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (!(e as { agentId?: string }).agentId) await quietly(update($, mainBusy, () => false))
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const threadId = e.agentId ?? MAIN
    const step: Step = { id: e.tool_use_id, text: describe(e.tool, e), state: 'running' }
    await quietly(update($, threads, list => setStep(list, threadId, step)))
    const ran = await next(e)
    const failed = Boolean(ran.deny || ran.isError)
    await quietly(update($, threads, list => setStep(list, threadId, { ...step, state: failed ? 'failed' : 'done' })))
    return ran
  })

  // Transcript: a tool call is one line of what it does; its code and output are hidden.
  on('ui.render', { component: 'ToolUse' }, async ($, e, next) => {
    if (await read($, showCode)) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const p = e.props
    const state: StepState = p.isRunning ? 'running' : p.isErrored ? 'failed' : 'done'
    return (
      <Box>
        <Text dimColor={state === 'done'} color={state === 'failed' ? 'red' : undefined}>
          {mark(state)} {describe(p.tool, p.input)}
        </Text>
      </Box>
    )
  })

  on('ui.render', { component: 'ToolResult' }, async ($, e, next) => {
    if (await read($, showCode)) return next(e)
    const { Box } = $.ui.resolve(e)
    return <Box />
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const list = await read($, threads)
    const busy = await read($, mainBusy)
    const agents = await $.agent.list()
    const width = Math.max(20, (e.props.bodyColumns ?? 60) - 2)
    const cut = (s: string) => (s.length > width ? `${s.slice(0, width - 1)}…` : s)

    const ordered = [
      ...list.filter(t => t.id === MAIN),
      ...list.filter(t => t.id !== MAIN).reverse(),
    ]
    if (ordered.length === 0) return <Text dimColor>Nothing started yet.</Text>

    return (
      <Box flexDirection="column">
        {ordered.map(t => {
          const info = agents.find(a => a.id === t.id)
          const name = t.id === MAIN ? 'Main thread' : info ? `${info.type}: ${info.description}` : `Agent ${t.id.slice(0, 6)}`
          const state = t.id === MAIN ? (busy ? 'working' : 'idle') : agentState(info)
          const done = t.steps.filter(s => s.state === 'done').length
          const failed = t.steps.filter(s => s.state === 'failed').length
          const running = t.steps.filter(s => s.state === 'running')
          const recent = t.steps.filter(s => s.state !== 'running').slice(-4)
          return (
            <Box flexDirection="column" marginBottom={1}>
              <Text bold>{cut(`${name} — ${state}`)}</Text>
              <Text dimColor>{cut(`${done} done${failed ? `, ${failed} failed` : ''}${running.length ? `, ${running.length} running` : ''}`)}</Text>
              {recent.map(s => (
                <Text dimColor={s.state === 'done'} color={s.state === 'failed' ? 'red' : undefined}>
                  {cut(`${mark(s.state)} ${s.text}`)}
                </Text>
              ))}
              {running.map(s => (
                <Text color="cyan">{cut(`${mark(s.state)} ${s.text}`)}</Text>
              ))}
            </Box>
          )
        })}
      </Box>
    )
  })
}
