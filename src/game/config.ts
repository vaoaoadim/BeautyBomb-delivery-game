export const GAME_VIEWPORT = Object.freeze({
  width: 360,
  height: 640,
});

export const LANE_CENTERS = [326, 400, 474] as const;

export const GAMEPLAY_RULES = Object.freeze({
  startingLives: 3,
  laneSwitchMs: 180,
  invulnerabilityMs: 1_100,
  greyboxRunDurationMs: 45_000,
  obstacleSpeedPxPerSecond: 172,
  runDurationSeconds: {
    min: 45,
    max: 60,
  },
});

export const DEMO_PRIZE_WEIGHTS = Object.freeze([
  { discountPercent: 20, weight: 50 },
  { discountPercent: 25, weight: 30 },
  { discountPercent: 30, weight: 15 },
  { discountPercent: 35, weight: 5 },
] as const);
