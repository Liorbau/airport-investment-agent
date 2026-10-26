import { useAirports } from './hooks/useAirports'
import { MAP_SIZE } from './PicksMap.constants'
import { DOT_STYLE, LABEL_STYLE, MAP_STYLE, PICK_STYLE, PULSE_STYLE } from './PicksMap.styles'
import { toMapPoint } from './PicksMap.utils'

type PicksMapProps = { codes: string[] }

export function PicksMap({ codes }: PicksMapProps) {
  const airports = useAirports()
  const points = airports.flatMap((airport) => {
    const point = toMapPoint(airport.lat, airport.lon)
    return point ? [{ code: airport.iata, ...point }] : []
  })
  const picks = codes.flatMap((code, index) => {
    const point = points.find((candidate) => candidate.code === code)
    return point ? [{ ...point, rank: index + 1 }] : []
  })
  return (
    <svg className={MAP_STYLE} viewBox={`-3 -3 ${MAP_SIZE.width + 9} ${MAP_SIZE.height + 6}`} aria-hidden="true">
      {points.map((point) => (
        <circle key={point.code} cx={point.x} cy={point.y} r={0.9} className={DOT_STYLE} />
      ))}
      {picks.map((pick) => (
        <g key={pick.code}>
          <circle cx={pick.x} cy={pick.y} r={2.4} className={PULSE_STYLE} />
          <circle cx={pick.x} cy={pick.y} r={1.6} className={PICK_STYLE} />
          <text x={pick.x + 3} y={pick.y + 1.7} className={LABEL_STYLE}>
            {pick.rank}
          </text>
        </g>
      ))}
    </svg>
  )
}
