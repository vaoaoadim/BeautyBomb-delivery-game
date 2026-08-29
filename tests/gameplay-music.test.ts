import { describe, expect, it } from "vitest";

import { canPlayGameplayMusic } from "../src/game/systems/gameplayMusic";

describe("gameplay music eligibility", () => {
  it("plays only during an unpaused and unmuted active run", () => {
    expect(canPlayGameplayMusic("playing", false, false)).toBe(true);
  });

  it("remains silent on the intro, defeat, and delivery screens", () => {
    expect(canPlayGameplayMusic("ready", false, false)).toBe(false);
    expect(canPlayGameplayMusic("defeated", false, false)).toBe(false);
    expect(canPlayGameplayMusic("delivered", false, false)).toBe(false);
  });

  it("remains silent when the active run is paused or muted", () => {
    expect(canPlayGameplayMusic("playing", true, false)).toBe(false);
    expect(canPlayGameplayMusic("playing", false, true)).toBe(false);
  });
});
