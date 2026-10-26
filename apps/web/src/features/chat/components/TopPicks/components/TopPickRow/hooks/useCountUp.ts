import { useEffect, useState } from 'react'

const DURATION_MS = 900

// Counts from 0 to `target`, easing out, whenever `target` changes.
export function useCountUp(target: number): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    const start = performance.now()
    let frame = 0
    const tick = (now: number) => {
      const progress = Math.min((now - start) / DURATION_MS, 1)
      setValue(Math.round(target * (1 - (1 - progress) ** 3)))
      if (progress < 1) {
        frame = requestAnimationFrame(tick)
      }
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [target])
  return value
}
