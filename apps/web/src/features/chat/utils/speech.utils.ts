import { MAX_CHUNK_CHARS } from '@/features/chat/constants/speech.constants'

export function toSpeech(markdown: string): string {
  return markdown
    .split('\n')
    .filter((line) => !line.trim().startsWith('|'))
    .map((line) => line.replace(/^\s*[-*]\s+/, '').replace(/[#*_`>]/g, ''))
    .join('\n')
    .trim()
}

export function speechChunks(text: string): string[] {
  const sentences = text.split(/(?<=[.!?])\s+|\n+/).map((part) => part.trim()).filter(Boolean)
  const chunks: string[] = []
  for (const sentence of sentences) {
    const last = chunks.at(-1)
    if (chunks.length > 1 && last && last.length + sentence.length < MAX_CHUNK_CHARS) {
      chunks[chunks.length - 1] = `${last} ${sentence}`
    } else {
      chunks.push(sentence)
    }
  }
  return chunks
}
