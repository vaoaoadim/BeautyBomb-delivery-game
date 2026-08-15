import Phaser from "phaser";

import { GAME_VIEWPORT } from "../game/config";
import { GreyboxScene } from "../game/scenes/GreyboxScene";

export function createGame(parent: HTMLElement): Phaser.Game {
  return new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: GAME_VIEWPORT.width,
    height: GAME_VIEWPORT.height,
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
      width: GAME_VIEWPORT.width,
      height: GAME_VIEWPORT.height,
    },
    scene: [GreyboxScene],
  });
}
