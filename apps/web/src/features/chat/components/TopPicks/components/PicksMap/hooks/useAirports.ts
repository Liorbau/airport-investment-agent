import { useEffect, useState } from 'react'
import { fetchAirports } from '@/features/chat/apiActions/airports'
import type { AirportPoint } from '@/features/chat/types/chat.types'

export function useAirports(): AirportPoint[] {
  const [airports, setAirports] = useState<AirportPoint[]>([])
  useEffect(() => {
    fetchAirports()
      .then(setAirports)
      .catch((error: unknown) => console.warn('The map is unavailable', error))
  }, [])
  return airports
}
