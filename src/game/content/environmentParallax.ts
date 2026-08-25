import rawEnvironmentParallax from "./environmentParallax.json";

import type { ParallaxMovementMode } from "../systems/parallax";

export type ReducedMotionBehavior = "freeze" | "essential";

export type EnvironmentAlphaMode =
  | "opaque-source-crop"
  | "reconstructed-sky"
  | "boundary-connected-city"
  | "approved-alpha-city";

export type EnvironmentCycleMode =
  | "direct-approved-loop"
  | "safe-gutter-direct-panorama";

export interface EnvironmentLayerSpec {
  readonly assetId: string;
  readonly masterId: string;
  readonly textureKey: string;
  readonly runtimeName: string;
  readonly runtimePath: string;
  readonly sourceBox: readonly [number, number, number, number];
  readonly contentCanvas: Readonly<{ width: number; height: number }>;
  readonly textureCanvas: Readonly<{ width: number; height: number }>;
  readonly seamGutterTexturePx: number;
  readonly alphaMode: EnvironmentAlphaMode;
  readonly cycleMode: EnvironmentCycleMode;
  readonly layer: string;
  readonly position: Readonly<{ x: number; y: number }>;
  readonly tileScale: Readonly<{ x: number; y: number }>;
  readonly speedMultiplier: number;
  readonly depth: number;
  readonly reducedMotion: ReducedMotionBehavior;
}

export interface EnvironmentParallaxContent {
  readonly version: "v9";
  readonly masters: readonly Readonly<{
    id: string;
    path: string;
    sha256: string;
  }>[];
  readonly route: Readonly<{
    baseDisplaySpeedPxPerSecond: number;
    mode: Extract<ParallaxMovementMode, "route-loop">;
  }>;
  readonly maskProfiles: Readonly<{
    skyToleranceMaxChannel: number;
    skyToleranceEuclidean: number;
    cityAnchorMinY: number;
    cityBottomSourceY: number;
  }>;
  readonly layers: readonly EnvironmentLayerSpec[];
}

export const ENVIRONMENT_PARALLAX = Object.freeze(
  rawEnvironmentParallax as unknown as EnvironmentParallaxContent,
);
