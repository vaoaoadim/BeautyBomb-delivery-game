export const GAME_VIEWPORT = Object.freeze({
  width: 360,
  height: 640,
});

export const GAME_RENDER_SCALE = 2;

export const LANE_BASELINES = [350, 424, 508] as const;
export const LANE_VISUAL_SCALES = [1.12, 1.22, 1.32] as const;
export const VEHICLE_COLLISION_TO_VISUAL_RATIO = 0.84;
export const OBSTACLE_VISUAL_SCALE_MULTIPLIERS = Object.freeze({
  "pink-hatchback": 1,
  "yellow-sedan": 1.04,
  "green-wagon": 1.18,
} as const);

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
