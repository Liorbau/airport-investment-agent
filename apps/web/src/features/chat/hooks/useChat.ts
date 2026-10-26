import { useRef, useState } from 'react'
import { postChat } from '@/features/chat/apiActions/chat'
import { NO_ANSWER_MESSAGE, STOPPED_MESSAGE } from '@/features/chat/constants/chat.constants'
import type { ChatEvent, UiMessage } from '@/features/chat/types/chat.types'
import { isAbort, toHistory } from '@/features/chat/utils/chat.utils'
import { toSpeech } from '@/features/chat/utils/speech.utils'
import { useSpeechPlayback } from './useSpeechPlayback'
import { useSpeechRecognition } from './useSpeechRecognition'

export function useChat() {
  const [messages, setMessages] = useState<UiMessage[]>([])
  const [progress, setProgress] = useState<string[]>([])
  const [isBusy, setIsBusy] = useState(false)
  const [startedAt, setStartedAt] = useState(0)
  const abortRef = useRef<AbortController | null>(null)
  const voice = { ...useSpeechRecognition(), ...useSpeechPlayback() }

  function addMessage(role: UiMessage['role'], content: string, answer?: UiMessage['answer']): number {
    const id = Date.now() + Math.random()
    setMessages((previous) => [...previous, { id, role, content, answer }])
    return id
  }

  function handleEvent(event: ChatEvent): string {
    if (event.type === 'progress') {
      setProgress((previous) => [...previous, event.message])
    } else if (event.type === 'answer') {
      addMessage('assistant', event.text, event)
    } else {
      addMessage('error', event.message)
    }
    return event.type
  }

  async function send(question: string, spoken = false): Promise<boolean> {
    if (isBusy || question.trim() === '') {
      return false
    }
    const history = toHistory(messages)
    const controller = new AbortController()
    abortRef.current = controller
    voice.stopSpeaking()
    addMessage('user', question)
    setIsBusy(true)
    setStartedAt(Date.now())
    setProgress([])
    let finished = false
    try {
      await postChat(question, history, controller.signal, (event) => {
        finished = finished || event.type !== 'progress'
        handleEvent(event)
        if (spoken && event.type === 'answer') {
          void voice.speak(toSpeech(event.text))
        }
      })
      if (!finished) {
        addMessage('error', NO_ANSWER_MESSAGE)
      }
    } catch (error) {
      if (isAbort(error)) {
        addMessage('notice', STOPPED_MESSAGE)
      } else {
        addMessage('error', error instanceof Error ? error.message : 'The request failed.')
      }
    } finally {
      abortRef.current = null
      setIsBusy(false)
      setProgress([])
    }
    return true
  }

  function stop(): boolean {
    voice.stopSpeaking()
    abortRef.current?.abort()
    return Boolean(abortRef.current)
  }

  return { messages, progress, isBusy, startedAt, send, stop, voice }
}
