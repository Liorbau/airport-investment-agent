import { useEffect, useRef } from 'react'

export function useScrollToBottom<T extends HTMLElement>(trigger: unknown) {
  const containerRef = useRef<T>(null)
  useEffect(() => {
    const container = containerRef.current
    container?.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
  }, [trigger])
  return containerRef
}
