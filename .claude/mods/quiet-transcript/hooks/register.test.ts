declare const h: any
import { test, expect } from 'claude-code/testing'

test('assistant code blocks fold to a marker', async ($: any, on: any) => {
  on('ui.render', (h$: any, e: any) => {
    const { Text } = h$.ui.resolve(e)
    return h(Text, null, e.props.text)
  })
  const out = await $.ui.render({
    plugin: 'quiet-transcript',
    surface: 'terminal',
    component: 'AssistantMessage',
    props: { text: 'a\n```py\nx=1\ny=2\n```\nb', isFirstOfReply: true },
  })
  expect(JSON.stringify(out)).toContain('code hidden (2 lines)')
})
