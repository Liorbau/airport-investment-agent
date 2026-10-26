import { createContext, useContext } from 'react'
import type { useChat } from '@/features/chat/hooks/useChat'

export type ChatValue = ReturnType<typeof useChat>

export const ChatContext = createContext<ChatValue | null>(null)

export function useChatContext(): ChatValue {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider')
  }
  return context
}
