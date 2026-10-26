export type ChatMessage = { role: 'user' | 'assistant'; content: string }

export type ToolCall = { name: string; arguments: string; output: string }

export type NumberCheck = { numbers_checked: number; unverified_numbers: string[] }

export type AnswerEvent = {
  type: 'answer'
  text: string
  tool_calls: ToolCall[]
  steps: number
  number_check: NumberCheck
}

export type ChatEvent =
  | { type: 'progress'; message: string }
  | AnswerEvent
  | { type: 'error'; message: string }

export type UiMessage = {
  id: number
  role: 'user' | 'assistant' | 'error' | 'notice'
  content: string
  answer?: AnswerEvent
}

export type RankingRow = {
  rank: number
  airport: string
  name: string | null
  kpi: { passenger_increase: number; crowding: number | null; score: number }
}

export type Ranking = { scope: string; sorted_by: string; ranking: RankingRow[] }

export type AirportPoint = { iata: string; lat: number; lon: number }
