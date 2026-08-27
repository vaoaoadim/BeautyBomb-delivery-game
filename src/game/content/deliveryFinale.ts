import rawDeliveryFinale from "./deliveryFinale.json";

export type DeliveryPresentationPhase =
  | "inactive"
  | "finish-road"
  | "arrival-transition"
  | "reward-prompt"
  | "product-transfer"
  | "complete";

export type DeliveryPresentationEvent =
  | "progress-complete"
  | "finish-road-complete"
  | "arrival-complete"
  | "claim"
  | "product-transfer-complete"
  | "reset";

export interface ArrivalAnchors {
  readonly girl: Readonly<{
    x: number;
    y: number;
    originX: number;
    originY: number;
  }>;
  readonly vehicleStop: Readonly<{ x: number; y: number }>;
  readonly callout: Readonly<{ x: number; y: number }>;
  readonly cta: Readonly<{ x: number; y: number }>;
  readonly productStartOffset: Readonly<{ x: number; y: number }>;
  readonly productTarget: Readonly<{ x: number; y: number }>;
}

export interface DeliveryFinaleContent {
  readonly version: "v2";
  readonly finishRoadDurationMs: number;
  readonly arrivalDecelerationMs: number;
  readonly arrivalRevealMs: number;
  readonly rewardPromptDelayMs: number;
  readonly productFlightDurationMs: number;
  readonly productDisappearDurationMs: number;
  readonly reducedMotion: Readonly<{
    finishRoadDurationMs: number;
    confettiCount: number;
  }>;
  readonly confetti: Readonly<{
    count: number;
    durationMs: number;
    colors: readonly number[];
  }>;
  readonly anchors: ArrivalAnchors;
  readonly runtime: Readonly<{
    girlScale: number;
    productScale: number;
    arrivalStartX: number;
    destinationCityStartOffsetTexturePx: number;
    destinationCityReducedMotionOffsetTexturePx: number;
  }>;
  readonly depth: Readonly<{
    girl: number;
    confetti: number;
    product: number;
    callout: number;
    cta: number;
  }>;
}

export const DELIVERY_FINALE = Object.freeze(
  rawDeliveryFinale as DeliveryFinaleContent,
);

const TRANSITIONS: Readonly<
  Partial<
    Record<
      DeliveryPresentationPhase,
      Partial<Record<DeliveryPresentationEvent, DeliveryPresentationPhase>>
    >
  >
> = Object.freeze({
  inactive: { "progress-complete": "finish-road" },
  "finish-road": { "finish-road-complete": "arrival-transition" },
  "arrival-transition": { "arrival-complete": "product-transfer" },
  "product-transfer": { "product-transfer-complete": "reward-prompt" },
  "reward-prompt": { claim: "complete" },
});

export function advanceDeliveryPresentationPhase(
  phase: DeliveryPresentationPhase,
  event: DeliveryPresentationEvent,
): DeliveryPresentationPhase {
  if (event === "reset") {
    return "inactive";
  }

  return TRANSITIONS[phase]?.[event] ?? phase;
}
