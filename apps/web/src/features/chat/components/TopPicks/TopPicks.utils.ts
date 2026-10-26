import type { Ranking, UiMessage } from '@/features/chat/types/chat.types'
import { RECOMMENDATION_SORTS } from './TopPicks.constants'

// Only rankings by the KPI are investment picks; rankings by another metric stay in the chat.
export function findLatestPicks(messages: UiMessage[]): Ranking | null {
  const rankings = messages
    .flatMap((message) => message.answer?.tool_calls ?? [])
    .filter((call) => call.name === 'rank_airports')
    .map((call) => JSON.parse(call.output) as Ranking)
  const picks = rankings.filter(
    (ranking) => RECOMMENDATION_SORTS.includes(ranking.sorted_by) && ranking.ranking.length > 0,
  )
  return picks.at(-1) ?? null
}
