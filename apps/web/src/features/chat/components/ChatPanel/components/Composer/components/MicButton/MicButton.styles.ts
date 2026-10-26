const BUTTON_STYLE = 'flex h-9 w-9 shrink-0 items-center justify-center rounded-full border transition-colors'

export const ICON_STYLE = 'h-4 w-4'

export function micButtonStyle(isListening: boolean): string {
  return isListening
    ? `${BUTTON_STYLE} animate-pulse border-[#171719] bg-[#171719] text-white`
    : `${BUTTON_STYLE} border-[#e5e5e5] bg-white text-[#171719] hover:border-[#171719]`
}
