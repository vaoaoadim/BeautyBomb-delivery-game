import Phaser from "phaser";

import { GAME_RENDER_SCALE, GAME_VIEWPORT } from "../game/config";
import { GreyboxScene } from "../game/scenes/GreyboxScene";

export function createGame(parent: HTMLElement): Phaser.Game {
  return new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: GAME_VIEWPORT.width * GAME_RENDER_SCALE,
    height: GAME_VIEWPORT.height * GAME_RENDER_SCALE,
    backgroundColor: "#0aaeb8",
    pixelArt: true,
    roundPixels: true,
    render: {
      antialias: false,
      pixelArt: true,
      roundPixels: true,
    },
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH,
      width: GAME_VIEWPORT.width * GAME_RENDER_SCALE,
      height: GAME_VIEWPORT.height * GAME_RENDER_SCALE,
    },
    scene: [GreyboxScene],
  });
}
