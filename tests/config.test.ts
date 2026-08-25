import { describe, expect, it } from "vitest";

import {
  DEMO_PRIZE_WEIGHTS,
  GAME_RENDER_SCALE,
  GAME_VIEWPORT,
  GAMEPLAY_RULES,
  LANE_BASELINES,
  LANE_VISUAL_SCALES,
  OBSTACLE_VISUAL_SCALE_MULTIPLIERS,
  VEHICLE_COLLISION_TO_VISUAL_RATIO,
} from "../src/game/config";

describe("locked game configuration", () => {
  it("keeps the approved viewport, lane composition, and vehicle proportions", () => {
    const minGreenToPinkVisualHeightRatio = 35 / 30;

    expect(GAME_VIEWPORT).toEqual({ width: 360, height: 640 });
    expect(GAME_RENDER_SCALE).toBe(2);
    expect(LANE_BASELINES).toHaveLength(3);
    expect([...LANE_BASELINES]).toEqual(
      [...LANE_BASELINES].sort((a, b) => a - b),
    );
    expect(LANE_VISUAL_SCALES).toEqual([1.12, 1.22, 1.32]);
    expect(VEHICLE_COLLISION_TO_VISUAL_RATIO).toBe(0.84);
    expect(
      OBSTACLE_VISUAL_SCALE_MULTIPLIERS["green-wagon"],
    ).toBeGreaterThanOrEqual(
      minGreenToPinkVisualHeightRatio *
        OBSTACLE_VISUAL_SCALE_MULTIPLIERS["pink-hatchback"],
    );
  });

  it("keeps the approved lives, timing, and demo prize distribution", () => {
    expect(GAMEPLAY_RULES.startingLives).toBe(3);
    expect(GAMEPLAY_RULES.laneSwitchMs).toBe(180);
    expect(GAMEPLAY_RULES.invulnerabilityMs).toBe(1_100);
    expect(GAMEPLAY_RULES.greyboxRunDurationMs).toBe(45_000);
    expect(DEMO_PRIZE_WEIGHTS.reduce((sum, prize) => sum + prize.weight, 0)).toBe(100);
  });
});
