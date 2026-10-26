import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { UiMessage } from '@/features/chat/types/chat.types'
import { AnswerSources } from './components/AnswerSources/AnswerSources'
import { ASSISTANT_STYLE, ERROR_STYLE, NOTICE_STYLE, USER_STYLE } from './Message.styles'
import { withThousandsSeparators } from './Message.utils'

export function Message({ message }: { message: UiMessage }) {
  if (message.role === 'user') {
    return <p className={USER_STYLE}>{message.content}</p>
  }
  if (message.role === 'notice') {
    return <p className={NOTICE_STYLE}>{message.content}</p>
  }
  if (!message.answer) {
    return <p className={ERROR_STYLE}>{message.content}</p>
  }
  return (
    <div className={ASSISTANT_STYLE}>
      <Markdown remarkPlugins={[remarkGfm]}>{withThousandsSeparators(message.content)}</Markdown>
      <AnswerSources answer={message.answer} />
    </div>
  )
}
