import { createGame } from "./app/createGame";
import { installPortfolioEmbedBridge } from "./integration/portfolioEmbed";
import "./styles.css";

const gameRoot = document.querySelector<HTMLElement>("#game-root");

if (!gameRoot) {
  throw new Error("Game root element was not found.");
}

let game: ReturnType<typeof createGame> | null = null;
let destroyed = false;

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
} catch (error) {
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
  embedBridge.dispose();
  game?.destroy(true);
  game = null;
};

window.addEventListener(
  "pagehide",
  destroyGame,
  { once: true },
);
