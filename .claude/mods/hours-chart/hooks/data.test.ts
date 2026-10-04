import { expect, test } from 'claude-code/testing'

import { dates, day, period, segments, table } from './data'

const TS = `| Project | Proj ID | Activity | Task | Hours | Billable |
|---|---|---|---|---|---|
| customers/Aeven/AtomicServiceNow | 4058 | 400760 | none | 2.50 | yes |
| Dev | INTERNAL-RND | - | - | 0.50 | no |
`
const VAL = `| Project | Proj ID | Activity | Task | Keyboard h | Weighted h | Billable |
|---|---|---|---|---|---|---|
| customers/Aeven/AtomicServiceNow | 4058 | 400760 | none | 0.32 | 3.25 | yes |
| Dev | INTERNAL-RND | - | - | 0.05 | 0.50 | no |

| Tier | Turns | Keyboard min | Multiplier | Weighted h |
|---|---|---|---|---|
| T1 | 18 | 3 | 2.0x | 0.10 |
`

test('joins timesheet and value record per project', () => {
  const d = day('2026-10-03', TS, VAL)
  const aeven = d.lines.find(l => l.project.includes('Aeven'))!
  expect(aeven).toEqual({ project: 'customers/Aeven/AtomicServiceNow', keyboard: 0.32, measured: 2.5, weighted: 3.25 })
  expect(table(VAL, ['Project', 'Keyboard h']).length).toBe(2)
})

test('bar segments: keyboard, measured beyond, weighted add-on, below', () => {
  expect(segments({ project: 'x', keyboard: 0.5, measured: 2, weighted: 3 }, 10))
    .toEqual({ keyboard: 5, measured: 15, addon: 10, below: 0 })
  expect(segments({ project: 'x', keyboard: 0.5, measured: 4, weighted: 3 }, 10).below).toBe(1)
})

test('periods and date ranges', () => {
  expect(period('', '2026-10-04')).toEqual({ from: '2026-09-28', to: '2026-10-04' })
  expect(period('week', '2026-10-04')).toEqual({ from: '2026-09-28', to: '2026-10-04' })
  expect(period('month', '2026-10-04')).toEqual({ from: '2026-10-01', to: '2026-10-04' })
  expect(period('2026-10-02', '2026-10-04')).toEqual({ from: '2026-10-02', to: '2026-10-02' })
  expect(dates('2026-09-30', '2026-10-02')).toEqual(['2026-09-30', '2026-10-01', '2026-10-02'])
})
