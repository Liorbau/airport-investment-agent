import { useRef, useState } from 'react'
import { SILENCE_MS } from '@/features/chat/constants/speech.constants'
import type { Recognition, RecognitionConstructor } from '@/features/chat/types/speech.types'

const speechWindow = window as unknown as {
  SpeechRecognition?: RecognitionConstructor
  webkitSpeechRecognition?: RecognitionConstructor
}
const RecognitionClass = speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition

export function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<Recognition | null>(null)

  function listen(onText: (text: string) => void, onDone: (text: string) => void): boolean {
    if (!RecognitionClass) {
      return false
    }
    const recognition = new RecognitionClass()
    recognition.lang = 'en-US'
    recognition.continuous = true
    recognition.interimResults = true
    let transcript = ''
    let silenceTimer = 0
    recognition.onresult = (event) => {
      transcript = Array.from(event.results, (result) => result[0].transcript).join('')
      onText(transcript)
      window.clearTimeout(silenceTimer)
      silenceTimer = window.setTimeout(() => recognition.stop(), SILENCE_MS)
    }
    recognition.onend = () => {
      window.clearTimeout(silenceTimer)
      setIsListening(false)
      onDone(transcript)
    }
    recognitionRef.current = recognition
    recognition.start()
    setIsListening(true)
    return true
  }

  function stopListening(): boolean {
    recognitionRef.current?.stop()
    return isListening
  }

  return { canListen: Boolean(RecognitionClass), isListening, listen, stopListening }
}
