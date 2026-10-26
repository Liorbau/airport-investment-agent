import type { ReactNode } from 'react'
import { ChatContext } from '@/features/chat/context/chat.context'
import { useChat } from '@/features/chat/hooks/useChat'

export function ChatProvider({ children }: { children: ReactNode }) {
  return <ChatContext.Provider value={useChat()}>{children}</ChatContext.Provider>
}
