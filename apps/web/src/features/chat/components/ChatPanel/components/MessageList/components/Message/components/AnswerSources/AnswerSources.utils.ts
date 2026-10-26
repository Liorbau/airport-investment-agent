import type { ToolCall } from '@/features/chat/types/chat.types'
import { TOOL_TITLES } from './AnswerSources.constants'

type Sourced = { sources?: Record<string, string>; period?: string | null }
type ToolOutput = Sourced & { statistics?: Sourced & { profiles?: { traffic: { period: string } }[] } }

export function sourceSummary(call: ToolCall): string {
  const args = JSON.parse(call.arguments || '{}') as { codes?: string[]; states?: string[] }
  const output = JSON.parse(call.output) as ToolOutput
  const sourced = output.statistics ?? output
  return [
    TOOL_TITLES[call.name] ?? call.name,
    args.codes?.join(', ') ?? args.states?.join(', ') ?? 'whole US',
    Object.values(sourced.sources ?? {}).join(', '),
    output.period ?? output.statistics?.profiles?.[0]?.traffic.period,
  ]
    .filter(Boolean)
    .join(' · ')
}
