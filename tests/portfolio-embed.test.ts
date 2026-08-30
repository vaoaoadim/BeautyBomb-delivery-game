import { describe, expect, it } from "vitest";

import {
  PORTFOLIO_CLOSE_REQUEST,
  isPortfolioEmbedSearch,
  isPortfolioHostActivityMessage,
  normalizePortfolioParentOrigin,
} from "../src/integration/portfolioEmbed";

describe("portfolio embed contract", () => {
  it("enables the integration mode only for the explicit portfolio parameter", () => {
    expect(isPortfolioEmbedSearch("?embed=portfolio")).toBe(true);
    expect(isPortfolioEmbedSearch("?embed=other")).toBe(false);
    expect(isPortfolioEmbedSearch("")).toBe(false);
  });

  it("normalizes only valid configured parent origins", () => {
    expect(normalizePortfolioParentOrigin("https://portfolio.example.com/path")).toBe(
      "https://portfolio.example.com",
    );
    expect(normalizePortfolioParentOrigin("not an origin")).toBeNull();
    expect(normalizePortfolioParentOrigin(undefined)).toBeNull();
  });

  it("accepts only the explicit host activity message", () => {
    expect(
      isPortfolioHostActivityMessage({
        source: "portfolio-host",
        version: 1,
        type: "set-game-active",
        active: false,
      }),
    ).toBe(true);
    expect(isPortfolioHostActivityMessage(PORTFOLIO_CLOSE_REQUEST)).toBe(false);
    expect(isPortfolioHostActivityMessage({ type: "set-game-active" })).toBe(false);
  });
});
