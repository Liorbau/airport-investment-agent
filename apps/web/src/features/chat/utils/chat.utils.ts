import { HISTORY_LIMIT } from '@/features/chat/constants/chat.constants'
import type { ChatMessage, UiMessage } from '@/features/chat/types/chat.types'

export function toHistory(messages: UiMessage[]): ChatMessage[] {
  return messages
    .filter((message) => message.role === 'user' || message.role === 'assistant')
    .map((message) => ({ role: message.role as ChatMessage['role'], content: message.content }))
    .slice(-HISTORY_LIMIT)
}

export function isAbort(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}
