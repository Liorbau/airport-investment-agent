import { readSseStream } from '@/api/sse'
import type { ChatEvent, ChatMessage } from '@/features/chat/types/chat.types'

export async function postChat(
  question: string,
  history: ChatMessage[],
  signal: AbortSignal,
  onEvent: (event: ChatEvent) => void,
): Promise<number> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    signal,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
  })
  if (!response.ok) {
    throw new Error(`The server rejected the question (HTTP ${response.status}).`)
  }
  return readSseStream<ChatEvent>(response, onEvent)
}
