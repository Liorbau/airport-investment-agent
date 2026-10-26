import {
  HEADER_STYLE,
  ICON_STYLE,
  LAYOUT_STYLE,
  SCREEN_STYLE,
  TAGLINE_STYLE,
  TITLE_STYLE,
} from '@/App.styles'
import { ChatProvider } from '@/features/chat/context/ChatProvider'
import { ChatPanel } from '@/features/chat/components/ChatPanel/ChatPanel'
import { TopPicks } from '@/features/chat/components/TopPicks/TopPicks'

export function App() {
  return (
    <ChatProvider>
      <main className={SCREEN_STYLE}>
        <header className={HEADER_STYLE}>
          <svg className={ICON_STYLE} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" />
          </svg>
          <div>
            <h1 className={TITLE_STYLE}>Airport Investment Agent</h1>
            <p className={TAGLINE_STYLE}>Identify airports where renovations will be most profitable </p>
          </div>
        </header>
        <div className={LAYOUT_STYLE}>
          <ChatPanel />
          <TopPicks />
        </div>
      </main>
    </ChatProvider>
  )
}
