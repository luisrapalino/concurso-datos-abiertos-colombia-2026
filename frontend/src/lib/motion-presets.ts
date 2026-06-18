/** Duración corta para AnimatePresence mode="wait" (~300ms total). */
export const PRESENCE_TRANSITION_MS = 0.15;

export const fadeSlide = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 6 },
} as const;

export function presenceTransition(reduceMotion: boolean | null) {
  return { duration: reduceMotion ? 0 : PRESENCE_TRANSITION_MS };
}
