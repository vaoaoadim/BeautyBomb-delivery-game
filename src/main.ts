import { createGame } from "./app/createGame";
import "./styles.css";

const gameRoot = document.querySelector<HTMLElement>("#game-root");

if (!gameRoot) {
  throw new Error("Game root element was not found.");
}

const game = createGame(gameRoot);

window.addEventListener(
  "pagehide",
  () => {
    game.destroy(true);
  },
  { once: true },
);

