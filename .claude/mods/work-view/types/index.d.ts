export type StepState = 'running' | 'done' | 'failed'
export type Step = { id: string; text: string; state: StepState }
export type Thread = { id: string; steps: Step[] }

declare module 'claude-code' {
  interface PluginState {
    'work-view': { threads: Thread[]; showCode: boolean; mainBusy: boolean }
  }
}
