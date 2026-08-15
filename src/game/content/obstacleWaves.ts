import type { LaneIndex } from "../domain/runState";

export interface ObstacleWave {
  readonly id: number;
  readonly spawnAtMs: number;
  readonly safeLane: LaneIndex;
  readonly blockedLanes: readonly [LaneIndex, LaneIndex];
}

const ALL_LANES = [0, 1, 2] as const;
const SAFE_LANE_PATTERN = [1, 0, 2, 1, 2, 0] as const;

export function createObstacleWaves(
  durationMs: number,
  firstWaveAtMs = 1_800,
  intervalMs = 1_650,
): readonly ObstacleWave[] {
  if (durationMs <= 0 || firstWaveAtMs < 0 || intervalMs <= 0) {
    throw new Error("Obstacle schedule timing must be positive.");
  }

  const waves: ObstacleWave[] = [];
  let id = 0;

  for (
    let spawnAtMs = firstWaveAtMs;
    spawnAtMs < durationMs - 1_000;
    spawnAtMs += intervalMs
  ) {
    const safeLane = SAFE_LANE_PATTERN[id % SAFE_LANE_PATTERN.length]!;
    const blockedLanes = ALL_LANES.filter(
      (lane): lane is LaneIndex => lane !== safeLane,
    ) as [LaneIndex, LaneIndex];

    waves.push({
      id,
      spawnAtMs,
      safeLane,
      blockedLanes,
    });
    id += 1;
  }

  return waves;
}
