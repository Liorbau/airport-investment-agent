import type { AirportPoint } from '@/features/chat/types/chat.types'

export async function fetchAirports(): Promise<AirportPoint[]> {
  const response = await fetch('/api/airports')
  if (!response.ok) {
    throw new Error(`Airports request failed (HTTP ${response.status})`)
  }
  return response.json() as Promise<AirportPoint[]>
}
