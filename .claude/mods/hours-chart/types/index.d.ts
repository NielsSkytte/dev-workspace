export type Period = { from: string; to: string }

declare module 'claude-code' {
  interface PluginState {
    'hours-chart': { period: Period }
  }
}
