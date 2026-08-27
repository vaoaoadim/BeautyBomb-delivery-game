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

  it("parks on the upper road edge and keeps the product start local to the van", () => {
    expect(DELIVERY_FINALE.anchors.vehicleStop).toEqual({ x: 74, y: 322 });
    expect(DELIVERY_FINALE.anchors.productStartOffset).toEqual({
      x: -4,
      y: -64,
    });
  });

  it("keeps the recipient doorway arrival and lower reward UI on their approved finale anchors", () => {
    expect(DELIVERY_FINALE.anchors).toMatchObject({
      girl: { originX: 0.5, originY: 1 },
      character: {
        doorwayStart: { x: 307, y: 276 },
        doorstepEnd: { x: 319, y: 284 },
        productTarget: { x: 319, y: 262 },
      },
      callout: { x: 14, y: 338 },
      cta: { x: 180, y: 466 },
    });
    expect(DELIVERY_FINALE.runtime.destinationCityStartOffsetTexturePx).toBe(
      526,
    );
    expect(
      DELIVERY_FINALE.runtime.destinationCityReducedMotionOffsetTexturePx,
    ).toBe(701);
    expect(522 - (DELIVERY_FINALE.anchors.cta.y + 18 * 1.06)).toBeGreaterThanOrEqual(
      14,
    );
  });

  it("advances through the finale exactly in the intended order", () => {
    const events: readonly DeliveryPresentationEvent[] = [
      "progress-complete",
      "finish-road-complete",
      "arrival-complete",
      "product-transfer-complete",
      "claim",
    ];
    const expected: readonly DeliveryPresentationPhase[] = [
      "finish-road",
      "arrival-transition",
      "product-transfer",
      "reward-prompt",
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
      advanceDeliveryPresentationPhase("arrival-transition", "claim"),
    ).toBe("arrival-transition");
    expect(
      advanceDeliveryPresentationPhase("product-transfer", "claim"),
    ).toBe("product-transfer");
    expect(advanceDeliveryPresentationPhase("complete", "reset")).toBe(
      "inactive",
    );
  });
});
