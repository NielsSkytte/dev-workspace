import { expect, test } from 'claude-code/testing'

import { argv, byDate, segments } from './data'
import type { Line } from './data'

const line = (o: Partial<Line>): Line => ({
  date: '2026-10-01', project: 'customers/Carl-Ras/datahub', activity: '', task: 'CarlRData-557',
  keyboard: 0, measured: 0, claimed: 0, weighted: 0, shared: false, billable: true, live: false, ...o,
})

test('bar segments: keyboard, registered beyond, weighted add-on, below', () => {
  expect(segments(line({ keyboard: 0.5, claimed: 2, weighted: 3 }), 10))
    .toEqual({ keyboard: 5, registered: 15, addon: 10, below: 0 })
  expect(segments(line({ keyboard: 0.5, claimed: 4, weighted: 3 }), 10).below).toBe(1)
})

test('lines group by date, oldest first', () => {
  const g = byDate([line({ date: '2026-10-02' }), line({ date: '2026-10-01' }), line({ date: '2026-10-02' })])
  expect(g.map(([d, ls]) => [d, ls.length])).toEqual([['2026-10-01', 1], ['2026-10-02', 2]])
})

test('args pass through to hours.py', () => {
  expect(argv('  2026-09-28   2026-10-04 ')).toEqual(['2026-09-28', '2026-10-04'])
  expect(argv('')).toEqual([])
})
