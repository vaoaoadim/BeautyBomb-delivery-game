export type ParallaxMovementMode = "route-loop" | "arrival-finite";

export interface ParallaxAdvanceInput {
  readonly currentOffsetTexturePx: number;
  readonly texturePixelsPerSecond: number;
  readonly deltaMs: number;
  readonly mode: ParallaxMovementMode;
  readonly loopPeriodTexturePx?: number;
  readonly arrivalEndOffsetTexturePx?: number;
}

function assertFinite(name: string, value: number): void {
  if (!Number.isFinite(value)) {
    throw new RangeError(`${name} must be a finite number.`);
  }
}

export function positiveModulo(value: number, modulus: number): number {
  assertFinite("value", value);
  assertFinite("modulus", modulus);
  if (modulus <= 0) {
    throw new RangeError("modulus must be greater than zero.");
  }

  return ((value % modulus) + modulus) % modulus;
}

export function advanceParallaxOffset({
  currentOffsetTexturePx,
  texturePixelsPerSecond,
  deltaMs,
  mode,
  loopPeriodTexturePx,
  arrivalEndOffsetTexturePx,
}: ParallaxAdvanceInput): number {
  assertFinite("currentOffsetTexturePx", currentOffsetTexturePx);
  assertFinite("texturePixelsPerSecond", texturePixelsPerSecond);
  assertFinite("deltaMs", deltaMs);
  if (deltaMs < 0) {
    throw new RangeError("deltaMs cannot be negative.");
  }

  const nextOffset =
    currentOffsetTexturePx + texturePixelsPerSecond * (deltaMs / 1_000);

  if (mode === "route-loop") {
    if (loopPeriodTexturePx === undefined) {
      throw new RangeError("route-loop requires loopPeriodTexturePx.");
    }
    return positiveModulo(nextOffset, loopPeriodTexturePx);
  }

  if (arrivalEndOffsetTexturePx === undefined) {
    throw new RangeError(
      "arrival-finite requires arrivalEndOffsetTexturePx.",
    );
  }
  assertFinite("arrivalEndOffsetTexturePx", arrivalEndOffsetTexturePx);
  if (arrivalEndOffsetTexturePx < 0) {
    throw new RangeError("arrivalEndOffsetTexturePx cannot be negative.");
  }

  return Math.min(
    Math.max(nextOffset, 0),
    arrivalEndOffsetTexturePx,
  );
}
