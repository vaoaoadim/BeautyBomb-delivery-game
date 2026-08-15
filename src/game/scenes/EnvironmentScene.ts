import Phaser from "phaser";

import { GAME_VIEWPORT, LANE_CENTERS } from "../config";

export class EnvironmentScene extends Phaser.Scene {
  public constructor() {
    super("environment");
  }

  public create(): void {
    this.cameras.main.setBackgroundColor("#0aaeb8");

    const graphics = this.add.graphics();
    graphics.fillStyle(0x4c4c6c, 1);
    graphics.fillRect(0, 282, GAME_VIEWPORT.width, 240);

    graphics.lineStyle(2, 0xfff3dc, 0.75);
    for (const laneY of LANE_CENTERS.slice(0, -1)) {
      const dividerY = laneY + 37;
      graphics.lineBetween(0, dividerY, GAME_VIEWPORT.width, dividerY);
    }

    this.add
      .text(GAME_VIEWPORT.width / 2, 126, "BEAUTY BOMB\nDELIVERY", {
        align: "center",
        color: "#fff3dc",
        fontFamily: "monospace",
        fontSize: "24px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);

    this.add
      .text(GAME_VIEWPORT.width / 2, 555, "Development environment ready", {
        color: "#1e1d3e",
        fontFamily: "monospace",
        fontSize: "12px",
      })
      .setOrigin(0.5);
  }
}

