import type { AnswerEvent } from '@/features/chat/types/chat.types'
import { FOOTER_STYLE, OK_STYLE, SOURCE_STYLE, WARNING_STYLE } from './AnswerSources.styles'
import { sourceSummary } from './AnswerSources.utils'

export function AnswerSources({ answer }: { answer: AnswerEvent }) {
  const { numbers_checked: checked, unverified_numbers: unverified } = answer.number_check
  const sources = [...new Set(answer.tool_calls.map(sourceSummary))]
  return (
    <div className={FOOTER_STYLE}>
      {sources.map((source) => (
        <p key={source} className={SOURCE_STYLE}>
          Source: {source}
        </p>
      ))}
      {unverified.length > 0 ? (
        <p className={WARNING_STYLE}>⚠ Not found in the data: {unverified.join(', ')}</p>
      ) : (
        checked > 0 && <p className={OK_STYLE}>✓ All {checked} numbers match the data</p>
      )}
    </div>
  )
}
