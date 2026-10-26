import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { useChatContext } from '@/features/chat/context/chat.context'
import { MicButton } from './components/MicButton/MicButton'
import { BUTTON_STYLE, FORM_STYLE, INPUT_STYLE, STOP_STYLE } from './Composer.styles'

export function Composer() {
  const { isBusy, send, stop, voice } = useChatContext()
  const [question, setQuestion] = useState('')

  async function submit(): Promise<boolean> {
    const text = question
    setQuestion('')
    return send(text)
  }

  function onSubmit(event: FormEvent): Promise<boolean> {
    event.preventDefault()
    return submit()
  }

  function toggleListening(): boolean {
    if (voice.isListening) {
      return voice.stopListening()
    }
    return voice.listen(setQuestion, (text) => {
      setQuestion('')
      void send(text, true)
    })
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>): boolean {
    if (event.key !== 'Enter' || event.shiftKey) {
      return false
    }
    event.preventDefault()
    void submit()
    return true
  }

  return (
    <form className={FORM_STYLE} onSubmit={onSubmit}>
      <textarea
        className={INPUT_STYLE}
        rows={Math.min(question.split('\n').length, 5)}
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Ask about US airports…"
      />
      {voice.canListen && !isBusy && (
        <MicButton isListening={voice.isListening} onClick={toggleListening} />
      )}
      {isBusy || voice.isSpeaking ? (
        <button type="button" className={STOP_STYLE} onClick={stop}>
          Stop
        </button>
      ) : (
        <button className={BUTTON_STYLE} disabled={question.trim() === ''}>
          Send
        </button>
      )}
    </form>
  )
}
