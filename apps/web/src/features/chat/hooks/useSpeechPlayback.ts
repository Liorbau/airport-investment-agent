import { useRef, useState } from 'react'
import { fetchSpeech } from '@/features/chat/apiActions/speech'
import { PREFERRED_VOICES } from '@/features/chat/constants/speech.constants'
import { speechChunks } from '@/features/chat/utils/speech.utils'

export function useSpeechPlayback() {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const speechIdRef = useRef(0)

  function speakWithBrowser(text: string): boolean {
    const utterance = new SpeechSynthesisUtterance(text)
    const voices = window.speechSynthesis.getVoices()
    const preferred = PREFERRED_VOICES.map((name) => voices.find((voice) => voice.name.startsWith(name)))
    utterance.voice = preferred.find(Boolean) ?? null
    utterance.onend = () => setIsSpeaking(false)
    window.speechSynthesis.speak(utterance)
    return true
  }

  async function play(audio: Blob): Promise<boolean> {
    const player = new Audio(URL.createObjectURL(audio))
    audioRef.current = player
    const finished = new Promise((resolve) => {
      player.onended = resolve
      player.onpause = resolve
    })
    await player.play()
    await finished
    URL.revokeObjectURL(player.src)
    return true
  }

  async function speak(text: string): Promise<boolean> {
    stopSpeaking()
    const speechId = speechIdRef.current
    setIsSpeaking(true)
    const chunks = speechChunks(text)
    let next = fetchSpeech(chunks[0])
    for (let index = 0; index < chunks.length; index += 1) {
      const audio = await next
      if (speechId !== speechIdRef.current) {
        return false
      }
      if (!audio) {
        return speakWithBrowser(chunks.slice(index).join(' '))
      }
      next = index + 1 < chunks.length ? fetchSpeech(chunks[index + 1]) : Promise.resolve(null)
      await play(audio).catch(() => speakWithBrowser(chunks.slice(index).join(' ')))
      if (speechId !== speechIdRef.current) {
        return false
      }
    }
    setIsSpeaking(false)
    return true
  }

  function stopSpeaking(): boolean {
    speechIdRef.current += 1
    audioRef.current?.pause()
    window.speechSynthesis.cancel()
    setIsSpeaking(false)
    return true
  }

  return { isSpeaking, speak, stopSpeaking }
}
