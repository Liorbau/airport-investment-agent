import { useEffect, useState } from 'react'

export function useElapsedSeconds(startedAt: number): number {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [startedAt])
  return Math.max(0, Math.floor((now - startedAt) / 1000))
}
