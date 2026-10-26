import { ICON_STYLE, micButtonStyle } from './MicButton.styles'

type MicButtonProps = { isListening: boolean; onClick: () => void }

export function MicButton({ isListening, onClick }: MicButtonProps) {
  return (
    <button
      type="button"
      className={micButtonStyle(isListening)}
      onClick={onClick}
      aria-label={isListening ? 'Stop listening' : 'Ask by voice'}
      title={isListening ? 'Stop listening' : 'Ask by voice'}
    >
      <svg className={ICON_STYLE} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z" />
      </svg>
    </button>
  )
}
