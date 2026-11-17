declare const h: any
import { test, expect, mock } from 'claude-code/testing'

const message = {
  plugin: 'quiet-transcript',
  surface: 'terminal',
  component: 'AssistantMessage',
  props: { text: 'a\n```py\nx=1\ny=2\n```\nb', isFirstOfReply: true },
}

function engine(on: any, termProgram: string | undefined) {
  on('ui.render', (h$: any, e: any) => {
    const { Text } = h$.ui.resolve(e)
    return h(Text, null, e.props.text)
  })
  mock.env(on, termProgram ? { TERM_PROGRAM: termProgram } : {})
}

test('assistant code blocks fold to a marker', async ($: any, on: any) => {
  engine(on, 'WindowsTerminal')
  const out = await $.ui.render(message)
  expect(JSON.stringify(out)).toContain('code hidden (2 lines)')
})

test('in Orca the code is shown in full: Orca catches link clicks, so a fold could never open', async ($: any, on: any) => {
  engine(on, 'Orca')
  const out = JSON.stringify(await $.ui.render(message))
  expect(out).toContain('x=1')
  expect(out).not.toContain('code hidden')
  expect(out).not.toContain('show code')
})
