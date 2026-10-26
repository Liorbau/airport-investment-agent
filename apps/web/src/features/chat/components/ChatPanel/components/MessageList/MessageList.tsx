import { useChatContext } from '@/features/chat/context/chat.context'
import { Message } from './components/Message/Message'
import { SampleQuestions } from './components/SampleQuestions/SampleQuestions'
import { useScrollToBottom } from './hooks/useScrollToBottom'
import { LIST_STYLE } from './MessageList.styles'

export function MessageList() {
  const { messages, progress, isBusy } = useChatContext()
  const listRef = useScrollToBottom<HTMLDivElement>(`${messages.length}-${progress.length}-${isBusy}`)
  return (
    <div ref={listRef} className={LIST_STYLE}>
      {messages.length === 0 ? (
        <SampleQuestions />
      ) : (
        messages.map((message) => <Message key={message.id} message={message} />)
      )}
    </div>
  )
}
