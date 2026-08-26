import { describe, expect, it } from "vitest";

import {
  advanceDeliveryPresentationPhase,
  DELIVERY_FINALE,
  type DeliveryPresentationEvent,
  type DeliveryPresentationPhase,
} from "../src/game/content/deliveryFinale";

describe("delivery finale presentation", () => {
  it("keeps the route duration separate from the 1.5 second finish road", () => {
    expect(DELIVERY_FINALE.finishRoadDurationMs).toBe(1_500);
    expect(DELIVERY_FINALE.finishRoadDurationMs).toBeGreaterThanOrEqual(1_000);
    expect(DELIVERY_FINALE.finishRoadDurationMs).toBeLessThanOrEqual(2_000);
  });

  it("advances through the finale exactly in the intended order", () => {
    const events: readonly DeliveryPresentationEvent[] = [
      "progress-complete",
      "finish-road-complete",
      "arrival-complete",
      "claim",
      "product-transfer-complete",
    ];
    const expected: readonly DeliveryPresentationPhase[] = [
      "finish-road",
      "arrival-transition",
      "reward-prompt",
      "product-transfer",
      "complete",
    ];

    let phase: DeliveryPresentationPhase = "inactive";
    for (const [index, event] of events.entries()) {
      phase = advanceDeliveryPresentationPhase(phase, event);
      expect(phase).toBe(expected[index]);
    }
  });

  it("ignores click-through and duplicate transition events", () => {
    expect(advanceDeliveryPresentationPhase("inactive", "claim")).toBe(
      "inactive",
    );
    expect(
      advanceDeliveryPresentationPhase("product-transfer", "claim"),
    ).toBe("product-transfer");
    expect(advanceDeliveryPresentationPhase("complete", "reset")).toBe(
      "inactive",
    );
  });
});
