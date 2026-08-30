export const PORTFOLIO_EMBED_MODE = "portfolio";
export const PORTFOLIO_EMBED_SOURCE = "beautybomb-delivery";
export const PORTFOLIO_EMBED_VERSION = 1;

export const PORTFOLIO_CLOSE_REQUEST = Object.freeze({
  source: PORTFOLIO_EMBED_SOURCE,
  version: PORTFOLIO_EMBED_VERSION,
  type: "request-close",
} as const);

type PortfolioHostActivityMessage = Readonly<{
  source: "portfolio-host";
  version: 1;
  type: "set-game-active";
  active: boolean;
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
): Readonly<{ isEmbedded: boolean; dispose: () => void }> {
  const isEmbedded = isPortfolioEmbedSearch(window.location.search);
  const parentOrigin = normalizePortfolioParentOrigin(
    import.meta.env.VITE_PORTFOLIO_PARENT_ORIGIN,
  );
  const parentWindow = window.parent;
  let closeRequested = false;

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

  window.addEventListener("message", onMessage);
  activeCloseRequest = requestClose;

  return {
    isEmbedded,
    dispose: () => {
      window.removeEventListener("message", onMessage);
      if (activeCloseRequest === requestClose) {
        activeCloseRequest = null;
      }
    },
  };
}

export function requestPortfolioEmbedClose(): boolean {
  return activeCloseRequest?.() ?? false;
}
