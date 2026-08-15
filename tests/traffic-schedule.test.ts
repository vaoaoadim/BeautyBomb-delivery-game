import { describe, expect, it } from "vitest";

import {
  createTrafficSchedule,
  type ObstacleSpawn,
  type TrafficPattern,
} from "../src/game/content/trafficSchedule";

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

  it("keeps a safe lane throughout each collision window", () => {
    const schedule = createTrafficSchedule(45_000);
    const collisionWindowMs = 850;

    for (const obstacle of schedule) {
      const activeLanes = new Set(
        schedule
          .filter(
            (candidate) =>
              candidate.spawnAtMs <= obstacle.spawnAtMs &&
              candidate.spawnAtMs >= obstacle.spawnAtMs - collisionWindowMs,
          )
          .map((candidate) => candidate.lane),
      );

      expect(activeLanes.size).toBeLessThanOrEqual(2);
    }
  });

  it("varies the intervals between individual cars", () => {
    const schedule = createTrafficSchedule(45_000);
    const intervals = schedule.slice(1).map(
      (obstacle, index) => obstacle.spawnAtMs - schedule[index]!.spawnAtMs,
    );

    expect(new Set(intervals).size).toBeGreaterThan(5);
  });
});
