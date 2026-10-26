import { MAP_BOUNDS, MAP_SIZE } from './PicksMap.constants'

export function toMapPoint(lat: number, lon: number): { x: number; y: number } | null {
  const { west, east, north, south } = MAP_BOUNDS
  if (lon < west || lon > east || lat < south || lat > north) {
    return null
  }
  return {
    x: ((lon - west) / (east - west)) * MAP_SIZE.width,
    y: ((north - lat) / (north - south)) * MAP_SIZE.height,
  }
}
