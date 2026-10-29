import type { Register } from 'claude-code'

// The workspace's time substrate: `active-task` maps session id -> task slug (set by /task and
// /switch-task); the task file's front matter carries `fno_task` (Azure DevOps id) and `activity`.
const OPS = 'C:/Dev/ops'
const ACTIVE = `${OPS}/time/active-task`
const STATES = ['in-progress', 'open', 'done', 'cancelled']
const REFRESH_MS = 3000

type Held = { slug: string; title: string; project: string; fnoTask: string; activity: string; state: string }
type Shown = { text: string; tone: 'ok' | 'warn' | 'dim' }

let held: Held | null = null
let heldSlug: string | null = null
let missing = false
let shown: Shown | null = null
let timer: { cancel: () => void } | undefined

// `key: value  # comment` -> value. Values here are ids and titles, never contain ` #`.
function field(head: string, key: string): string {
  const m = head.match(new RegExp(`^${key}:[ \\t]*(.*)$`, 'm'))
  const v = (m?.[1] ?? '').replace(/(^|\s+)#.*$/, '').trim()
  return v.replace(/^["']|["']$/g, '')
}

const short = (s: string, n: number) => (s.length > n ? `${s.slice(0, n - 1)}…` : s)

function line(h: Held | null, isMissing: boolean): Shown {
  if (isMissing) return { text: 'F&O  task file not found for the held task', tone: 'warn' }
  if (h === null) return { text: 'F&O  no task held; time bills to the project only (/switch-task)', tone: 'warn' }
  const hasId = h.fnoTask !== '' && h.fnoTask.toLowerCase() !== 'none'
  const id = hasId ? h.fnoTask : h.fnoTask === '' ? 'no DevOps id' : 'task has no DevOps id'
  const act = h.activity !== '' ? `  ·  activity ${h.activity}` : ''
  const proj = h.project !== '' ? `  ·  ${h.project.split('/').slice(-1)[0]}` : ''
  const state = h.state !== 'in-progress' ? `  ·  ${h.state}` : ''
  return { text: `F&O  ${id}${act}  ·  ${short(h.title, 60)}${proj}${state}`, tone: hasId || h.activity !== '' ? 'ok' : 'warn' }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function refresh($: any) {
  let slug: string | null = null
  try {
    const sid = await $.session.id()
    const raw = JSON.parse(await $.fs.read(ACTIVE))
    slug = raw?.sessions?.[sid]?.slug ?? null
  } catch {
    slug = null
  }

  if (slug !== heldSlug) {
    heldSlug = slug
    held = null
    missing = false
    if (slug !== null) {
      for (const state of STATES) {
        const path = `${OPS}/tasks/${state}/${slug}.md`
        if (!(await $.fs.exists(path))) continue
        const text: string = await $.fs.read(path)
        const head = text.split(/\r?\n---/)[0]
        held = {
          slug,
          state,
          title: field(head, 'title') || slug,
          project: field(head, 'project'),
          fnoTask: field(head, 'fno_task'),
          activity: field(head, 'activity'),
        }
        break
      }
      missing = held === null
    }
  }

  const next = line(held, missing)
  if (shown === null || next.text !== shown.text || next.tone !== shown.tone) {
    shown = next
    $.ui.invalidate('ui.render')
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    timer?.cancel()
    shown = null
    heldSlug = null
    timer = $.clock.every(REFRESH_MS, () => void refresh($).catch(() => undefined))
    await refresh($).catch(() => undefined)
    return next(e)
  })

  // A task can change with a command or a prompt; look again at once instead of waiting for the timer.
  on('prompt.submit', async ($, e, next) => {
    void refresh($).catch(() => undefined)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || shown === null) return next(e)
    const { Text } = $.ui.resolve(e)
    const color = shown.tone === 'warn' ? 'warning' : shown.tone === 'dim' ? 'inactive' : 'subtle'
    return <Text color={color}>{shown.text}</Text>
  })
}
