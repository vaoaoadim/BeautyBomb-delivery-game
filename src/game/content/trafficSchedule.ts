import type { LaneIndex } from "../domain/runState";

export type TrafficPattern =
  | "single"
  | "parallel-pair"
  | "staggered-pair"
  | "convoy"
  | "scattered";

export interface ObstacleSpawn {
  readonly id: number;
  readonly groupId: number;
  readonly pattern: TrafficPattern;
  readonly spawnAtMs: number;
  readonly lane: LaneIndex;
}

interface TrafficTemplate {
  readonly pattern: TrafficPattern;
  readonly nextGroupDelayMs: number;
  readonly obstacles: readonly {
    readonly lane: LaneIndex;
    readonly offsetMs: number;
  }[];
}

const TRAFFIC_TEMPLATES: readonly TrafficTemplate[] = [
  {
    pattern: "single",
    nextGroupDelayMs: 1_450,
    obstacles: [{ lane: 1, offsetMs: 0 }],
  },
  {
    pattern: "staggered-pair",
    nextGroupDelayMs: 2_050,
    obstacles: [
      { lane: 0, offsetMs: 0 },
      { lane: 2, offsetMs: 480 },
    ],
  },
  {
    pattern: "parallel-pair",
    nextGroupDelayMs: 1_850,
    obstacles: [
      { lane: 0, offsetMs: 0 },
      { lane: 1, offsetMs: 0 },
    ],
  },
  {
    pattern: "convoy",
    nextGroupDelayMs: 2_100,
    obstacles: [
      { lane: 2, offsetMs: 0 },
      { lane: 2, offsetMs: 650 },
    ],
  },
  {
    pattern: "scattered",
    nextGroupDelayMs: 2_550,
    obstacles: [
      { lane: 1, offsetMs: 0 },
      { lane: 0, offsetMs: 520 },
      { lane: 2, offsetMs: 1_120 },
    ],
  },
] as const;

const GROUP_DELAY_JITTER_MS = [0, 170, -110, 90, -140, 60] as const;

function rotateLane(lane: LaneIndex, rotation: number): LaneIndex {
  return ((lane + rotation) % 3) as LaneIndex;
}

export function createTrafficSchedule(
  durationMs: number,
  firstGroupAtMs = 1_800,
): readonly ObstacleSpawn[] {
  if (durationMs <= 0 || firstGroupAtMs < 0) {
    throw new Error("Traffic schedule timing must be positive.");
  }

  const schedule: ObstacleSpawn[] = [];
  let groupId = 0;
  let spawnId = 0;
  let groupAtMs = firstGroupAtMs;

  while (groupAtMs < durationMs - 1_000) {
    const template = TRAFFIC_TEMPLATES[groupId % TRAFFIC_TEMPLATES.length]!;
    const rotation = Math.floor(groupId / TRAFFIC_TEMPLATES.length) % 3;

    for (const obstacle of template.obstacles) {
      const spawnAtMs = groupAtMs + obstacle.offsetMs;
      if (spawnAtMs >= durationMs - 700) {
        continue;
      }

      schedule.push({
        id: spawnId,
        groupId,
        pattern: template.pattern,
        spawnAtMs,
        lane: rotateLane(obstacle.lane, rotation),
      });
      spawnId += 1;
    }

    const jitter =
      GROUP_DELAY_JITTER_MS[groupId % GROUP_DELAY_JITTER_MS.length]!;
    groupAtMs += template.nextGroupDelayMs + jitter;
    groupId += 1;
  }

  return schedule.sort((left, right) =>
    left.spawnAtMs === right.spawnAtMs
      ? left.lane - right.lane
      : left.spawnAtMs - right.spawnAtMs,
  );
}
