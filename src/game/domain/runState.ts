import { GAMEPLAY_RULES, LANE_CENTERS } from "../config";

export type LaneIndex = 0 | 1 | 2;
export type LaneDirection = -1 | 1;
export type RunPhase = "ready" | "playing" | "defeated" | "delivered";

export interface RunState {
  readonly phase: RunPhase;
  readonly lane: LaneIndex;
  readonly lives: number;
  readonly elapsedMs: number;
  readonly durationMs: number;
  readonly invulnerabilityRemainingMs: number;
}

const STARTING_LANE: LaneIndex = 1;

export function createRunState(
  durationMs: number = GAMEPLAY_RULES.greyboxRunDurationMs,
): RunState {
  if (!Number.isFinite(durationMs) || durationMs <= 0) {
    throw new Error("Run duration must be a positive finite number.");
  }

  return {
    phase: "ready",
    lane: STARTING_LANE,
    lives: GAMEPLAY_RULES.startingLives,
    elapsedMs: 0,
    durationMs,
    invulnerabilityRemainingMs: 0,
  };
}

export function startRun(state: RunState): RunState {
  if (state.phase !== "ready") {
    return state;
  }

  return {
    ...state,
    phase: "playing",
  };
}

export function retryRun(state: RunState): RunState {
  return startRun(createRunState(state.durationMs));
}

export function moveLane(
  state: RunState,
  direction: LaneDirection,
): RunState {
  if (state.phase !== "playing") {
    return state;
  }

  const nextLane = Math.max(
    0,
    Math.min(LANE_CENTERS.length - 1, state.lane + direction),
  ) as LaneIndex;

  if (nextLane === state.lane) {
    return state;
  }

  return {
    ...state,
    lane: nextLane,
  };
}

export function advanceRun(state: RunState, deltaMs: number): RunState {
  if (state.phase !== "playing" || deltaMs <= 0) {
    return state;
  }

  const elapsedMs = Math.min(state.durationMs, state.elapsedMs + deltaMs);
  const phase: RunPhase =
    elapsedMs >= state.durationMs ? "delivered" : "playing";

  return {
    ...state,
    phase,
    elapsedMs,
    invulnerabilityRemainingMs: Math.max(
      0,
      state.invulnerabilityRemainingMs - deltaMs,
    ),
  };
}

export function registerHit(state: RunState): RunState {
  if (
    state.phase !== "playing" ||
    state.invulnerabilityRemainingMs > 0
  ) {
    return state;
  }

  const lives = Math.max(0, state.lives - 1);

  return {
    ...state,
    lives,
    phase: lives === 0 ? "defeated" : "playing",
    invulnerabilityRemainingMs:
      lives === 0 ? 0 : GAMEPLAY_RULES.invulnerabilityMs,
  };
}

export function getRunProgress(state: RunState): number {
  return Math.min(1, Math.max(0, state.elapsedMs / state.durationMs));
}
