import { describe, expect, it } from "vitest";

import {
  createTrafficSchedule,
  getSameLaneVisibleGapPx,
  TRAFFIC_MAX_FORMATION_STAGGER_MS,
  TRAFFIC_FINISH_CLEARANCE_MS,
  TRAFFIC_MIN_VISUAL_GAP_PX,
  TRAFFIC_SAFETY_WINDOW_MS,
  type ObstacleSpawn,
  type ObstacleKind,
  type TrafficPattern,
} from "../src/game/content/trafficSchedule";
import { GAMEPLAY_RULES } from "../src/game/config";
import type { LaneIndex } from "../src/game/domain/runState";

function groupById(
  schedule: readonly ObstacleSpawn[],
): ReadonlyMap<number, readonly ObstacleSpawn[]> {
  const groups = new Map<number, ObstacleSpawn[]>();

  for (const obstacle of schedule) {
    const group = groups.get(obstacle.groupId) ?? [];
    group.push(obstacle);
    groups.set(obstacle.groupId, group);
  }

  return groups;
}

describe("deterministic traffic schedule", () => {
  it("is stable for the same timing inputs", () => {
    expect(createTrafficSchedule(45_000)).toEqual(
      createTrafficSchedule(45_000),
    );
  });

  it("uses all intended traffic patterns", () => {
    const patterns = new Set<TrafficPattern>(
      createTrafficSchedule(45_000).map((obstacle) => obstacle.pattern),
    );

    expect(patterns).toEqual(
      new Set([
        "single",
        "parallel-pair",
        "staggered-pair",
        "convoy",
        "scattered",
      ]),
    );
  });

  it("cycles through all three obstacle vehicle kinds", () => {
    const kinds = new Set<ObstacleKind>(
      createTrafficSchedule(45_000).map((obstacle) => obstacle.kind),
    );

    expect(kinds).toEqual(
      new Set(["pink-hatchback", "yellow-sedan", "green-wagon"]),
    );
  });

  it("mixes single cars, synchronized pairs, offsets, and convoys", () => {
    const groups = [...groupById(createTrafficSchedule(45_000)).values()];

    expect(groups.some((group) => group.length === 1)).toBe(true);
    expect(
      groups.some(
        (group) =>
          group.length === 2 &&
          group[0]?.spawnAtMs === group[1]?.spawnAtMs &&
          group[0]?.lane !== group[1]?.lane,
      ),
    ).toBe(true);
    expect(
      groups.some(
        (group) =>
          group.length > 1 &&
          new Set(group.map((obstacle) => obstacle.spawnAtMs)).size > 1,
      ),
    ).toBe(true);
    expect(
      groups.some(
        (group) =>
          group.length === 2 &&
          group[0]?.lane === group[1]?.lane &&
          group[0]?.spawnAtMs !== group[1]?.spawnAtMs,
      ),
    ).toBe(true);
  });

  it("keeps every chronological same-lane pair visually separated", () => {
    const schedule = createTrafficSchedule(45_000);

    for (const lane of [0, 1, 2] as const) {
      const laneSchedule = schedule.filter((obstacle) => obstacle.lane === lane);

      for (let index = 1; index < laneSchedule.length; index += 1) {
        const first = laneSchedule[index - 1]!;
        const second = laneSchedule[index]!;

        expect(getSameLaneVisibleGapPx(first, second)).toBeGreaterThanOrEqual(
          TRAFFIC_MIN_VISUAL_GAP_PX,
        );
      }
    }
  });

  it("keeps cross-lane threats either simultaneous or outside the safety window", () => {
    const schedule = createTrafficSchedule(45_000);

    for (const [index, first] of schedule.entries()) {
      for (const second of schedule.slice(index + 1)) {
        const spawnDelayMs = second.spawnAtMs - first.spawnAtMs;
        if (spawnDelayMs >= TRAFFIC_SAFETY_WINDOW_MS) {
          break;
        }

        if (first.lane !== second.lane) {
          expect(spawnDelayMs).toBeLessThanOrEqual(
            TRAFFIC_MAX_FORMATION_STAGGER_MS,
          );
        }
      }
    }
  });

  it("never blocks all three lanes at one spawn position", () => {
    const lanesByTime = new Map<number, Set<number>>();

    for (const obstacle of createTrafficSchedule(45_000)) {
      const lanes = lanesByTime.get(obstacle.spawnAtMs) ?? new Set<number>();
      lanes.add(obstacle.lane);
      lanesByTime.set(obstacle.spawnAtMs, lanes);
    }

    for (const lanes of lanesByTime.values()) {
      expect(lanes.size).toBeLessThanOrEqual(2);
    }
  });

  it("never emits more than two obstacles in one formation", () => {
    const groups = [...groupById(createTrafficSchedule(45_000)).values()];

    for (const group of groups) {
      expect(group.length).toBeLessThanOrEqual(2);
    }
  });

  it("keeps a safe lane throughout each collision window", () => {
    const schedule = createTrafficSchedule(45_000);
    for (const obstacle of schedule) {
      const activeLanes = new Set(
        schedule
          .filter(
            (candidate) =>
              candidate.spawnAtMs <= obstacle.spawnAtMs &&
              candidate.spawnAtMs >=
                obstacle.spawnAtMs - TRAFFIC_SAFETY_WINDOW_MS,
          )
          .map((candidate) => candidate.lane),
      );

      expect(activeLanes.size).toBeLessThanOrEqual(2);
    }
  });

  it("keeps at least one escape lane reachable from the previous state", () => {
    const schedule = createTrafficSchedule(45_000);
    const eventTimes = [...new Set(schedule.map(({ spawnAtMs }) => spawnAtMs))];
    const laneIndexes: readonly LaneIndex[] = [0, 1, 2];
    let reachableLanes = new Set<LaneIndex>([1]);
    let previousEventAtMs = 0;

    for (const eventAtMs of eventTimes) {
      const blockedLanes = new Set(
        schedule
          .filter(
            ({ spawnAtMs }) =>
              spawnAtMs <= eventAtMs &&
              spawnAtMs >= eventAtMs - TRAFFIC_SAFETY_WINDOW_MS,
          )
          .map(({ lane }) => lane),
      );
      const availableLaneSteps = Math.floor(
        (eventAtMs - previousEventAtMs) / GAMEPLAY_RULES.laneSwitchMs,
      );
      const nextReachableLanes = new Set(
        laneIndexes.filter(
          (lane) =>
            !blockedLanes.has(lane) &&
            [...reachableLanes].some(
              (previousLane) =>
                Math.abs(lane - previousLane) <= availableLaneSteps,
            ),
        ),
      );

      expect(nextReachableLanes.size).toBeGreaterThan(0);
      reachableLanes = nextReachableLanes;
      previousEventAtMs = eventAtMs;
    }
  });

  it("varies the intervals between individual cars", () => {
    const schedule = createTrafficSchedule(45_000);
    const intervals = schedule.slice(1).map(
      (obstacle, index) => obstacle.spawnAtMs - schedule[index]!.spawnAtMs,
    );

    expect(new Set(intervals).size).toBeGreaterThan(5);
  });

  it("leaves enough time for the final obstacle to exit before delivery", () => {
    const schedule = createTrafficSchedule(GAMEPLAY_RULES.greyboxRunDurationMs);
    const lastObstacle = schedule.at(-1);

    expect(lastObstacle).toBeDefined();
    expect(lastObstacle!.spawnAtMs).toBeLessThanOrEqual(
      GAMEPLAY_RULES.greyboxRunDurationMs - TRAFFIC_FINISH_CLEARANCE_MS,
    );
  });
});
