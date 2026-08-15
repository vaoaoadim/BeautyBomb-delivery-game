import { describe, expect, it } from "vitest";

import {
  DEMO_PRIZE_WEIGHTS,
  GAME_VIEWPORT,
  GAMEPLAY_RULES,
  LANE_CENTERS,
} from "../src/game/config";

describe("locked game configuration", () => {
  it("keeps the approved portrait viewport and three-lane model", () => {
    expect(GAME_VIEWPORT).toEqual({ width: 360, height: 640 });
    expect(LANE_CENTERS).toHaveLength(3);
    expect([...LANE_CENTERS]).toEqual([...LANE_CENTERS].sort((a, b) => a - b));
  });

  it("keeps the approved lives, timing, and demo prize distribution", () => {
    expect(GAMEPLAY_RULES.startingLives).toBe(3);
    expect(GAMEPLAY_RULES.laneSwitchMs).toBe(180);
    expect(GAMEPLAY_RULES.invulnerabilityMs).toBe(1_100);
    expect(GAMEPLAY_RULES.greyboxRunDurationMs).toBe(45_000);
    expect(DEMO_PRIZE_WEIGHTS.reduce((sum, prize) => sum + prize.weight, 0)).toBe(100);
  });
});
