import { createGame } from "./app/createGame";
import {
  installPortfolioEmbedBridge,
  PORTFOLIO_EMBED_LIFECYCLE_EVENTS,
} from "./integration/portfolioEmbed";
import "./styles.css";

const gameRoot = document.querySelector<HTMLElement>("#game-root");
const loadingScreen = document.querySelector<HTMLElement>("#game-loading");
const loadingProgress = loadingScreen?.querySelector<HTMLElement>(
  ".game-loading__progress",
);
const loadingError = loadingScreen?.querySelector<HTMLElement>(
  ".game-loading__error",
);

if (!gameRoot) {
  throw new Error("Game root element was not found.");
}

let game: ReturnType<typeof createGame> | null = null;
let destroyed = false;

const setLoadingProgress = (value: unknown): void => {
  if (
    !loadingProgress ||
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return;
  }

  const progress = Math.min(1, Math.max(0, value));
  loadingProgress.classList.remove("game-loading__progress--indeterminate");
  loadingProgress.style.setProperty("--game-loading-progress", `${progress * 100}%`);
  loadingProgress.setAttribute("aria-valuenow", String(Math.round(progress * 100)));
};

const showLoadingError = (): void => {
  loadingScreen?.classList.add("game-loading--error");
  loadingScreen?.setAttribute("aria-busy", "false");
  loadingError?.removeAttribute("hidden");
};

const hideLoadingScreen = (): void => {
  if (!loadingScreen) {
    return;
  }

  setLoadingProgress(1);
  loadingScreen.classList.add("game-loading--ready");
  loadingScreen.setAttribute("aria-busy", "false");
};

const setGameActivity = (active: boolean): void => {
  if (!game || destroyed) {
    return;
  }

  game.events.emit("portfolio-embed-activity", active);
  if (active) {
    game.loop.wake();
  } else {
    game.loop.sleep();
  }
};

const embedBridge = installPortfolioEmbedBridge({
  onHostActivityChange: setGameActivity,
});

document.documentElement.classList.toggle("portfolio-embed", embedBridge.isEmbedded);

try {
  game = createGame(gameRoot);
  embedBridge.bindGameEvents(game.events);
  game.events.on(
    PORTFOLIO_EMBED_LIFECYCLE_EVENTS.preloadProgress,
    setLoadingProgress,
  );
  game.events.once(PORTFOLIO_EMBED_LIFECYCLE_EVENTS.preloadError, showLoadingError);
  game.events.once(PORTFOLIO_EMBED_LIFECYCLE_EVENTS.ready, hideLoadingScreen);
} catch (error) {
  showLoadingError();
  embedBridge.reportStartupError();
  throw error;
}

game.canvas.tabIndex = 0;

const focusGame = (): void => {
  game?.canvas.focus({ preventScroll: true });
};

const syncDocumentVisibility = (): void => {
  setGameActivity(!document.hidden);
};

gameRoot.addEventListener("pointerdown", focusGame);
document.addEventListener("visibilitychange", syncDocumentVisibility);
syncDocumentVisibility();

const destroyGame = (): void => {
  if (destroyed) {
    return;
  }

  destroyed = true;
  gameRoot.removeEventListener("pointerdown", focusGame);
  document.removeEventListener("visibilitychange", syncDocumentVisibility);
  game?.events.off(
    PORTFOLIO_EMBED_LIFECYCLE_EVENTS.preloadProgress,
    setLoadingProgress,
  );
  embedBridge.dispose();
  game?.destroy(true);
  game = null;
};

window.addEventListener(
  "pagehide",
  destroyGame,
  { once: true },
);
