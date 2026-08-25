import greenWagonAsset from "../../../public/assets/game/vehicles/obs-003-green-wagon-static-v2.json";
import pinkHatchbackAsset from "../../../public/assets/game/vehicles/obs-001-pink-hatchback-static-v2.json";
import yellowSedanAsset from "../../../public/assets/game/vehicles/obs-002-yellow-sedan-static-v2.json";

import {
  GAMEPLAY_RULES,
  LANE_VISUAL_SCALES,
  OBSTACLE_VISUAL_SCALE_MULTIPLIERS,
} from "../config";
import type { LaneIndex } from "../domain/runState";

export type TrafficPattern =
  | "single"
  | "parallel-pair"
  | "staggered-pair"
  | "convoy"
  | "scattered";

export type ObstacleKind =
  | "pink-hatchback"
  | "yellow-sedan"
  | "green-wagon";

export const TRAFFIC_SAFETY_WINDOW_MS = 1_200;
export const TRAFFIC_MAX_FORMATION_STAGGER_MS = 200;
export const CONVOY_SPAWN_GAP_MS = 933;
export const TRAFFIC_MIN_VISUAL_GAP_PX = 48;

export interface ObstacleSpawn {
  readonly id: number;
  readonly groupId: number;
  readonly pattern: TrafficPattern;
  readonly spawnAtMs: number;
  readonly lane: LaneIndex;
  readonly kind: ObstacleKind;
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
    nextGroupDelayMs: 1_341,
    obstacles: [{ lane: 1, offsetMs: 0 }],
  },
  {
    pattern: "staggered-pair",
    nextGroupDelayMs: 2_050,
    obstacles: [
      { lane: 0, offsetMs: 0 },
      { lane: 2, offsetMs: TRAFFIC_MAX_FORMATION_STAGGER_MS },
    ],
  },
  {
    pattern: "parallel-pair",
    nextGroupDelayMs: 1_786,
    obstacles: [
      { lane: 0, offsetMs: 0 },
      { lane: 1, offsetMs: 0 },
    ],
  },
  {
    pattern: "convoy",
    nextGroupDelayMs: 2_273,
    obstacles: [
      { lane: 2, offsetMs: 0 },
      { lane: 2, offsetMs: CONVOY_SPAWN_GAP_MS },
    ],
  },
  {
    pattern: "scattered",
    nextGroupDelayMs: 2_550,
    obstacles: [
      { lane: 1, offsetMs: 0 },
      { lane: 0, offsetMs: TRAFFIC_SAFETY_WINDOW_MS },
    ],
  },
] as const;

const GROUP_DELAY_JITTER_MS = [0, 170, -110, 90, -140, 60] as const;
const OBSTACLE_KINDS: readonly ObstacleKind[] = [
  "pink-hatchback",
  "yellow-sedan",
  "green-wagon",
];

const OBSTACLE_VISIBLE_WIDTHS: Readonly<Record<ObstacleKind, number>> = {
  "pink-hatchback": pinkHatchbackAsset.visibleBounds.width,
  "yellow-sedan": yellowSedanAsset.visibleBounds.width,
  "green-wagon": greenWagonAsset.visibleBounds.width,
};

function rotateLane(lane: LaneIndex, rotation: number): LaneIndex {
  return ((lane + rotation) % 3) as LaneIndex;
}

function getObstacleDisplayWidth(obstacle: ObstacleSpawn): number {
  return (
    OBSTACLE_VISIBLE_WIDTHS[obstacle.kind] *
    LANE_VISUAL_SCALES[obstacle.lane] *
    OBSTACLE_VISUAL_SCALE_MULTIPLIERS[obstacle.kind]
  );
}

export function getSameLaneVisibleGapPx(
  first: ObstacleSpawn,
  second: ObstacleSpawn,
): number {
  if (first.lane !== second.lane) {
    throw new Error("Visible-gap calculation requires obstacles in the same lane.");
  }

  const centerDistancePx =
    ((second.spawnAtMs - first.spawnAtMs) / 1_000) *
    GAMEPLAY_RULES.obstacleSpeedPxPerSecond;

  return (
    centerDistancePx -
    (getObstacleDisplayWidth(first) + getObstacleDisplayWidth(second)) / 2
  );
}

function assertEscapeLane(schedule: readonly ObstacleSpawn[]): void {
  for (const obstacle of schedule) {
    const blockedLanes = new Set(
      schedule
        .filter(
          (candidate) =>
            candidate.spawnAtMs <= obstacle.spawnAtMs &&
            candidate.spawnAtMs >=
              obstacle.spawnAtMs - TRAFFIC_SAFETY_WINDOW_MS,
        )
        .map((candidate) => candidate.lane),
    );

    if (blockedLanes.size === 3) {
      throw new Error(
        `Unsafe traffic schedule near ${obstacle.spawnAtMs}ms: all lanes are blocked.`,
      );
    }
  }
}

function assertSameLaneVisualGaps(schedule: readonly ObstacleSpawn[]): void {
  for (const lane of [0, 1, 2] as const) {
    const laneSchedule = schedule.filter((obstacle) => obstacle.lane === lane);

    for (let index = 1; index < laneSchedule.length; index += 1) {
      const first = laneSchedule[index - 1]!;
      const second = laneSchedule[index]!;
      const visibleGapPx = getSameLaneVisibleGapPx(first, second);

      if (visibleGapPx < TRAFFIC_MIN_VISUAL_GAP_PX) {
        throw new Error(
          `Unsafe same-lane traffic between ${first.id} and ${second.id}: ${visibleGapPx.toFixed(2)}px gap.`,
        );
      }
    }
  }
}

function assertReadableCrossLaneFormations(
  schedule: readonly ObstacleSpawn[],
): void {
  for (const [index, first] of schedule.entries()) {
    for (const second of schedule.slice(index + 1)) {
      const spawnDelayMs = second.spawnAtMs - first.spawnAtMs;
      if (spawnDelayMs >= TRAFFIC_SAFETY_WINDOW_MS) {
        break;
      }

      if (
        first.lane !== second.lane &&
        spawnDelayMs > TRAFFIC_MAX_FORMATION_STAGGER_MS
      ) {
        throw new Error(
          `Unreadable cross-lane traffic between ${first.id} and ${second.id}: ${spawnDelayMs}ms delay.`,
        );
      }
    }
  }
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
        kind: OBSTACLE_KINDS[spawnId % OBSTACLE_KINDS.length]!,
      });
      spawnId += 1;
    }

    const jitter =
      GROUP_DELAY_JITTER_MS[groupId % GROUP_DELAY_JITTER_MS.length]!;
    groupAtMs += template.nextGroupDelayMs + jitter;
    groupId += 1;
  }

  const sortedSchedule = schedule.sort((left, right) =>
    left.spawnAtMs === right.spawnAtMs
      ? left.lane - right.lane
      : left.spawnAtMs - right.spawnAtMs,
  );

  assertEscapeLane(sortedSchedule);
  assertSameLaneVisualGaps(sortedSchedule);
  assertReadableCrossLaneFormations(sortedSchedule);
  return sortedSchedule;
}
