import { PANEL_STYLE } from './ChatPanel.styles'
import { Composer } from './components/Composer/Composer'
import { MessageList } from './components/MessageList/MessageList'
import { ProgressSteps } from './components/ProgressSteps/ProgressSteps'

export function ChatPanel() {
  return (
    <section className={PANEL_STYLE}>
      <MessageList />
      <ProgressSteps />
      <Composer />
    </section>
  )
}
