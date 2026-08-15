import { describe, expect, it } from "vitest";

import { createObstacleWaves } from "../src/game/content/obstacleWaves";

describe("deterministic obstacle waves", () => {
  it("keeps exactly one safe lane in every wave", () => {
    const waves = createObstacleWaves(10_000);

    expect(waves.length).toBeGreaterThan(0);

    for (const wave of waves) {
      const lanes = [wave.safeLane, ...wave.blockedLanes];
      expect(new Set(lanes)).toEqual(new Set([0, 1, 2]));
      expect(wave.blockedLanes).toHaveLength(2);
    }
  });

  it("is stable for the same timing inputs", () => {
    expect(createObstacleWaves(10_000)).toEqual(
      createObstacleWaves(10_000),
    );
  });
});
