import { useChatContext } from '@/features/chat/context/chat.context'
import { PicksMap } from './components/PicksMap/PicksMap'
import { TopPickRow } from './components/TopPickRow/TopPickRow'
import { TOP_PICKS_COUNT } from './TopPicks.constants'
import { CARD_STYLE, EMPTY_STYLE, TITLE_STYLE } from './TopPicks.styles'
import { findLatestPicks } from './TopPicks.utils'

export function TopPicks() {
  const picks = findLatestPicks(useChatContext().messages)
  const rows = picks?.ranking.slice(0, TOP_PICKS_COUNT) ?? []
  return (
    <aside className={CARD_STYLE}>
      <h2 className={TITLE_STYLE}>Top picks{picks && ` · ${picks.scope}`}</h2>
      <PicksMap codes={rows.map((row) => row.airport)} />
      {rows.map((row) => (
        <TopPickRow key={`${picks?.scope}-${row.airport}`} row={row} best={rows[0].kpi.score} />
      ))}
      {!picks && <p className={EMPTY_STYLE}>Ask where to invest and the best candidates appear here.</p>}
    </aside>
  )
}
