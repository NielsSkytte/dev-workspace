import { expect, test } from 'claude-code/testing'

const BASH = {
  tool_use_id: 't1',
  tool: 'Bash',
  input: { command: 'rm -rf /tmp/secret && echo done', description: 'Delete temp files' },
  isRunning: false,
  isErrored: false,
  isInterrupted: false,
  output: { stdout: 'done', stderr: '', interrupted: false },
}

for (const surface of ['terminal', 'desktop'] as const) {
  test(`a tool call shows what it does, not its code (${surface})`, async $ => {
    const ui = await $.ui.mount({ plugin: 'work-view', surface, component: 'ToolUse', props: BASH })
    expect(await ui.find({ type: 'Text', text: /Delete temp files/ })).toBeTruthy()
    expect(await ui.findAll({ type: 'Text', text: /rm -rf/ })).toHaveLength(0)
  })

  test(`an edit shows the file name only (${surface})`, async $ => {
    const ui = await $.ui.mount({
      plugin: 'work-view', surface, component: 'ToolUse',
      props: { ...BASH, tool: 'Edit', input: { file_path: 'C:/src/app.py', old_string: 'a = 1', new_string: 'a = 2' } },
    })
    expect(await ui.find({ type: 'Text', text: /Editing app\.py/ })).toBeTruthy()
    expect(await ui.findAll({ type: 'Text', text: /a = 2/ })).toHaveLength(0)
  })
}
