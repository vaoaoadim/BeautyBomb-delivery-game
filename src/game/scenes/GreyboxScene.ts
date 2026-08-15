import Phaser from "phaser";

import { GAME_VIEWPORT, GAMEPLAY_RULES, LANE_CENTERS } from "../config";
import {
  createTrafficSchedule,
  type ObstacleSpawn,
} from "../content/trafficSchedule";
import {
  advanceRun,
  createRunState,
  getRunProgress,
  moveLane,
  registerHit,
  retryRun,
  startRun,
  type LaneDirection,
  type RunPhase,
  type RunState,
} from "../domain/runState";

interface ActiveObstacle {
  readonly body: Phaser.GameObjects.Rectangle;
  readonly lane: number;
}

const COLORS = Object.freeze({
  sky: 0x08b7b0,
  skylineFar: 0x247b8f,
  skylineNear: 0x17566d,
  road: 0x34344f,
  laneLine: 0xfff4df,
  cream: 0xf8f1df,
  cyan: 0x16c6dc,
  pink: 0xff4d91,
  lime: 0xd8f34a,
  navy: 0x17162f,
  danger: 0xff5b5b,
});

const ROAD_TOP = 282;
const ROAD_BOTTOM = 522;
const PLAYER_X = 74;
const OBSTACLE_SPAWN_X = GAME_VIEWPORT.width + 42;

export class GreyboxScene extends Phaser.Scene {
  private runState: RunState = createRunState();
  private readonly trafficSchedule: readonly ObstacleSpawn[] = createTrafficSchedule(
    GAMEPLAY_RULES.greyboxRunDurationMs,
  );
  private nextObstacleIndex = 0;
  private obstacles: ActiveObstacle[] = [];
  private player!: Phaser.GameObjects.Container;
  private livesText!: Phaser.GameObjects.Text;
  private statusText!: Phaser.GameObjects.Text;
  private progressFill!: Phaser.GameObjects.Rectangle;
  private promptOverlay!: Phaser.GameObjects.Container;
  private promptTitle!: Phaser.GameObjects.Text;
  private promptBody!: Phaser.GameObjects.Text;
  private promptButton!: Phaser.GameObjects.Text;
  private laneTweenActive = false;
  private bufferedDirection: LaneDirection | null = null;
  private displayedPhase: RunPhase = "ready";

  public constructor() {
    super("greybox");
  }

  public create(): void {
    this.runState = createRunState();
    this.nextObstacleIndex = 0;
    this.obstacles = [];
    this.displayedPhase = "ready";

    this.drawEnvironment();
    this.createHud();
    this.player = this.createPlayer();
    this.createTouchControls();
    this.createOverlay();
    this.bindKeyboard();
    this.updateHud();
  }

  public update(_time: number, delta: number): void {
    if (this.runState.phase !== "playing") {
      return;
    }

    const previousPhase = this.runState.phase;
    this.runState = advanceRun(this.runState, delta);
    this.spawnDueObstacles();
    this.moveObstacles(delta);
    this.checkCollisions();
    this.updateHud();

    this.player.setAlpha(
      this.runState.invulnerabilityRemainingMs > 0 &&
        Math.floor(this.runState.invulnerabilityRemainingMs / 90) % 2 === 0
        ? 0.34
        : 1,
    );

    if (this.runState.phase !== previousPhase) {
      this.showPhase(this.runState.phase);
    }
  }

  private drawEnvironment(): void {
    this.cameras.main.setBackgroundColor(COLORS.sky);

    const graphics = this.add.graphics();
    graphics.fillStyle(COLORS.cream, 1);
    graphics.fillRect(26, 76, 76, 14);
    graphics.fillRect(44, 64, 35, 12);
    graphics.fillRect(228, 105, 94, 14);
    graphics.fillRect(252, 92, 42, 14);

    graphics.fillStyle(COLORS.skylineFar, 1);
    graphics.fillRect(0, 180, 62, 102);
    graphics.fillRect(66, 208, 48, 74);
    graphics.fillRect(118, 164, 68, 118);
    graphics.fillRect(190, 194, 52, 88);
    graphics.fillRect(246, 151, 72, 131);
    graphics.fillRect(322, 218, 38, 64);

    graphics.fillStyle(COLORS.skylineNear, 1);
    graphics.fillRect(0, 236, 92, 46);
    graphics.fillRect(99, 224, 74, 58);
    graphics.fillRect(180, 242, 106, 40);
    graphics.fillRect(294, 229, 66, 53);

    graphics.fillStyle(COLORS.road, 1);
    graphics.fillRect(0, ROAD_TOP, GAME_VIEWPORT.width, ROAD_BOTTOM - ROAD_TOP);
    graphics.lineStyle(2, COLORS.laneLine, 0.6);
    graphics.lineBetween(0, 363, GAME_VIEWPORT.width, 363);
    graphics.lineBetween(0, 437, GAME_VIEWPORT.width, 437);
    graphics.lineStyle(4, COLORS.lime, 1);
    graphics.lineBetween(0, ROAD_TOP, GAME_VIEWPORT.width, ROAD_TOP);
    graphics.lineBetween(0, ROAD_BOTTOM, GAME_VIEWPORT.width, ROAD_BOTTOM);

    this.add
      .text(GAME_VIEWPORT.width / 2, 32, "BEAUTY BOMB DELIVERY", {
        color: "#fff4df",
        fontFamily: "monospace",
        fontSize: "17px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);
  }

  private createHud(): void {
    this.livesText = this.add.text(18, 106, "", {
      color: "#fff4df",
      fontFamily: "monospace",
      fontSize: "16px",
      fontStyle: "bold",
    });

    this.statusText = this.add
      .text(GAME_VIEWPORT.width - 18, 108, "", {
        align: "right",
        color: "#fff4df",
        fontFamily: "monospace",
        fontSize: "12px",
      })
      .setOrigin(1, 0);

    this.add
      .rectangle(18, 142, GAME_VIEWPORT.width - 36, 12, COLORS.navy, 0.75)
      .setOrigin(0, 0.5);
    this.progressFill = this.add
      .rectangle(20, 142, 0, 8, COLORS.lime, 1)
      .setOrigin(0, 0.5);
  }

  private createPlayer(): Phaser.GameObjects.Container {
    const container = this.add.container(PLAYER_X, LANE_CENTERS[1]);
    const shadow = this.add.rectangle(0, 18, 76, 12, COLORS.navy, 0.35);
    const van = this.add.rectangle(0, 0, 72, 38, COLORS.cyan, 1);
    van.setStrokeStyle(3, COLORS.navy, 1);
    const cabin = this.add.rectangle(21, -8, 20, 15, COLORS.cream, 1);
    const wheelLeft = this.add.circle(-22, 20, 8, COLORS.navy, 1);
    const wheelRight = this.add.circle(23, 20, 8, COLORS.navy, 1);
    const creamTube = this.add.rectangle(0, -29, 56, 15, COLORS.cream, 1);
    creamTube.setStrokeStyle(3, COLORS.navy, 1);
    const tubeCap = this.add.rectangle(31, -29, 7, 17, COLORS.pink, 1);
    const label = this.add
      .text(-17, -5, "BB", {
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "12px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);

    container.add([
      shadow,
      van,
      cabin,
      wheelLeft,
      wheelRight,
      creamTube,
      tubeCap,
      label,
    ]);
    container.setSize(78, 66);
    container.setDepth(20);
    return container;
  }

  private createTouchControls(): void {
    const hint = this.add
      .text(18, 544, "MOVE", {
        color: "#fff4df",
        fontFamily: "monospace",
        fontSize: "12px",
      })
      .setOrigin(0, 0.5);

    const up = this.createControlButton(132, 575, "▲", -1);
    const down = this.createControlButton(228, 575, "▼", 1);
    hint.setDepth(30);
    up.setDepth(30);
    down.setDepth(30);
  }

  private createControlButton(
    x: number,
    y: number,
    label: string,
    direction: LaneDirection,
  ): Phaser.GameObjects.Container {
    const button = this.add.container(x, y);
    const background = this.add.rectangle(0, 0, 76, 48, COLORS.cream, 1);
    background.setStrokeStyle(3, COLORS.navy, 1);
    background.setInteractive({ useHandCursor: true });
    const text = this.add
      .text(0, 0, label, {
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "24px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);

    background.on("pointerdown", () => {
      background.setFillStyle(COLORS.lime, 1);
      this.requestLaneMove(direction);
    });
    background.on("pointerup", () => background.setFillStyle(COLORS.cream, 1));
    background.on("pointerout", () => background.setFillStyle(COLORS.cream, 1));
    button.add([background, text]);
    return button;
  }

  private createOverlay(): void {
    const shade = this.add.rectangle(
      GAME_VIEWPORT.width / 2,
      GAME_VIEWPORT.height / 2,
      GAME_VIEWPORT.width,
      GAME_VIEWPORT.height,
      COLORS.navy,
      0.78,
    );
    const panel = this.add.rectangle(180, 322, 302, 238, COLORS.cream, 1);
    panel.setStrokeStyle(5, COLORS.pink, 1);

    this.promptTitle = this.add
      .text(180, 260, "DELIVER THE CREAM", {
        align: "center",
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "20px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);
    this.promptBody = this.add
      .text(180, 312, "Dodge traffic.\nYou have 3 lives.", {
        align: "center",
        color: "#34344f",
        fontFamily: "monospace",
        fontSize: "13px",
        lineSpacing: 7,
      })
      .setOrigin(0.5);
    this.promptButton = this.add
      .text(180, 382, "START", {
        backgroundColor: "#d8f34a",
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "18px",
        fontStyle: "bold",
        padding: { x: 28, y: 12 },
      })
      .setOrigin(0.5)
      .setInteractive({ useHandCursor: true });
    this.promptButton.on("pointerdown", () => this.activateOverlayAction());

    this.promptOverlay = this.add.container(0, 0, [
      shade,
      panel,
      this.promptTitle,
      this.promptBody,
      this.promptButton,
    ]);
    this.promptOverlay.setDepth(100);
  }

  private bindKeyboard(): void {
    const keyboard = this.input.keyboard;
    if (!keyboard) {
      return;
    }

    keyboard.on("keydown-UP", () => this.requestLaneMove(-1));
    keyboard.on("keydown-W", () => this.requestLaneMove(-1));
    keyboard.on("keydown-DOWN", () => this.requestLaneMove(1));
    keyboard.on("keydown-S", () => this.requestLaneMove(1));
    keyboard.on("keydown-ENTER", () => this.activateOverlayAction());
    keyboard.on("keydown-SPACE", () => this.activateOverlayAction());
  }

  private activateOverlayAction(): void {
    if (this.runState.phase === "ready") {
      this.runState = startRun(this.runState);
      this.promptOverlay.setVisible(false);
      this.displayedPhase = "playing";
      this.updateHud();
      return;
    }

    if (
      this.runState.phase === "defeated" ||
      this.runState.phase === "delivered"
    ) {
      this.resetRun();
    }
  }

  private requestLaneMove(direction: LaneDirection): void {
    if (this.runState.phase !== "playing") {
      return;
    }

    if (this.laneTweenActive) {
      this.bufferedDirection = direction;
      return;
    }

    const nextState = moveLane(this.runState, direction);
    if (nextState === this.runState) {
      return;
    }

    this.runState = nextState;
    this.laneTweenActive = true;
    this.tweens.add({
      targets: this.player,
      y: LANE_CENTERS[this.runState.lane],
      duration: GAMEPLAY_RULES.laneSwitchMs,
      ease: "Cubic.Out",
      onComplete: () => {
        this.laneTweenActive = false;
        const bufferedDirection = this.bufferedDirection;
        this.bufferedDirection = null;
        if (bufferedDirection !== null) {
          this.requestLaneMove(bufferedDirection);
        }
      },
    });
  }

  private spawnDueObstacles(): void {
    let nextObstacle = this.trafficSchedule[this.nextObstacleIndex];
    while (
      nextObstacle &&
      nextObstacle.spawnAtMs <= this.runState.elapsedMs
    ) {
      this.spawnObstacle(nextObstacle);
      this.nextObstacleIndex += 1;
      nextObstacle = this.trafficSchedule[this.nextObstacleIndex];
    }
  }

  private spawnObstacle(obstacle: ObstacleSpawn): void {
    const body = this.add.rectangle(
      OBSTACLE_SPAWN_X,
      LANE_CENTERS[obstacle.lane],
      62,
      42,
      obstacle.id % 2 === 0 ? COLORS.pink : COLORS.lime,
      1,
    );
    body.setStrokeStyle(3, COLORS.navy, 1);
    body.setDepth(18);
    this.obstacles.push({ body, lane: obstacle.lane });
  }

  private moveObstacles(delta: number): void {
    const distance =
      GAMEPLAY_RULES.obstacleSpeedPxPerSecond * (delta / 1_000);
    const remaining: ActiveObstacle[] = [];

    for (const obstacle of this.obstacles) {
      obstacle.body.x -= distance;
      if (obstacle.body.x < -48) {
        obstacle.body.destroy();
      } else {
        remaining.push(obstacle);
      }
    }

    this.obstacles = remaining;
  }

  private checkCollisions(): void {
    if (this.runState.invulnerabilityRemainingMs > 0) {
      return;
    }

    const playerBounds = this.player.getBounds();
    const collidedIndex = this.obstacles.findIndex((obstacle) =>
      Phaser.Geom.Intersects.RectangleToRectangle(
        playerBounds,
        obstacle.body.getBounds(),
      ),
    );

    if (collidedIndex === -1) {
      return;
    }

    const [collided] = this.obstacles.splice(collidedIndex, 1);
    if (!collided) {
      return;
    }
    collided.body.destroy();
    this.runState = registerHit(this.runState);
    this.cameras.main.shake(110, 0.008);
    this.updateHud();

    if (this.runState.phase === "defeated") {
      this.showPhase("defeated");
    }
  }

  private updateHud(): void {
    const hearts = "♥".repeat(this.runState.lives);
    this.livesText.setText(`LIVES ${hearts || "0"}`);
    this.livesText.setColor(
      this.runState.lives > 1 ? "#fff4df" : "#ff5b5b",
    );

    const progress = getRunProgress(this.runState);
    this.progressFill.width = Math.max(0, (GAME_VIEWPORT.width - 40) * progress);
    this.statusText.setText(
      this.runState.phase === "playing"
        ? `${Math.ceil((this.runState.durationMs - this.runState.elapsedMs) / 1_000)}s`
        : this.runState.phase.toUpperCase(),
    );
  }

  private showPhase(phase: RunPhase): void {
    if (this.displayedPhase === phase) {
      return;
    }
    this.displayedPhase = phase;

    if (phase === "delivered") {
      this.clearObstacles();
      this.promptTitle.setText("ORDER DELIVERED!");
      this.promptBody.setText("Greybox route complete.\nPrize roulette comes later.");
      this.promptButton.setText("PLAY AGAIN");
      this.promptOverlay.setVisible(true);
    } else if (phase === "defeated") {
      this.promptTitle.setText("DELIVERY FAILED");
      this.promptBody.setText("No lives left.\nTry the route again.");
      this.promptButton.setText("RETRY");
      this.promptOverlay.setVisible(true);
    }
  }

  private resetRun(): void {
    this.tweens.killTweensOf(this.player);
    this.clearObstacles();
    this.runState = retryRun(this.runState);
    this.nextObstacleIndex = 0;
    this.laneTweenActive = false;
    this.bufferedDirection = null;
    this.displayedPhase = "playing";
    this.player.setPosition(PLAYER_X, LANE_CENTERS[this.runState.lane]);
    this.player.setAlpha(1);
    this.promptOverlay.setVisible(false);
    this.updateHud();
  }

  private clearObstacles(): void {
    for (const obstacle of this.obstacles) {
      obstacle.body.destroy();
    }
    this.obstacles = [];
  }
}
