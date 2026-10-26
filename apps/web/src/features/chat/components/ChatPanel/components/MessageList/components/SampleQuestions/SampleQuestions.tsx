import { useChatContext } from '@/features/chat/context/chat.context'
import { BUTTON_STYLE, HINT_STYLE, TITLE_STYLE, WRAPPER_STYLE } from './SampleQuestions.styles'
import { SAMPLE_QUESTIONS } from './SampleQuestions.constants'

export function SampleQuestions() {
  const { send } = useChatContext()
  return (
    <div className={WRAPPER_STYLE}>
      <p className={TITLE_STYLE}>Where should we invest in airport capacity?</p>
      <p className={HINT_STYLE}>
        Score = real passenger growth × how crowded the airport is. Every number is checked against the data.
      </p>
      {SAMPLE_QUESTIONS.map((question) => (
        <button key={question} className={BUTTON_STYLE} onClick={() => send(question)}>
          {question}
        </button>
      ))}
    </div>
  )
}
