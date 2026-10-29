import { expect, mock, test } from 'claude-code/testing'

const TASK = `---
title: Carl Ras - operation_hardening
status: in-progress
project: customers/Carl-Ras/datahub
activity:             # none
fno_task: CarlRData-555
---

## What
`

const BAND = { plugin: 'fno-task', surface: 'terminal', component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false } } as const

test('the band shows the held task id, title and project', async ($, on) => {
  mock.clock(on)
  on('session.start', () => ({ cwd: '/work' }))
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['drawn by Claude Code'] }))
  on('session.id', () => ({ value: 'S1' }))
  on('fs.exists', ($, e) => ({ value: e.path.split('\\').join('/').endsWith('in-progress/t1.md') }))
  on('fs.read', ($, e) => ({ value: e.path.endsWith('active-task') ? JSON.stringify({ sessions: { S1: { slug: 't1' } } }) : TASK }))
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  const ui = await $.ui.mount(BAND)
  expect(await ui.find({ type: 'Text', text: /CarlRData-555.*operation_hardening.*datahub/ })).toBeDefined()
})

test('the band says so when no task is held', async ($, on) => {
  mock.clock(on)
  on('session.start', () => ({ cwd: '/work' }))
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['drawn by Claude Code'] }))
  on('session.id', () => ({ value: 'S2' }))
  on('fs.read', () => ({ value: JSON.stringify({ sessions: {} }) }))
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  const ui = await $.ui.mount(BAND)
  expect(await ui.find({ type: 'Text', text: /no task held/ })).toBeDefined()
})
