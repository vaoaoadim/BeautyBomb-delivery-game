import { describe, expect, it } from "vitest";

import {
  advanceParallaxOffset,
  positiveModulo,
} from "../src/game/systems/parallax";

describe("parallax movement", () => {
  it("keeps route-loop frame-rate independent and bounded by its texture period", () => {
    const at30Fps = Array.from({ length: 30 }).reduce<number>(
      (offset) =>
        advanceParallaxOffset({
          currentOffsetTexturePx: offset,
          texturePixelsPerSecond: 60,
          deltaMs: 1_000 / 30,
          mode: "route-loop",
          loopPeriodTexturePx: 256,
        }),
      0,
    );
    const at60Fps = Array.from({ length: 60 }).reduce<number>(
      (offset) =>
        advanceParallaxOffset({
          currentOffsetTexturePx: offset,
          texturePixelsPerSecond: 60,
          deltaMs: 1_000 / 60,
          mode: "route-loop",
          loopPeriodTexturePx: 256,
        }),
      0,
    );

    expect(at30Fps).toBeCloseTo(60, 8);
    expect(at60Fps).toBeCloseTo(at30Fps, 8);
    expect(
      advanceParallaxOffset({
        currentOffsetTexturePx: 250,
        texturePixelsPerSecond: 20,
        deltaMs: 500,
        mode: "route-loop",
        loopPeriodTexturePx: 256,
      }),
    ).toBe(4);
  });

  it("clamps an arrival-finite layer at its authored end offset", () => {
    expect(
      advanceParallaxOffset({
        currentOffsetTexturePx: 90,
        texturePixelsPerSecond: 40,
        deltaMs: 500,
        mode: "arrival-finite",
        arrivalEndOffsetTexturePx: 100,
      }),
    ).toBe(100);
  });

  it("rejects invalid cyclic inputs instead of producing an unbounded offset", () => {
    expect(() => positiveModulo(10, 0)).toThrow(RangeError);
    expect(() =>
      advanceParallaxOffset({
        currentOffsetTexturePx: 0,
        texturePixelsPerSecond: 1,
        deltaMs: -1,
        mode: "route-loop",
        loopPeriodTexturePx: 128,
      }),
    ).toThrow(RangeError);
  });
});
