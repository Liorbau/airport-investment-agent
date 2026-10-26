import { useChatContext } from '@/features/chat/context/chat.context'
import { FIRST_STEP } from './ProgressSteps.constants'
import { DOTS_STYLE, STATUS_STYLE, TIMER_STYLE } from './ProgressSteps.styles'
import { useElapsedSeconds } from './hooks/useElapsedSeconds'

export function ProgressSteps() {
  const { isBusy, progress, startedAt } = useChatContext()
  const seconds = useElapsedSeconds(startedAt)
  if (!isBusy) {
    return null
  }
  return (
    <p className={STATUS_STYLE}>
      <span className={DOTS_STYLE}>•••</span>
      <span>{progress.at(-1) ?? FIRST_STEP}</span>
      <span className={TIMER_STYLE}>· {seconds}s</span>
    </p>
  )
}
