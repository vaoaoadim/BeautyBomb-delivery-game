import { afterEach, describe, expect, it, vi } from "vitest";

import {
  PORTFOLIO_CLOSE_REQUEST,
  isPortfolioEmbedSearch,
  isPortfolioHostActivityMessage,
  normalizePortfolioParentOrigin,
  installPortfolioEmbedBridge,
  requestPortfolioEmbedClose,
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
    expect(normalizePortfolioParentOrigin("data:text/html,test")).toBeNull();
    expect(normalizePortfolioParentOrigin("file:///tmp/test")).toBeNull();
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

describe("portfolio host allowlist", () => {
  const sites = "https://vao-dev-portfolio.bsdvbk.chatgpt.site";
  const pages = "https://vaoaoadim.github.io";
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  function setup(referrer: string) {
    const parent = { postMessage: vi.fn() };
    const handlers = new Map<string, (event: MessageEvent) => void>();
    vi.stubEnv("VITE_PORTFOLIO_PARENT_ORIGIN", `${sites},${pages}`);
    vi.stubGlobal("document", { referrer });
    vi.stubGlobal("window", {
      location: { search: "?embed=portfolio" },
      parent,
      addEventListener: (name: string, handler: (event: MessageEvent) => void) => handlers.set(name, handler),
      removeEventListener: (name: string) => handlers.delete(name),
    });
    const onHostActivityChange = vi.fn();
    const bridge = installPortfolioEmbedBridge({ onHostActivityChange });
    const activity = (origin: string, source: unknown = parent) => handlers.get("message")?.({
      origin, source,
      data: { source: "portfolio-host", version: 1, type: "set-game-active", active: false },
    } as MessageEvent);
    return { parent, activity, bridge, onHostActivityChange };
  }

  it.each([sites, pages])("sends one close request to the actual allowed host %s", (origin) => {
    const { parent, activity, bridge, onHostActivityChange } = setup(`${origin}/portfolio/`);
    activity(origin);
    expect(onHostActivityChange).toHaveBeenCalledWith(false);
    expect(requestPortfolioEmbedClose()).toBe(true);
    expect(parent.postMessage).toHaveBeenCalledWith(PORTFOLIO_CLOSE_REQUEST, origin);
    expect(requestPortfolioEmbedClose()).toBe(false);
    expect(parent.postMessage).toHaveBeenCalledTimes(1);
    bridge.dispose();
  });

  it("learns an allowed host only from a validated parent message when referrer is absent", () => {
    const { parent, activity, bridge, onHostActivityChange } = setup("");
    expect(requestPortfolioEmbedClose()).toBe(false);
    activity("https://untrusted.example");
    activity(pages, {});
    expect(onHostActivityChange).not.toHaveBeenCalled();
    activity(pages);
    expect(requestPortfolioEmbedClose()).toBe(true);
    expect(parent.postMessage).toHaveBeenCalledWith(PORTFOLIO_CLOSE_REQUEST, pages);
    bridge.dispose();
  });
});
