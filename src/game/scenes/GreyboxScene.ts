import Phaser from "phaser";

import {
  GAME_VIEWPORT,
  GAME_RENDER_SCALE,
  GAMEPLAY_RULES,
  LANE_BASELINES,
  LANE_VISUAL_SCALES,
  OBSTACLE_VISUAL_SCALE_MULTIPLIERS,
  VEHICLE_COLLISION_TO_VISUAL_RATIO,
} from "../config";
import {
  createTrafficSchedule,
  type ObstacleKind,
  type ObstacleSpawn,
} from "../content/trafficSchedule";
import {
  ENVIRONMENT_PARALLAX,
  type EnvironmentLayerSpec,
} from "../content/environmentParallax";
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
import {
  advanceParallaxOffset,
  type ParallaxMovementMode,
} from "../systems/parallax";

interface CollisionSpec {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

interface ActiveObstacle {
  readonly sprite: Phaser.GameObjects.Sprite;
  readonly lane: number;
  readonly originPixelX: number;
  readonly originPixelY: number;
  readonly collision: CollisionSpec;
  readonly collisionScaleRatio: number;
}

interface ObstacleAssetSpec {
  readonly textureKey: string;
  readonly path: string;
  readonly frameWidth: number;
  readonly frameHeight: number;
  readonly driveAnimationKey: string;
  readonly canvasHeight: number;
  readonly originPixelX: number;
  readonly originPixelY: number;
  readonly collision: CollisionSpec;
  readonly visualScaleMultiplier: number;
}

interface ActiveEnvironmentLayer {
  readonly sprite: Phaser.GameObjects.TileSprite;
  readonly spec: EnvironmentLayerSpec;
  arrivalEndOffsetTexturePx: number;
}

const COLORS = Object.freeze({
  sky: 0x73e6f7,
  cream: 0xf8f1df,
  cyan: 0x16c6dc,
  pink: 0xff4d91,
  navy: 0x17162f,
  danger: 0xff5b5b,
});

const PLAYER_X = 74;
const OBSTACLE_SPAWN_X = GAME_VIEWPORT.width + 72;
const PLAYER_ASSET = Object.freeze({
  textureKey: "courier-clean-drive",
  path: "/assets/game/vehicles/veh-001-courier-clean-drive-v6.png",
  frameWidth: 208,
  frameHeight: 160,
  canvasHeight: 160,
  originPixelX: 104,
  originPixelY: 152,
  textureScale: 0.5,
  collision: { x: 16, y: 76, width: 176, height: 68 },
});
const PLAYER_DRIVE_ANIMATION = "courier-clean-drive-loop";
const PLAYER_INTRO_IDLE_ASSET = Object.freeze({
  textureKey: "courier-clean-intro-idle",
  path: "/assets/game/vehicles/veh-001-courier-clean-intro-idle-v1.png",
  frameWidth: 208,
  frameHeight: 160,
});
const PLAYER_INTRO_IDLE_ANIMATION = "courier-clean-intro-idle-loop";

const HUD_ASSETS = Object.freeze({
  title: {
    textureKey: "hud-game-title-v1",
    path: "/assets/game/ui/ui-009-game-title-v1.png",
    x: GAME_VIEWPORT.width / 2,
    y: 38,
  },
  hearts: {
    textureKey: "hud-life-heart-v1",
    path: "/assets/game/ui/ico-001-life-heart-v1.png",
    frameWidth: 20,
    frameHeight: 18,
    frameFull: 0,
    frameEmpty: 1,
  },
  progress: {
    textureKey: "hud-progress-bar-v1",
    path: "/assets/game/ui/ui-003-progress-bar-v1.png",
    x: 18,
    y: 134,
    fillX: 20,
    fillCenterY: 142,
    fillWidth: GAME_VIEWPORT.width - 40,
    fillHeight: 8,
  },
  controls: {
    textureKey: "hud-touch-controls-v1",
    path: "/assets/game/ui/ui-004-touch-controls-v1.png",
    frameWidth: 76,
    frameHeight: 48,
    displayScale: 1.5,
    upX: 111,
    downX: 249,
    y: 572,
  },
  panel: {
    textureKey: "hud-control-panel-v1",
    path: "/assets/game/ui/ui-008-control-panel-v1.png",
    x: 0,
    y: 522,
  },
});

const INTRO_ASSETS = Object.freeze({
  callout: {
    textureKey: "intro-callout-v1",
    path: "/assets/game/ui/ui-013-intro-callout-v1.png",
    x: 16,
    y: 154,
  },
  tap: {
    textureKey: "intro-tap-v1",
    path: "/assets/game/ui/ui-014-intro-tap-v1.png",
    frameWidth: 112,
    frameHeight: 36,
    x: 180,
    y: 354,
  },
});

const RENDER_DEPTH = Object.freeze({
  environmentFront: 9,
  obstacleBase: 18,
  playerBase: 20,
  hud: 40,
  controls: 50,
  intro: 80,
  overlay: 100,
});

const OBSTACLE_ASSETS: Readonly<Record<ObstacleKind, ObstacleAssetSpec>> = {
  "pink-hatchback": {
    textureKey: "obstacle-pink-hatchback",
    path: "/assets/game/vehicles/obs-001-pink-hatchback-drive-v2.png",
    frameWidth: 80,
    frameHeight: 56,
    driveAnimationKey: "obstacle-pink-hatchback-drive-loop",
    canvasHeight: 56,
    originPixelX: 40,
    originPixelY: 52,
    collision: { x: 6, y: 27, width: 68, height: 24 },
    visualScaleMultiplier:
      OBSTACLE_VISUAL_SCALE_MULTIPLIERS["pink-hatchback"],
  },
  "yellow-sedan": {
    textureKey: "obstacle-yellow-sedan",
    path: "/assets/game/vehicles/obs-002-yellow-sedan-drive-v2.png",
    frameWidth: 88,
    frameHeight: 56,
    driveAnimationKey: "obstacle-yellow-sedan-drive-loop",
    canvasHeight: 56,
    originPixelX: 44,
    originPixelY: 52,
    collision: { x: 6, y: 30, width: 76, height: 21 },
    visualScaleMultiplier:
      OBSTACLE_VISUAL_SCALE_MULTIPLIERS["yellow-sedan"],
  },
  "green-wagon": {
    textureKey: "obstacle-green-wagon",
    path: "/assets/game/vehicles/obs-003-green-wagon-drive-v2.png",
    frameWidth: 84,
    frameHeight: 58,
    driveAnimationKey: "obstacle-green-wagon-drive-loop",
    canvasHeight: 58,
    originPixelX: 42,
    originPixelY: 54,
    collision: { x: 6, y: 29, width: 72, height: 24 },
    visualScaleMultiplier:
      OBSTACLE_VISUAL_SCALE_MULTIPLIERS["green-wagon"],
  },
};

export class GreyboxScene extends Phaser.Scene {
  private runState: RunState = createRunState();
  private readonly trafficSchedule: readonly ObstacleSpawn[] = createTrafficSchedule(
    GAMEPLAY_RULES.greyboxRunDurationMs,
  );
  private nextObstacleIndex = 0;
  private obstacles: ActiveObstacle[] = [];
  private player!: Phaser.GameObjects.Sprite;
  private lifeIcons: Phaser.GameObjects.Sprite[] = [];
  private progressFill!: Phaser.GameObjects.Rectangle;
  private progressHighlight!: Phaser.GameObjects.Rectangle;
  private introContainer!: Phaser.GameObjects.Container;
  private introTap!: Phaser.GameObjects.Sprite;
  private promptOverlay!: Phaser.GameObjects.Container;
  private promptTitle!: Phaser.GameObjects.Text;
  private promptBody!: Phaser.GameObjects.Text;
  private promptButton!: Phaser.GameObjects.Text;
  private pauseOverlay!: Phaser.GameObjects.Container;
  private environmentLayers: ActiveEnvironmentLayer[] = [];
  private environmentMode: ParallaxMovementMode = "route-loop";
  private prefersReducedMotion = false;
  private reducedMotionMediaQuery: MediaQueryList | null = null;
  private laneTweenActive = false;
  private bufferedDirection: LaneDirection | null = null;
  private displayedPhase: RunPhase = "ready";
  private isPaused = false;
  private playerIntroIdleAnimationActive = false;
  private introPulseTween: Phaser.Tweens.Tween | null = null;
  private introTransitionTween: Phaser.Tweens.Tween | null = null;
  private introTransitionActive = false;

  private readonly onIntroPointerDown = (): void => {
    this.beginIntroTransition();
  };

  private readonly onReducedMotionChange = (
    event: MediaQueryListEvent,
  ): void => {
    this.prefersReducedMotion = event.matches;
    if (!this.player || this.runState.phase !== "ready") {
      return;
    }
    if (event.matches) {
      this.stopPlayerIntroIdleAnimation(true);
      this.stopIntroPulseTween(true);
    } else if (!this.introTransitionActive) {
      this.startPlayerIntroIdleAnimation();
      this.startIntroPulseTween();
    }
  };

  public constructor() {
    super("greybox");
  }

  public preload(): void {
    for (const layer of ENVIRONMENT_PARALLAX.layers) {
      this.load.image(layer.textureKey, layer.runtimePath);
    }
    this.load.spritesheet(PLAYER_ASSET.textureKey, PLAYER_ASSET.path, {
      frameWidth: PLAYER_ASSET.frameWidth,
      frameHeight: PLAYER_ASSET.frameHeight,
    });
    this.load.spritesheet(
      PLAYER_INTRO_IDLE_ASSET.textureKey,
      PLAYER_INTRO_IDLE_ASSET.path,
      {
        frameWidth: PLAYER_INTRO_IDLE_ASSET.frameWidth,
        frameHeight: PLAYER_INTRO_IDLE_ASSET.frameHeight,
      },
    );
    for (const asset of Object.values(OBSTACLE_ASSETS)) {
      this.load.spritesheet(asset.textureKey, asset.path, {
        frameWidth: asset.frameWidth,
        frameHeight: asset.frameHeight,
      });
    }
    this.load.spritesheet(HUD_ASSETS.hearts.textureKey, HUD_ASSETS.hearts.path, {
      frameWidth: HUD_ASSETS.hearts.frameWidth,
      frameHeight: HUD_ASSETS.hearts.frameHeight,
    });
    this.load.image(HUD_ASSETS.progress.textureKey, HUD_ASSETS.progress.path);
    this.load.spritesheet(
      HUD_ASSETS.controls.textureKey,
      HUD_ASSETS.controls.path,
      {
        frameWidth: HUD_ASSETS.controls.frameWidth,
        frameHeight: HUD_ASSETS.controls.frameHeight,
      },
    );
    this.load.image(HUD_ASSETS.panel.textureKey, HUD_ASSETS.panel.path);
    this.load.image(HUD_ASSETS.title.textureKey, HUD_ASSETS.title.path);
    this.load.image(
      INTRO_ASSETS.callout.textureKey,
      INTRO_ASSETS.callout.path,
    );
    this.load.spritesheet(
      INTRO_ASSETS.tap.textureKey,
      INTRO_ASSETS.tap.path,
      {
        frameWidth: INTRO_ASSETS.tap.frameWidth,
        frameHeight: INTRO_ASSETS.tap.frameHeight,
      },
    );
  }

  public create(): void {
    this.runState = createRunState();
    this.nextObstacleIndex = 0;
    this.obstacles = [];
    this.displayedPhase = "ready";
    this.isPaused = false;
    this.environmentMode = ENVIRONMENT_PARALLAX.route.mode;
    this.configureReducedMotion();

    this.cameras.main
      .setOrigin(0, 0)
      .setZoom(GAME_RENDER_SCALE)
      .setRoundPixels(true)
      .setScroll(0, 0);

    this.textures
      .get(PLAYER_ASSET.textureKey)
      .setFilter(Phaser.Textures.FilterMode.NEAREST);
    this.textures
      .get(PLAYER_INTRO_IDLE_ASSET.textureKey)
      .setFilter(Phaser.Textures.FilterMode.NEAREST);
    for (const layer of ENVIRONMENT_PARALLAX.layers) {
      this.textures
        .get(layer.textureKey)
        .setFilter(Phaser.Textures.FilterMode.NEAREST);
    }
    for (const asset of Object.values(OBSTACLE_ASSETS)) {
      this.textures
        .get(asset.textureKey)
        .setFilter(Phaser.Textures.FilterMode.NEAREST);
    }
    for (const textureKey of [
      HUD_ASSETS.title.textureKey,
      HUD_ASSETS.hearts.textureKey,
      HUD_ASSETS.progress.textureKey,
      HUD_ASSETS.controls.textureKey,
      HUD_ASSETS.panel.textureKey,
      INTRO_ASSETS.callout.textureKey,
    ]) {
      this.textures
        .get(textureKey)
        .setFilter(Phaser.Textures.FilterMode.NEAREST);
    }
    this.textures
      .get(INTRO_ASSETS.tap.textureKey)
      .setFilter(Phaser.Textures.FilterMode.LINEAR);
    this.ensurePlayerDriveAnimation();
    this.ensurePlayerIntroIdleAnimation();
    this.ensureObstacleDriveAnimations();

    this.createEnvironment();
    this.createHud();
    this.player = this.createPlayer();
    this.createTouchControls();
    this.createIntroOverlay();
    this.createOutcomeOverlay();
    this.createPauseOverlay();
    this.bindKeyboard();
    this.bindIntroPointerInput();
    this.updateHud();
    this.startPlayerIntroIdleAnimation();
    this.startIntroPulseTween();

    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.unbindIntroPointerInput();
      this.stopIntroTransitionTween(false);
      this.stopIntroPulseTween(false);
      this.stopPlayerIntroIdleAnimation(false);
      this.reducedMotionMediaQuery?.removeEventListener(
        "change",
        this.onReducedMotionChange,
      );
      this.reducedMotionMediaQuery = null;
    });
  }

  public update(_time: number, delta: number): void {
    if (this.runState.phase !== "playing" || this.isPaused) {
      return;
    }

    const previousPhase = this.runState.phase;
    this.runState = advanceRun(this.runState, delta);
    this.animateEnvironment(delta);
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

  private createEnvironment(): void {
    this.cameras.main.setBackgroundColor(COLORS.sky);

    this.environmentLayers = ENVIRONMENT_PARALLAX.layers.map((layer) => {
      const sprite = this.add
        .tileSprite(
          layer.position.x,
          layer.position.y,
          GAME_VIEWPORT.width,
          layer.contentCanvas.height * layer.tileScale.y,
          layer.textureKey,
        )
        .setOrigin(0, 0)
        .setTileScale(layer.tileScale.x, layer.tileScale.y)
        .setDepth(layer.depth);
      return {
        sprite,
        spec: layer,
        arrivalEndOffsetTexturePx: 0,
      };
    });
  }

  private animateEnvironment(delta: number): void {
    for (const layer of this.environmentLayers) {
      const texturePixelsPerSecond =
        this.getEnvironmentTextureSpeed(layer.spec);
      layer.sprite.tilePositionX = advanceParallaxOffset({
        currentOffsetTexturePx: layer.sprite.tilePositionX,
        texturePixelsPerSecond,
        deltaMs: delta,
        mode: this.environmentMode,
        loopPeriodTexturePx: layer.spec.textureCanvas.width,
        arrivalEndOffsetTexturePx: layer.arrivalEndOffsetTexturePx,
      });
    }
  }

  private resetEnvironment(): void {
    this.environmentMode = ENVIRONMENT_PARALLAX.route.mode;
    for (const layer of this.environmentLayers) {
      layer.sprite.tilePositionX = 0;
      layer.arrivalEndOffsetTexturePx = 0;
    }
  }

  private setEnvironmentMode(mode: ParallaxMovementMode): void {
    this.environmentMode = mode;
    if (mode !== "arrival-finite") {
      return;
    }

    for (const layer of this.environmentLayers) {
      layer.arrivalEndOffsetTexturePx = layer.sprite.tilePositionX;
    }
  }

  private getEnvironmentTextureSpeed(layer: EnvironmentLayerSpec): number {
    if (this.prefersReducedMotion && layer.reducedMotion === "freeze") {
      return 0;
    }

    const displaySpeed =
      ENVIRONMENT_PARALLAX.route.baseDisplaySpeedPxPerSecond *
      layer.speedMultiplier;
    return displaySpeed / layer.tileScale.x;
  }

  private configureReducedMotion(): void {
    this.reducedMotionMediaQuery?.removeEventListener(
      "change",
      this.onReducedMotionChange,
    );
    this.reducedMotionMediaQuery = null;
    this.prefersReducedMotion = false;

    if (typeof window === "undefined" || !window.matchMedia) {
      return;
    }

    this.reducedMotionMediaQuery = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    );
    this.prefersReducedMotion = this.reducedMotionMediaQuery.matches;
    this.reducedMotionMediaQuery.addEventListener(
      "change",
      this.onReducedMotionChange,
    );
  }

  private createHud(): void {
    this.add
      .image(HUD_ASSETS.title.x, HUD_ASSETS.title.y, HUD_ASSETS.title.textureKey)
      .setOrigin(0.5)
      .setDepth(RENDER_DEPTH.hud)
      .setScrollFactor(0);

    this.lifeIcons = Array.from(
      { length: GAMEPLAY_RULES.startingLives },
      (_, index) =>
        this.add
          .sprite(
            18 + index * (HUD_ASSETS.hearts.frameWidth + 2),
            106,
            HUD_ASSETS.hearts.textureKey,
            HUD_ASSETS.hearts.frameFull,
          )
          .setOrigin(0, 0)
          .setDepth(RENDER_DEPTH.hud)
          .setScrollFactor(0),
    );

    this.add
      .image(
        HUD_ASSETS.progress.x,
        HUD_ASSETS.progress.y,
        HUD_ASSETS.progress.textureKey,
      )
      .setOrigin(0, 0)
      .setDepth(RENDER_DEPTH.hud)
      .setScrollFactor(0);
    this.progressFill = this.add
      .rectangle(
        HUD_ASSETS.progress.fillX,
        HUD_ASSETS.progress.fillCenterY,
        0,
        HUD_ASSETS.progress.fillHeight,
        0xffef5c,
        1,
      )
      .setOrigin(0, 0.5)
      .setDepth(RENDER_DEPTH.hud + 1)
      .setScrollFactor(0);
    this.progressHighlight = this.add
      .rectangle(
        HUD_ASSETS.progress.fillX,
        HUD_ASSETS.progress.fillCenterY,
        2,
        6,
        0xffffff,
        1,
      )
      .setOrigin(0, 0.5)
      .setDepth(RENDER_DEPTH.hud + 2)
      .setVisible(false)
      .setScrollFactor(0);
  }

  private ensurePlayerDriveAnimation(): void {
    if (this.anims.exists(PLAYER_DRIVE_ANIMATION)) {
      return;
    }

    this.anims.create({
      key: PLAYER_DRIVE_ANIMATION,
      frames: this.anims.generateFrameNumbers(PLAYER_ASSET.textureKey, {
        start: 0,
        end: 3,
      }),
      frameRate: 9,
      repeat: -1,
    });
  }

  private ensurePlayerIntroIdleAnimation(): void {
    if (this.anims.exists(PLAYER_INTRO_IDLE_ANIMATION)) {
      return;
    }

    this.anims.create({
      key: PLAYER_INTRO_IDLE_ANIMATION,
      frames: this.anims.generateFrameNumbers(PLAYER_INTRO_IDLE_ASSET.textureKey, {
        start: 0,
        end: 3,
      }),
      frameRate: 9,
      repeat: -1,
    });
  }

  private ensureObstacleDriveAnimations(): void {
    for (const asset of Object.values(OBSTACLE_ASSETS)) {
      if (this.anims.exists(asset.driveAnimationKey)) {
        continue;
      }

      this.anims.create({
        key: asset.driveAnimationKey,
        frames: this.anims.generateFrameNumbers(asset.textureKey, {
          start: 0,
          end: 3,
        }),
        frameRate: 7,
        repeat: -1,
      });
    }
  }

  private createPlayer(): Phaser.GameObjects.Sprite {
    const lane = this.runState.lane;
    return this.add
      .sprite(PLAYER_X, LANE_BASELINES[lane], PLAYER_ASSET.textureKey, 0)
      .setOrigin(0.5, PLAYER_ASSET.originPixelY / PLAYER_ASSET.canvasHeight)
      .setScale(LANE_VISUAL_SCALES[lane] * PLAYER_ASSET.textureScale)
      .setDepth(RENDER_DEPTH.playerBase + lane);
  }

  private createTouchControls(): void {
    this.add
      .image(
        HUD_ASSETS.panel.x,
        HUD_ASSETS.panel.y,
        HUD_ASSETS.panel.textureKey,
      )
      .setOrigin(0, 0)
      .setDepth(RENDER_DEPTH.controls - 1)
      .setScrollFactor(0);

    const up = this.createControlButton(HUD_ASSETS.controls.upX, HUD_ASSETS.controls.y, -1);
    const down = this.createControlButton(HUD_ASSETS.controls.downX, HUD_ASSETS.controls.y, 1);
    up.setDepth(RENDER_DEPTH.controls).setScrollFactor(0);
    down.setDepth(RENDER_DEPTH.controls).setScrollFactor(0);
  }

  private createControlButton(
    x: number,
    y: number,
    direction: LaneDirection,
  ): Phaser.GameObjects.Sprite {
    const frame = direction === -1 ? 0 : 2;
    const button = this.add
      .sprite(x, y, HUD_ASSETS.controls.textureKey, frame)
      .setScale(HUD_ASSETS.controls.displayScale)
      .setInteractive({ useHandCursor: true });

    button.on("pointerdown", () => {
      button.setFrame(frame + 1);
      this.requestLaneMove(direction);
    });
    button.on("pointerup", () => button.setFrame(frame));
    button.on("pointerout", () => button.setFrame(frame));
    return button.setScrollFactor(0);
  }

  private createIntroOverlay(): void {
    const callout = this.add
      .image(
        INTRO_ASSETS.callout.x,
        INTRO_ASSETS.callout.y,
        INTRO_ASSETS.callout.textureKey,
      )
      .setOrigin(0, 0);
    this.introTap = this.add
      .sprite(
        INTRO_ASSETS.tap.x,
        INTRO_ASSETS.tap.y,
        INTRO_ASSETS.tap.textureKey,
        0,
      )
      .setOrigin(0.5)
      .setScale(1);

    this.introContainer = this.add.container(0, 0, [callout, this.introTap]);
    this.introContainer
      .setDepth(RENDER_DEPTH.intro)
      .setScrollFactor(0);
  }

  private createOutcomeOverlay(): void {
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
      .text(180, 260, "ORDER DELIVERED!", {
        align: "center",
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "20px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);
    this.promptBody = this.add
      .text(180, 312, "Greybox route complete.\nPrize roulette comes later.", {
        align: "center",
        color: "#34344f",
        fontFamily: "monospace",
        fontSize: "13px",
        lineSpacing: 7,
      })
      .setOrigin(0.5);
    this.promptButton = this.add
      .text(180, 382, "PLAY AGAIN", {
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
    this.promptOverlay
      .setDepth(RENDER_DEPTH.overlay)
      .setScrollFactor(0)
      .setVisible(false);
  }

  private startPlayerIntroIdleAnimation(): void {
    if (
      this.prefersReducedMotion ||
      this.runState.phase !== "ready" ||
      this.playerIntroIdleAnimationActive
    ) {
      return;
    }

    this.playerIntroIdleAnimationActive = true;
    this.player
      .setTexture(PLAYER_INTRO_IDLE_ASSET.textureKey, 0)
      .play(PLAYER_INTRO_IDLE_ANIMATION);
  }

  private stopPlayerIntroIdleAnimation(restoreBaseline: boolean): void {
    this.playerIntroIdleAnimationActive = false;
    this.player?.stop().setFrame(0);
    if (restoreBaseline) {
      this.player.setY(LANE_BASELINES[this.runState.lane]);
    }
  }

  private startIntroPulseTween(): void {
    if (
      this.prefersReducedMotion ||
      this.runState.phase !== "ready" ||
      this.introTransitionActive ||
      this.introPulseTween
    ) {
      return;
    }

    this.introTap.setFrame(0).setScale(1);
    this.introPulseTween = this.tweens.add({
      targets: this.introTap,
      scaleX: 1.06,
      scaleY: 1.06,
      duration: 500,
      ease: "Sine.InOut",
      yoyo: true,
      repeat: -1,
    });
  }

  private stopIntroPulseTween(restoreVisual: boolean): void {
    const pulseTween = this.introPulseTween;
    this.introPulseTween = null;
    pulseTween?.stop();
    if (restoreVisual && this.introTap) {
      this.introTap.setFrame(0).setScale(1);
    }
  }

  private bindIntroPointerInput(): void {
    this.input.on("pointerdown", this.onIntroPointerDown, this);
  }

  private unbindIntroPointerInput(): void {
    this.input.off("pointerdown", this.onIntroPointerDown, this);
  }

  private beginIntroTransition(): void {
    if (
      this.runState.phase !== "ready" ||
      this.isPaused ||
      this.introTransitionActive
    ) {
      return;
    }

    this.introTransitionActive = true;
    this.unbindIntroPointerInput();
    this.stopIntroPulseTween(true);

    const transition = { phase: 0 };
    this.introTransitionTween = this.tweens.add({
      targets: transition,
      phase: 3,
      duration: 1_000,
      ease: "Linear",
      onUpdate: () => {
        const boundedPhase = Math.min(2.999_999, transition.phase);
        const cycle = Math.floor(boundedPhase);
        const cycleProgress = boundedPhase - cycle;
        const transitionFrame = cycle === 0 ? 1 : cycle === 1 ? 2 : 0;
        this.introTap.setFrame(transitionFrame);

        if (this.prefersReducedMotion) {
          this.introTap.setScale(1);
          return;
        }

        const sinePulse = (1 - Math.cos(cycleProgress * Math.PI * 2)) / 2;
        this.introTap.setScale(1 + sinePulse * 0.06);
      },
      onComplete: () => {
        this.introTransitionTween = null;
        this.completeIntroTransition();
      },
    });
  }

  private completeIntroTransition(): void {
    if (!this.introTransitionActive || this.runState.phase !== "ready") {
      return;
    }

    this.stopPlayerIntroIdleAnimation(true);
    this.introTap.setFrame(0).setScale(1);
    this.introContainer.setVisible(false);
    this.runState = startRun(this.runState);
    this.displayedPhase = "playing";
    this.introTransitionActive = false;
    this.player
      .setTexture(PLAYER_ASSET.textureKey, 0)
      .play(PLAYER_DRIVE_ANIMATION);
    this.updateHud();
  }

  private stopIntroTransitionTween(restoreVisual: boolean): void {
    const transitionTween = this.introTransitionTween;
    this.introTransitionTween = null;
    transitionTween?.stop();
    this.introTransitionActive = false;
    if (restoreVisual && this.introTap) {
      this.introTap.setFrame(0).setScale(1);
    }
  }

  private createPauseOverlay(): void {
    const shade = this.add
      .rectangle(
        GAME_VIEWPORT.width / 2,
        GAME_VIEWPORT.height / 2,
        GAME_VIEWPORT.width,
        GAME_VIEWPORT.height,
        COLORS.navy,
        0.78,
      )
      .setInteractive();
    const panelShadow = this.add.rectangle(184, 326, 288, 226, 0x982add, 1);
    const panel = this.add.rectangle(180, 320, 288, 226, COLORS.cream, 1);
    panel.setStrokeStyle(5, COLORS.pink, 1);
    const title = this.add
      .text(180, 248, "ПАУЗА", {
        align: "center",
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "22px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);
    const continueButton = this.createPauseMenuButton(
      310,
      "ПРОДОЛЖИТЬ",
      () => this.resumeRun(),
    );
    const restartButton = this.createPauseMenuButton(
      370,
      "ЗАНОВО",
      () => this.restartPausedRun(),
    );

    this.pauseOverlay = this.add.container(0, 0, [
      shade,
      panelShadow,
      panel,
      title,
      continueButton,
      restartButton,
    ]);
    this.pauseOverlay
      .setDepth(RENDER_DEPTH.overlay + 10)
      .setScrollFactor(0)
      .setVisible(false);
  }

  private createPauseMenuButton(
    y: number,
    label: string,
    onActivate: () => void,
  ): Phaser.GameObjects.Container {
    const width = 168;
    const height = 44;
    const shadow = this.add.rectangle(3, 3, width, 40, 0x982add, 1);
    const outline = this.add.rectangle(0, 0, width, 40, COLORS.navy, 1);
    const face = this.add.rectangle(0, -2, width - 8, 32, 0xffef5c, 1);
    const text = this.add
      .text(0, -2, label, {
        align: "center",
        color: "#1d1d1b",
        fontFamily: "monospace",
        fontSize: "14px",
        fontStyle: "bold",
      })
      .setOrigin(0.5);
    const button = this.add.container(180, y, [shadow, outline, face, text]);
    let pressed = false;

    const setPressed = (value: boolean): void => {
      pressed = value;
      face.setFillStyle(value ? 0xdad73d : 0xffef5c, 1);
      face.setY(value ? 1 : -2);
      text.setY(value ? 1 : -2);
    };

    button
      .setSize(width, height)
      .setInteractive({ useHandCursor: true })
      .on("pointerdown", () => setPressed(true))
      .on("pointerup", () => {
        if (!pressed) {
          return;
        }
        setPressed(false);
        onActivate();
      })
      .on("pointerout", () => setPressed(false));
    return button;
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
    keyboard.on("keydown-P", () => this.togglePause());
    keyboard.on("keydown-ESC", () => this.togglePause());
  }

  private activateOverlayAction(): void {
    if (this.isPaused) {
      return;
    }

    if (this.runState.phase === "ready") {
      this.beginIntroTransition();
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
    if (this.runState.phase !== "playing" || this.isPaused) {
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
    this.player.setDepth(RENDER_DEPTH.playerBase + this.runState.lane);
    this.tweens.add({
      targets: this.player,
      y: LANE_BASELINES[this.runState.lane],
      scaleX:
        LANE_VISUAL_SCALES[this.runState.lane] * PLAYER_ASSET.textureScale,
      scaleY:
        LANE_VISUAL_SCALES[this.runState.lane] * PLAYER_ASSET.textureScale,
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
    const asset = OBSTACLE_ASSETS[obstacle.kind];
    const sprite = this.add.sprite(
      OBSTACLE_SPAWN_X,
      LANE_BASELINES[obstacle.lane],
      asset.textureKey,
      0,
    );
    sprite.setOrigin(0.5, asset.originPixelY / asset.canvasHeight);
    sprite.setScale(
      LANE_VISUAL_SCALES[obstacle.lane] * asset.visualScaleMultiplier,
    );
    sprite.setDepth(RENDER_DEPTH.obstacleBase + obstacle.lane);
    sprite.play(asset.driveAnimationKey);
    this.obstacles.push({
      sprite,
      lane: obstacle.lane,
      originPixelX: asset.originPixelX,
      originPixelY: asset.originPixelY,
      collision: asset.collision,
      collisionScaleRatio:
        VEHICLE_COLLISION_TO_VISUAL_RATIO / asset.visualScaleMultiplier,
    });
  }

  private moveObstacles(delta: number): void {
    const distance =
      GAMEPLAY_RULES.obstacleSpeedPxPerSecond * (delta / 1_000);
    const remaining: ActiveObstacle[] = [];

    for (const obstacle of this.obstacles) {
      obstacle.sprite.x -= distance;
      if (obstacle.sprite.x + obstacle.sprite.displayWidth / 2 < 0) {
        obstacle.sprite.destroy();
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

    const playerBounds = this.getSpriteCollisionBounds(
      this.player,
      PLAYER_ASSET.originPixelX,
      PLAYER_ASSET.originPixelY,
      PLAYER_ASSET.collision,
      VEHICLE_COLLISION_TO_VISUAL_RATIO,
    );
    const collidedIndex = this.obstacles.findIndex((obstacle) =>
      Phaser.Geom.Intersects.RectangleToRectangle(
        playerBounds,
        this.getSpriteCollisionBounds(
          obstacle.sprite,
          obstacle.originPixelX,
          obstacle.originPixelY,
          obstacle.collision,
          obstacle.collisionScaleRatio,
        ),
      ),
    );

    if (collidedIndex === -1) {
      return;
    }

    const [collided] = this.obstacles.splice(collidedIndex, 1);
    if (!collided) {
      return;
    }
    collided.sprite.destroy();
    this.runState = registerHit(this.runState);
    if (!this.prefersReducedMotion) {
      this.cameras.main.shake(110, 0.008);
    }
    this.updateHud();

    if (this.runState.phase === "defeated") {
      this.showPhase("defeated");
    }
  }

  private updateHud(): void {
    for (const [index, icon] of this.lifeIcons.entries()) {
      icon.setFrame(
        index < this.runState.lives
          ? HUD_ASSETS.hearts.frameFull
          : HUD_ASSETS.hearts.frameEmpty,
      );
    }

    const progress = getRunProgress(this.runState);
    const progressWidth = Math.max(
      0,
      HUD_ASSETS.progress.fillWidth * progress,
    );
    this.progressFill.width = progressWidth;
    this.progressHighlight
      .setVisible(progressWidth >= 2)
      .setX(HUD_ASSETS.progress.fillX + Math.max(0, progressWidth - 2));
  }

  private showPhase(phase: RunPhase): void {
    if (this.displayedPhase === phase) {
      return;
    }
    this.displayedPhase = phase;

    if (phase === "delivered") {
      this.setEnvironmentMode("arrival-finite");
      this.player.stop();
      this.player.setFrame(0);
      this.clearObstacles();
      this.promptTitle.setText("ORDER DELIVERED!");
      this.promptBody.setText("Greybox route complete.\nPrize roulette comes later.");
      this.promptButton.setText("PLAY AGAIN");
      this.promptOverlay.setVisible(true);
    } else if (phase === "defeated") {
      this.player.stop();
      this.player.setFrame(0);
      this.promptTitle.setText("DELIVERY FAILED");
      this.promptBody.setText("No lives left.\nTry the route again.");
      this.promptButton.setText("RETRY");
      this.promptOverlay.setVisible(true);
    }
  }

  private resetRun(): void {
    this.isPaused = false;
    this.pauseOverlay.setVisible(false);
    this.tweens.resumeAll();
    this.tweens.killTweensOf(this.player);
    this.playerIntroIdleAnimationActive = false;
    this.clearObstacles();
    this.runState = retryRun(this.runState);
    this.nextObstacleIndex = 0;
    this.laneTweenActive = false;
    this.bufferedDirection = null;
    this.displayedPhase = "playing";
    this.player.setPosition(PLAYER_X, LANE_BASELINES[this.runState.lane]);
    this.player.setScale(
      LANE_VISUAL_SCALES[this.runState.lane] * PLAYER_ASSET.textureScale,
    );
    this.player.setDepth(RENDER_DEPTH.playerBase + this.runState.lane);
    this.player.setAlpha(1);
    this.player
      .setTexture(PLAYER_ASSET.textureKey, 0)
      .play(PLAYER_DRIVE_ANIMATION);
    this.resetEnvironment();
    this.promptOverlay.setVisible(false);
    this.updateHud();
  }

  private togglePause(): void {
    if (this.runState.phase !== "playing") {
      return;
    }
    if (this.isPaused) {
      this.resumeRun();
    } else {
      this.pauseRun();
    }
  }

  private pauseRun(): void {
    if (this.runState.phase !== "playing" || this.isPaused) {
      return;
    }
    this.isPaused = true;
    this.tweens.pauseAll();
    this.player.anims.pause();
    for (const obstacle of this.obstacles) {
      obstacle.sprite.anims.pause();
    }
    this.pauseOverlay.setVisible(true);
  }

  private resumeRun(): void {
    if (!this.isPaused) {
      return;
    }
    this.isPaused = false;
    this.pauseOverlay.setVisible(false);
    this.tweens.resumeAll();
    this.player.anims.resume();
    for (const obstacle of this.obstacles) {
      obstacle.sprite.anims.resume();
    }
  }

  private restartPausedRun(): void {
    if (!this.isPaused) {
      return;
    }
    this.isPaused = false;
    this.pauseOverlay.setVisible(false);
    this.tweens.resumeAll();
    this.resetRun();
  }

  private clearObstacles(): void {
    for (const obstacle of this.obstacles) {
      obstacle.sprite.destroy();
    }
    this.obstacles = [];
  }

  private getSpriteCollisionBounds(
    sprite: Phaser.GameObjects.Image,
    originPixelX: number,
    originPixelY: number,
    collision: CollisionSpec,
    collisionScaleRatio: number,
  ): Phaser.Geom.Rectangle {
    const visualX =
      sprite.x + (collision.x - originPixelX) * sprite.scaleX;
    const visualY =
      sprite.y + (collision.y - originPixelY) * sprite.scaleY;
    const visualWidth = collision.width * sprite.scaleX;
    const visualHeight = collision.height * sprite.scaleY;
    const collisionWidth = visualWidth * collisionScaleRatio;
    const collisionHeight = visualHeight * collisionScaleRatio;
    return new Phaser.Geom.Rectangle(
      visualX + (visualWidth - collisionWidth) / 2,
      visualY + (visualHeight - collisionHeight) / 2,
      collisionWidth,
      collisionHeight,
    );
  }
}
