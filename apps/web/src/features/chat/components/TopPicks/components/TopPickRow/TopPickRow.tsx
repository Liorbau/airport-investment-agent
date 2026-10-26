import type { RankingRow } from '@/features/chat/types/chat.types'
import { useCountUp } from './hooks/useCountUp'
import {
  BAR_STYLE,
  CODE_STYLE,
  NAME_STYLE,
  NUMBER_STYLE,
  RANK_STYLE,
  ROW_STYLE,
  TRACK_STYLE,
} from './TopPickRow.styles'

type TopPickRowProps = { row: RankingRow; best: number }

export function TopPickRow({ row, best }: TopPickRowProps) {
  const value = useCountUp(row.kpi.score)
  return (
    <div className={ROW_STYLE}>
      <p className={CODE_STYLE}>
        <span className={RANK_STYLE}>{row.rank}</span>
        {row.airport}
      </p>
      <p className={NAME_STYLE}>{row.name}</p>
      <div className={TRACK_STYLE}>
        <div className={BAR_STYLE} style={{ width: `${best ? (100 * value) / best : 0}%` }} />
      </div>
      <p className={NUMBER_STYLE}>
        {value.toLocaleString()} = +{row.kpi.passenger_increase.toLocaleString()} × {row.kpi.crowding}
      </p>
    </div>
  )
}
