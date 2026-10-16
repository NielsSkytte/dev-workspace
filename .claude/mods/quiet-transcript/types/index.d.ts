export type Job = { id: string; loop: string; label: string; key: string; startedAt: number; est: number }
export type Last = { tool: string; cmd: string; startedAt: number; endedAt: number; state: 'running' | 'done' | 'failed' }
export type Status ='pending' | 'in_progress' | 'completed'
export type Ask = { kind: 'approve' | 'answer' | 'do'; text: string }
export type Board = { next: string; you: Ask[]; claude: string[]; at: number; turn: number }
export type Step = { title: string; status: Status; children?: { title: string; status: Status }[] }

declare module 'claude-code' {
  interface PluginState {
    'quiet-transcript': {
      jobs: Job[]
      plans: Record<string, Step[]>
      carried: Record<string, { done: number; total: number }>
      names: Record<string, string>
      last: Last | null
      tick: number
      done: number
      board: Record<string, Board>
      turn: number
    }
  }
}
