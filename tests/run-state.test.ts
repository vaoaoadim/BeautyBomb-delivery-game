import { describe, expect, it } from "vitest";

import { GAMEPLAY_RULES } from "../src/game/config";
import {
  advanceRun,
  createRunState,
  getRunProgress,
  moveLane,
  registerHit,
  retryRun,
  startRun,
} from "../src/game/domain/runState";

describe("run state", () => {
  it("starts in the middle lane with three lives", () => {
    const state = createRunState();

    expect(state.phase).toBe("ready");
    expect(state.lane).toBe(1);
    expect(state.lives).toBe(3);
    expect(getRunProgress(state)).toBe(0);
  });

  it("moves one adjacent lane and clamps at road edges", () => {
    let state = startRun(createRunState());

    state = moveLane(state, -1);
    expect(state.lane).toBe(0);
    expect(moveLane(state, -1)).toBe(state);

    state = moveLane(state, 1);
    state = moveLane(state, 1);
    expect(state.lane).toBe(2);
    expect(moveLane(state, 1)).toBe(state);
  });

  it("ignores repeated hits during temporary invulnerability", () => {
    let state = startRun(createRunState());

    state = registerHit(state);
    expect(state.lives).toBe(2);
    expect(state.invulnerabilityRemainingMs).toBe(
      GAMEPLAY_RULES.invulnerabilityMs,
    );

    state = registerHit(state);
    expect(state.lives).toBe(2);

    state = advanceRun(state, GAMEPLAY_RULES.invulnerabilityMs);
    state = registerHit(state);
    expect(state.lives).toBe(1);
  });

  it("enters defeat at zero lives and retry creates a fresh active run", () => {
    let state = startRun(createRunState());

    for (let hit = 0; hit < 3; hit += 1) {
      state = registerHit(state);
      state = advanceRun(state, GAMEPLAY_RULES.invulnerabilityMs);
    }

    expect(state.phase).toBe("defeated");
    expect(state.lives).toBe(0);

    state = retryRun(state);
    expect(state.phase).toBe("playing");
    expect(state.lives).toBe(3);
    expect(state.elapsedMs).toBe(0);
    expect(state.lane).toBe(1);
  });

  it("advances only while playing and delivers at full progress", () => {
    const ready = createRunState(1_000);
    expect(advanceRun(ready, 500)).toBe(ready);

    const playing = startRun(ready);
    const halfway = advanceRun(playing, 500);
    expect(getRunProgress(halfway)).toBe(0.5);

    const delivered = advanceRun(halfway, 500);
    expect(delivered.phase).toBe("delivered");
    expect(getRunProgress(delivered)).toBe(1);
    expect(advanceRun(delivered, 500)).toBe(delivered);
  });
});
