export const PORTFOLIO_EMBED_MODE = "portfolio";
export const PORTFOLIO_EMBED_SOURCE = "beautybomb-delivery";
export const PORTFOLIO_EMBED_VERSION = 1;

export const PORTFOLIO_CLOSE_REQUEST = Object.freeze({
  source: PORTFOLIO_EMBED_SOURCE,
  version: PORTFOLIO_EMBED_VERSION,
  type: "request-close",
} as const);

const PORTFOLIO_EMBED_GAME_EVENTS = Object.freeze({
  preloadProgress: "portfolio-embed-preload-progress",
  preloadError: "portfolio-embed-preload-error",
  ready: "portfolio-embed-ready",
});

type PortfolioHostActivityMessage = Readonly<{
  source: "portfolio-host";
  version: 1;
  type: "set-game-active";
  active: boolean;
}>;

type PortfolioGameMessage =
  | Readonly<{
      source: typeof PORTFOLIO_EMBED_SOURCE;
      version: typeof PORTFOLIO_EMBED_VERSION;
      type: "progress";
      progress: number;
    }>
  | Readonly<{
      source: typeof PORTFOLIO_EMBED_SOURCE;
      version: typeof PORTFOLIO_EMBED_VERSION;
      type: "ready";
    }>
  | Readonly<{
      source: typeof PORTFOLIO_EMBED_SOURCE;
      version: typeof PORTFOLIO_EMBED_VERSION;
      type: "error";
      reason: "preload" | "startup";
    }>;

type GameEventEmitter = Readonly<{
  on: (eventName: string, listener: (...args: unknown[]) => void) => unknown;
  off: (eventName: string, listener: (...args: unknown[]) => void) => unknown;
}>;

type PortfolioEmbedOptions = Readonly<{
  onHostActivityChange: (active: boolean) => void;
}>;

let activeCloseRequest: (() => boolean) | null = null;

export function isPortfolioEmbedSearch(search: string): boolean {
  return new URLSearchParams(search).get("embed") === PORTFOLIO_EMBED_MODE;
}

export function normalizePortfolioParentOrigin(
  configuredOrigin: string | undefined,
): string | null {
  if (!configuredOrigin?.trim()) {
    return null;
  }

  try {
    return new URL(configuredOrigin).origin;
  } catch {
    return null;
  }
}

export function isPortfolioHostActivityMessage(
  value: unknown,
): value is PortfolioHostActivityMessage {
  if (!value || typeof value !== "object") {
    return false;
  }

  const message = value as Record<string, unknown>;
  return (
    message.source === "portfolio-host" &&
    message.version === PORTFOLIO_EMBED_VERSION &&
    message.type === "set-game-active" &&
    typeof message.active === "boolean"
  );
}

export function installPortfolioEmbedBridge(
  options: PortfolioEmbedOptions,
): Readonly<{
  isEmbedded: boolean;
  bindGameEvents: (events: GameEventEmitter) => void;
  reportStartupError: () => void;
  dispose: () => void;
}> {
  const isEmbedded = isPortfolioEmbedSearch(window.location.search);
  const parentOrigin = normalizePortfolioParentOrigin(
    import.meta.env.VITE_PORTFOLIO_PARENT_ORIGIN,
  );
  const parentWindow = window.parent;
  let closeRequested = false;
  let gameEvents: GameEventEmitter | null = null;

  const postToHost = (message: PortfolioGameMessage): boolean => {
    if (!isEmbedded || !parentOrigin || parentWindow === window) {
      return false;
    }

    parentWindow.postMessage(message, parentOrigin);
    return true;
  };

  const requestClose = (): boolean => {
    if (
      !isEmbedded ||
      !parentOrigin ||
      parentWindow === window ||
      closeRequested
    ) {
      return false;
    }

    closeRequested = true;
    parentWindow.postMessage(PORTFOLIO_CLOSE_REQUEST, parentOrigin);
    return true;
  };

  const onMessage = (event: MessageEvent<unknown>): void => {
    if (
      !isEmbedded ||
      !parentOrigin ||
      event.origin !== parentOrigin ||
      event.source !== parentWindow ||
      !isPortfolioHostActivityMessage(event.data)
    ) {
      return;
    }

    options.onHostActivityChange(event.data.active);
  };

  const onPreloadProgress = (value: unknown): void => {
    if (typeof value !== "number" || !Number.isFinite(value)) {
      return;
    }

    postToHost({
      source: PORTFOLIO_EMBED_SOURCE,
      version: PORTFOLIO_EMBED_VERSION,
      type: "progress",
      progress: Math.min(1, Math.max(0, value)),
    });
  };

  const onPreloadError = (): void => {
    postToHost({
      source: PORTFOLIO_EMBED_SOURCE,
      version: PORTFOLIO_EMBED_VERSION,
      type: "error",
      reason: "preload",
    });
  };

  const onReady = (): void => {
    postToHost({
      source: PORTFOLIO_EMBED_SOURCE,
      version: PORTFOLIO_EMBED_VERSION,
      type: "ready",
    });
  };

  const unbindGameEvents = (): void => {
    if (!gameEvents) {
      return;
    }

    gameEvents.off(PORTFOLIO_EMBED_GAME_EVENTS.preloadProgress, onPreloadProgress);
    gameEvents.off(PORTFOLIO_EMBED_GAME_EVENTS.preloadError, onPreloadError);
    gameEvents.off(PORTFOLIO_EMBED_GAME_EVENTS.ready, onReady);
    gameEvents = null;
  };

  window.addEventListener("message", onMessage);
  activeCloseRequest = requestClose;

  return {
    isEmbedded,
    bindGameEvents: (events) => {
      unbindGameEvents();
      gameEvents = events;
      gameEvents.on(
        PORTFOLIO_EMBED_GAME_EVENTS.preloadProgress,
        onPreloadProgress,
      );
      gameEvents.on(PORTFOLIO_EMBED_GAME_EVENTS.preloadError, onPreloadError);
      gameEvents.on(PORTFOLIO_EMBED_GAME_EVENTS.ready, onReady);
    },
    reportStartupError: () => {
      postToHost({
        source: PORTFOLIO_EMBED_SOURCE,
        version: PORTFOLIO_EMBED_VERSION,
        type: "error",
        reason: "startup",
      });
    },
    dispose: () => {
      window.removeEventListener("message", onMessage);
      unbindGameEvents();
      if (activeCloseRequest === requestClose) {
        activeCloseRequest = null;
      }
    },
  };
}

export function requestPortfolioEmbedClose(): boolean {
  return activeCloseRequest?.() ?? false;
}

export const PORTFOLIO_EMBED_LIFECYCLE_EVENTS = PORTFOLIO_EMBED_GAME_EVENTS;
