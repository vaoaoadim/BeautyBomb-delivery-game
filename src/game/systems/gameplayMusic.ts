import type { RunPhase } from "../domain/runState";

/** Music is a presentation layer, but its permitted state is deterministic. */
export const canPlayGameplayMusic = (
  phase: RunPhase,
  isPaused: boolean,
  isMuted: boolean,
): boolean => phase === "playing" && !isPaused && !isMuted;
