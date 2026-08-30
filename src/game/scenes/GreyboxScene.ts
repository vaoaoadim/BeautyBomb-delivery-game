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
  advanceDeliveryPresentationPhase,
  DELIVERY_FINALE,
  type DeliveryPresentationPhase,
} from "../content/deliveryFinale";
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
import { canPlayGameplayMusic } from "../systems/gameplayMusic";
import { requestPortfolioEmbedClose } from "../../integration/portfolioEmbed";

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

interface GameplayMusic extends Phaser.Sound.BaseSound {
  mute: boolean;
}

const COLORS = Object.freeze({
  sky: 0x73e6f7,
  cream: 0xf8f1df,
  cyan: 0x16c6dc,
  pink: 0xff4d91,
  navy: 0x17162f,
  danger: 0xff5b5b,
  brandRed: 0xe30613,
});

const PLAYER_X = 74;
const OBSTACLE_SPAWN_X = GAME_VIEWPORT.width + 72;
const PLAYER_ASSET = Object.freeze({
  textureKey: "courier-clean-drive",
  path: "/assets/game/vehicles/veh-001-courier-clean-drive-v7.png",
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
  path: "/assets/game/vehicles/veh-001-courier-clean-intro-idle-v2.png",
  frameWidth: 208,
  frameHeight: 160,
});
const PLAYER_INTRO_IDLE_ANIMATION = "courier-clean-intro-idle-loop";

const GAMEPLAY_AUDIO = Object.freeze({
  music: {
    textureKey: "bgm-gameplay-v1",
    path: "/assets/game/audio/bgm-gameplay-v1.mp3",
    volume: 0.35,
  },
});

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
    textureKey: "hud-touch-controls-v2",
    path: "/assets/game/ui/ui-004-touch-controls-v2.png",
    frameWidth: 76,
    frameHeight: 48,
    displayScale: 1.5,
    downX: 111,
    upX: 249,
    y: 572,
  },
  pause: {
    textureKey: "hud-pause-button-v2",
    path: "/assets/game/ui/ui-010-pause-button-v2.png",
    frameWidth: 32,
    frameHeight: 32,
    x: 332,
    y: 32,
    hitAreaSize: 44,
  },
  sound: {
    textureKey: "hud-sound-button-v2",
    path: "/assets/game/ui/ui-012-sound-button-v2.png",
    frameWidth: 32,
    frameHeight: 32,
    x: 332,
    y: 78,
    hitAreaSize: 44,
  },
});

const EXIT_CONTROL = Object.freeze({
  className: "game-exit-stub",
  ariaLabel: "Закрыть игру",
});

const CONTROL_PANEL_COBBLESTONE = Object.freeze({
  textureKey: "environment-control-panel-cobblestone-v1",
  path: "/assets/game/environment/env-010-control-panel-cobblestone-v1.png",
  x: 0,
  y: 520,
  width: GAME_VIEWPORT.width,
  height: 122,
  textureWidth: 512,
  texturePixelsPerSecond: 92.16,
});

const INTRO_ASSETS = Object.freeze({
  callout: {
    textureKey: "intro-callout-v3",
    path: "/assets/game/ui/ui-013-intro-callout-v3.png",
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

const PAUSE_ASSETS = Object.freeze({
  callout: {
    textureKey: "pause-callout-v2",
    path: "/assets/game/ui/ui-015-pause-callout-v2.png",
    x: 180,
    y: 318,
  },
});

const DEFEAT_ASSETS = Object.freeze({
  callout: {
    textureKey: "defeat-callout-v2",
    path: "/assets/game/ui/ui-006-defeat-callout-v2.png",
    x: 180,
    y: 318,
  },
});

const DELIVERY_ASSETS = Object.freeze({
  destinationCity: {
    textureKey: "delivery-destination-city-v3",
    path: "/assets/game/environment/env-009-delivery-destination-city-v3.png",
  },
  girl: {
    textureKey: "delivery-girl-lowpoly-v1",
    path: "/assets/game/characters/chr-003-lowpoly-recipient-v1.png",
  },
  callout: {
    textureKey: "delivery-callout-v5",
    path: "/assets/game/ui/ui-016-delivery-callout-v5.png",
  },
  claim: {
    textureKey: "delivery-claim-v1",
    path: "/assets/game/ui/ui-017-claim-v1.png",
    frameWidth: 168,
    frameHeight: 36,
  },
  product: {
    textureKey: "delivery-product-v3",
    path: "/assets/game/products/prd-003-delivery-transfer-v3.png",
  },
  rewardCoupon: {
    textureKey: "delivery-reward-coupon-v7",
    path: "/assets/game/ui/ui-018-reward-coupon-v7.png",
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

const FINALE_FADE_TIMING = Object.freeze({
  fadeOutMs: 220,
  coveredHoldMs: 40,
  fadeInMs: 260,
});

const COUPON_CODE = "XQZ-20476";
const COUPON_POPUP_LAYOUT = Object.freeze({
  centerX: 180,
  centerY: 320,
  width: 332,
  height: 498,
  codeFieldX: 154,
  codeFieldY: 484,
  codeFieldWidth: 122,
  codeFieldHeight: 44,
  copyButtonX: 246,
  copyButtonY: 484,
  copyButtonSize: 44,
  copyButtonHitArea: 48,
  copyFeedbackY: 526,
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
  private promptPanel!: Phaser.GameObjects.Rectangle;
  private promptTitle!: Phaser.GameObjects.Text;
  private promptBody!: Phaser.GameObjects.Text;
  private promptButton!: Phaser.GameObjects.Text;
  private couponPanel!: Phaser.GameObjects.Container;
  private couponCopyButton!: Phaser.GameObjects.Container;
  private couponCopyIcon!: Phaser.GameObjects.Container;
  private couponCopyCheck!: Phaser.GameObjects.Container;
  private couponCopyFeedback!: Phaser.GameObjects.Text;
  private couponCopyResetTimer: Phaser.Time.TimerEvent | null = null;
  private couponCopyAccessibleButton: HTMLButtonElement | null = null;
  private couponCopyAnnouncement: HTMLSpanElement | null = null;
  private pauseOverlay!: Phaser.GameObjects.Container;
  private defeatOverlay!: Phaser.GameObjects.Container;
  private utilityControls: Phaser.GameObjects.Sprite[] = [];
  private exitControl: HTMLButtonElement | null = null;
  private soundControl: Phaser.GameObjects.Sprite | null = null;
  private soundMuteSlash: Phaser.GameObjects.Container | null = null;
  private gameplayMusic: GameplayMusic | null = null;
  private isMusicMuted = false;
  private musicPausedForVisibility = false;
  private musicPausedForEmbed = false;
  private environmentLayers: ActiveEnvironmentLayer[] = [];
  private controlPanelCobblestone!: Phaser.GameObjects.TileSprite;
  private controlPanelCobblestoneArrivalEndOffsetTexturePx = 0;
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
  private deliveryPhase: DeliveryPresentationPhase = "inactive";
  private deliveryPhaseElapsedMs = 0;
  private arrivalPlayerStart: { x: number; y: number; scale: number } = {
    x: PLAYER_X,
    y: LANE_BASELINES[1],
    scale: 1,
  };
  private deliveryGirl!: Phaser.GameObjects.Image;
  private deliveryCallout!: Phaser.GameObjects.Image;
  private deliveryClaim!: Phaser.GameObjects.Sprite;
  private deliveryProduct: Phaser.GameObjects.Image | null = null;
  private deliveryClaimPulseTween: Phaser.Tweens.Tween | null = null;
  private productTween: Phaser.Tweens.Tween | null = null;
  private confettiPieces: Phaser.GameObjects.Rectangle[] = [];
  private finaleFadeOverlay!: Phaser.GameObjects.Rectangle;
  private finaleFadeTween: Phaser.Tweens.Tween | null = null;
  private finaleFadeHoldTimer: Phaser.Time.TimerEvent | null = null;
  private finaleFadeActive = false;
  private claimInputBound = false;
  private rewardFlowInvoked = false;

  private readonly onIntroPointerDown = (): void => {
    this.beginIntroTransition();
  };

  private readonly onClaimPointerDown = (): void => {
    this.claimDeliveryReward();
  };

  private readonly onVisibilityChange = (): void => {
    if (typeof document === "undefined") {
      return;
    }

    if (document.hidden) {
      this.musicPausedForVisibility = this.pauseGameplayMusic();
      return;
    }

    if (!this.musicPausedForVisibility) {
      return;
    }

    this.musicPausedForVisibility = false;
    this.resumeGameplayMusic();
  };

  private readonly onPortfolioEmbedActivity = (active: boolean): void => {
    if (!active) {
      this.musicPausedForEmbed = this.pauseGameplayMusic();
      return;
    }

    if (!this.musicPausedForEmbed) {
      return;
    }

    this.musicPausedForEmbed = false;
    this.resumeGameplayMusic();
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
    this.load.image(
      CONTROL_PANEL_COBBLESTONE.textureKey,
      CONTROL_PANEL_COBBLESTONE.path,
    );
    this.load.image(HUD_ASSETS.title.textureKey, HUD_ASSETS.title.path);
    this.load.spritesheet(HUD_ASSETS.pause.textureKey, HUD_ASSETS.pause.path, {
      frameWidth: HUD_ASSETS.pause.frameWidth,
      frameHeight: HUD_ASSETS.pause.frameHeight,
    });
    this.load.spritesheet(HUD_ASSETS.sound.textureKey, HUD_ASSETS.sound.path, {
      frameWidth: HUD_ASSETS.sound.frameWidth,
      frameHeight: HUD_ASSETS.sound.frameHeight,
    });
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
    this.load.image(
      PAUSE_ASSETS.callout.textureKey,
      PAUSE_ASSETS.callout.path,
    );
    this.load.image(
      DEFEAT_ASSETS.callout.textureKey,
      DEFEAT_ASSETS.callout.path,
    );
    this.load.image(
      DELIVERY_ASSETS.destinationCity.textureKey,
      DELIVERY_ASSETS.destinationCity.path,
    );
    this.load.image(DELIVERY_ASSETS.girl.textureKey, DELIVERY_ASSETS.girl.path);
    this.load.image(
      DELIVERY_ASSETS.callout.textureKey,
      DELIVERY_ASSETS.callout.path,
    );
    this.load.spritesheet(
      DELIVERY_ASSETS.claim.textureKey,
      DELIVERY_ASSETS.claim.path,
      {
        frameWidth: DELIVERY_ASSETS.claim.frameWidth,
        frameHeight: DELIVERY_ASSETS.claim.frameHeight,
      },
    );
    this.load.image(
      DELIVERY_ASSETS.product.textureKey,
      DELIVERY_ASSETS.product.path,
    );
    this.load.image(
      DELIVERY_ASSETS.rewardCoupon.textureKey,
      DELIVERY_ASSETS.rewardCoupon.path,
    );
    this.load.audio(GAMEPLAY_AUDIO.music.textureKey, GAMEPLAY_AUDIO.music.path);
  }

  public create(): void {
    this.runState = createRunState();
    this.nextObstacleIndex = 0;
    this.obstacles = [];
    this.displayedPhase = "ready";
    this.isPaused = false;
    this.environmentMode = ENVIRONMENT_PARALLAX.route.mode;
    this.deliveryPhase = "inactive";
    this.deliveryPhaseElapsedMs = 0;
    this.rewardFlowInvoked = false;
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
      CONTROL_PANEL_COBBLESTONE.textureKey,
      HUD_ASSETS.pause.textureKey,
      HUD_ASSETS.sound.textureKey,
      INTRO_ASSETS.callout.textureKey,
      PAUSE_ASSETS.callout.textureKey,
      DEFEAT_ASSETS.callout.textureKey,
      DELIVERY_ASSETS.destinationCity.textureKey,
      DELIVERY_ASSETS.girl.textureKey,
      DELIVERY_ASSETS.callout.textureKey,
      DELIVERY_ASSETS.product.textureKey,
      DELIVERY_ASSETS.rewardCoupon.textureKey,
    ]) {
      this.textures
        .get(textureKey)
        .setFilter(Phaser.Textures.FilterMode.NEAREST);
    }
    this.textures
      .get(INTRO_ASSETS.tap.textureKey)
      .setFilter(Phaser.Textures.FilterMode.LINEAR);
    this.textures
      .get(DELIVERY_ASSETS.claim.textureKey)
      .setFilter(Phaser.Textures.FilterMode.LINEAR);
    this.ensurePlayerDriveAnimation();
    this.ensurePlayerIntroIdleAnimation();
    this.ensureObstacleDriveAnimations();
    this.createGameplayMusic();
    this.bindGameplayMusicVisibility();
    this.game.events.on(
      "portfolio-embed-activity",
      this.onPortfolioEmbedActivity,
    );

    this.createEnvironment();
    this.createHud();
    this.player = this.createPlayer();
    this.createDeliveryFinaleObjects();
    this.createTouchControls();
    this.createUtilityControls();
    this.createIntroOverlay();
    this.createOutcomeOverlay();
    this.createPauseOverlay();
    this.createDefeatOverlay();
    this.createFinaleFadeOverlay();
    this.bindKeyboard();
    this.bindIntroPointerInput();
    this.updateHud();
    this.startPlayerIntroIdleAnimation();
    this.startIntroPulseTween();

    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.unbindIntroPointerInput();
      this.unbindClaimInput();
      this.resetDeliveryFinale();
      this.stopIntroTransitionTween(false);
      this.stopIntroPulseTween(false);
      this.stopPlayerIntroIdleAnimation(false);
      this.unbindGameplayMusicVisibility();
      this.game.events.off(
        "portfolio-embed-activity",
        this.onPortfolioEmbedActivity,
      );
      this.destroyGameplayMusic();
      this.exitControl?.remove();
      this.exitControl = null;
      this.reducedMotionMediaQuery?.removeEventListener(
        "change",
        this.onReducedMotionChange,
      );
      this.reducedMotionMediaQuery = null;
      this.pauseOverlay?.setVisible(false);
      this.defeatOverlay?.setVisible(false);
    });
  }

  public update(_time: number, delta: number): void {
    if (this.isPaused) {
      return;
    }

    if (this.runState.phase === "delivered") {
      this.updateDeliveryFinale(delta);
      return;
    }

    if (this.runState.phase !== "playing") {
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

  private createGameplayMusic(): void {
    this.sound.pauseOnBlur = false;
    this.gameplayMusic = this.sound.add(
      GAMEPLAY_AUDIO.music.textureKey,
      {
        loop: true,
        volume: GAMEPLAY_AUDIO.music.volume,
        mute: this.isMusicMuted,
      },
    ) as GameplayMusic;
  }

  private destroyGameplayMusic(): void {
    const music = this.gameplayMusic;
    this.gameplayMusic = null;
    this.musicPausedForVisibility = false;
    if (!music) {
      return;
    }

    music.stop();
    this.sound.remove(music);
  }

  private unlockGameplayAudio(): void {
    const soundManager = this.sound as unknown as {
      readonly locked: boolean;
      unlock?: () => void;
    };
    if (soundManager.locked) {
      soundManager.unlock?.();
    }
  }

  private startGameplayMusic(): void {
    const music = this.gameplayMusic;
    if (!music || !canPlayGameplayMusic(this.runState.phase, this.isPaused, this.isMusicMuted)) {
      return;
    }

    if (music.isPlaying || music.isPaused) {
      music.stop();
    }
    music.mute = false;
    music.play();
  }

  private pauseGameplayMusic(): boolean {
    const music = this.gameplayMusic;
    if (!music?.isPlaying) {
      return false;
    }

    music.pause();
    return true;
  }

  private resumeGameplayMusic(): void {
    const music = this.gameplayMusic;
    if (
      !music ||
      !music.isPaused ||
      !canPlayGameplayMusic(this.runState.phase, this.isPaused, this.isMusicMuted)
    ) {
      return;
    }

    music.resume();
  }

  private stopGameplayMusic(): void {
    this.musicPausedForVisibility = false;
    this.gameplayMusic?.stop();
  }

  private toggleGameplayMusicMuted(): void {
    if (this.runState.phase !== "playing" || this.isPaused) {
      return;
    }

    this.isMusicMuted = !this.isMusicMuted;
    if (this.gameplayMusic) {
      this.gameplayMusic.mute = this.isMusicMuted;
    }
    if (this.isMusicMuted) {
      this.pauseGameplayMusic();
    } else {
      this.resumeGameplayMusic();
    }
    this.updateSoundControlVisual();
  }

  private bindGameplayMusicVisibility(): void {
    if (typeof document !== "undefined") {
      document.addEventListener("visibilitychange", this.onVisibilityChange);
    }
  }

  private unbindGameplayMusicVisibility(): void {
    if (typeof document !== "undefined") {
      document.removeEventListener("visibilitychange", this.onVisibilityChange);
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

  private getCoherentCityLayer(): ActiveEnvironmentLayer | undefined {
    return this.environmentLayers.find(
      ({ spec }) => spec.assetId === "ENV-004",
    );
  }

  private showDeliveryDestinationCity(): void {
    const city = this.getCoherentCityLayer();
    if (!city) {
      return;
    }

    city.sprite
      .setTexture(DELIVERY_ASSETS.destinationCity.textureKey)
      .setTileScale(city.spec.tileScale.x, city.spec.tileScale.y);
    city.sprite.tilePositionX = this.prefersReducedMotion
      ? DELIVERY_FINALE.runtime.destinationCityReducedMotionOffsetTexturePx
      : DELIVERY_FINALE.runtime.destinationCityStartOffsetTexturePx;
  }

  private restoreRouteCity(): void {
    const city = this.getCoherentCityLayer();
    if (!city) {
      return;
    }

    const currentOffset = city.sprite.tilePositionX;
    city.sprite
      .setTexture(city.spec.textureKey)
      .setTileScale(city.spec.tileScale.x, city.spec.tileScale.y);
    city.sprite.tilePositionX = currentOffset;
  }

  private animateEnvironment(delta: number, speedScale = 1): void {
    for (const layer of this.environmentLayers) {
      const texturePixelsPerSecond =
        this.getEnvironmentTextureSpeed(layer.spec);
      layer.sprite.tilePositionX = advanceParallaxOffset({
        currentOffsetTexturePx: layer.sprite.tilePositionX,
        texturePixelsPerSecond,
        deltaMs: delta * speedScale,
        mode: this.environmentMode,
        loopPeriodTexturePx: layer.spec.textureCanvas.width,
        arrivalEndOffsetTexturePx: layer.arrivalEndOffsetTexturePx,
      });
    }
    this.animateControlPanelCobblestone(delta, speedScale);
  }

  private animateControlPanelCobblestone(
    delta: number,
    speedScale: number,
  ): void {
    if (this.prefersReducedMotion) {
      return;
    }

    this.controlPanelCobblestone.tilePositionX = advanceParallaxOffset({
      currentOffsetTexturePx: this.controlPanelCobblestone.tilePositionX,
      texturePixelsPerSecond:
        CONTROL_PANEL_COBBLESTONE.texturePixelsPerSecond,
      deltaMs: delta * speedScale,
      mode: this.environmentMode,
      loopPeriodTexturePx: CONTROL_PANEL_COBBLESTONE.textureWidth,
      arrivalEndOffsetTexturePx:
        this.controlPanelCobblestoneArrivalEndOffsetTexturePx,
    });
  }

  private resetEnvironment(): void {
    this.environmentMode = ENVIRONMENT_PARALLAX.route.mode;
    for (const layer of this.environmentLayers) {
      layer.sprite.tilePositionX = 0;
      layer.arrivalEndOffsetTexturePx = 0;
    }
    this.controlPanelCobblestone.tilePositionX = 0;
    this.controlPanelCobblestoneArrivalEndOffsetTexturePx = 0;
  }

  private setEnvironmentMode(mode: ParallaxMovementMode): void {
    this.environmentMode = mode;
    if (mode !== "arrival-finite") {
      return;
    }

    for (const layer of this.environmentLayers) {
      layer.arrivalEndOffsetTexturePx = layer.sprite.tilePositionX;
    }
    this.controlPanelCobblestoneArrivalEndOffsetTexturePx =
      this.controlPanelCobblestone.tilePositionX;
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

  private createDeliveryFinaleObjects(): void {
    const { anchors, depth, runtime } = DELIVERY_FINALE;
    this.deliveryGirl = this.add
      .image(
        anchors.character.doorwayStart.x,
        anchors.character.doorwayStart.y,
        DELIVERY_ASSETS.girl.textureKey,
      )
      .setOrigin(anchors.girl.originX, anchors.girl.originY)
      .setScale(runtime.girlScale)
      .setAlpha(0)
      .setVisible(false)
      .setDepth(depth.girl);
    this.deliveryCallout = this.add
      .image(
        anchors.callout.x,
        anchors.callout.y,
        DELIVERY_ASSETS.callout.textureKey,
      )
      .setOrigin(0, 0)
      .setVisible(false)
      .setDepth(depth.callout)
      .setScrollFactor(0);
    this.deliveryClaim = this.add
      .sprite(
        anchors.cta.x,
        anchors.cta.y,
        DELIVERY_ASSETS.claim.textureKey,
        0,
      )
      .setOrigin(0.5)
      .setVisible(false)
      .setDepth(depth.cta)
      .setScrollFactor(0);
    this.deliveryClaim
      .setInteractive({
        hitArea: new Phaser.Geom.Rectangle(-84, -24, 168, 48),
        hitAreaCallback: Phaser.Geom.Rectangle.Contains,
        useHandCursor: true,
      })
      .on("pointerdown", () => this.claimDeliveryReward());
  }

  private createFinaleFadeOverlay(): void {
    this.finaleFadeOverlay = this.add
      .rectangle(
        0,
        0,
        GAME_VIEWPORT.width,
        GAME_VIEWPORT.height,
        0x000000,
        1,
      )
      .setOrigin(0, 0)
      .setAlpha(0)
      .setVisible(false)
      .setDepth(RENDER_DEPTH.overlay + 11)
      .setScrollFactor(0);
  }

  private updateDeliveryFinale(delta: number): void {
    if (this.deliveryPhase === "inactive") {
      this.beginDeliveryFinale();
      return;
    }

    if (this.finaleFadeActive) {
      return;
    }

    this.deliveryPhaseElapsedMs += delta;
    if (this.deliveryPhase === "finish-road") {
      this.animateEnvironment(delta);
      this.moveObstacles(delta);
      const duration = this.prefersReducedMotion
        ? DELIVERY_FINALE.reducedMotion.finishRoadDurationMs
        : DELIVERY_FINALE.finishRoadDurationMs;
      if (this.deliveryPhaseElapsedMs >= duration) {
        this.beginArrivalTransition();
      }
      return;
    }

    if (this.deliveryPhase === "arrival-transition") {
      this.updateArrivalTransition(delta);
    }
  }

  private beginDeliveryFinale(): void {
    const nextPhase = advanceDeliveryPresentationPhase(
      this.deliveryPhase,
      "progress-complete",
    );
    if (nextPhase === this.deliveryPhase) {
      return;
    }

    this.deliveryPhase = nextPhase;
    this.deliveryPhaseElapsedMs = 0;
    this.bufferedDirection = null;
    this.laneTweenActive = false;
    this.tweens.killTweensOf(this.player);
    this.player.setAlpha(1).play(PLAYER_DRIVE_ANIMATION);
    this.beginFinaleFade();
  }

  private beginFinaleFade(): void {
    if (this.finaleFadeActive) {
      return;
    }

    this.finaleFadeActive = true;
    this.finaleFadeOverlay.setVisible(true).setAlpha(0);
    this.finaleFadeTween = this.tweens.add({
      targets: this.finaleFadeOverlay,
      alpha: 1,
      duration: FINALE_FADE_TIMING.fadeOutMs,
      ease: "Sine.InOut",
      onComplete: () => {
        this.finaleFadeTween = null;
        if (!this.finaleFadeActive) {
          return;
        }

        this.showDeliveryDestinationCity();
        this.finaleFadeHoldTimer = this.time.delayedCall(
          FINALE_FADE_TIMING.coveredHoldMs,
          () => {
            this.finaleFadeHoldTimer = null;
            if (!this.finaleFadeActive) {
              return;
            }

            this.finaleFadeTween = this.tweens.add({
              targets: this.finaleFadeOverlay,
              alpha: 0,
              duration: FINALE_FADE_TIMING.fadeInMs,
              ease: "Sine.InOut",
              onComplete: () => {
                this.finaleFadeTween = null;
                if (!this.finaleFadeActive) {
                  return;
                }

                this.finaleFadeOverlay.setAlpha(0).setVisible(false);
                this.finaleFadeActive = false;
                this.startConfetti();
              },
            });
          },
        );
      },
    });
  }

  private resetFinaleFade(): void {
    this.finaleFadeActive = false;
    this.finaleFadeTween?.stop();
    this.finaleFadeTween = null;
    this.finaleFadeHoldTimer?.remove(false);
    this.finaleFadeHoldTimer = null;
    this.finaleFadeOverlay?.setAlpha(0).setVisible(false);
  }

  private startConfetti(): void {
    if (this.confettiPieces.length > 0) {
      return;
    }

    const count = this.prefersReducedMotion
      ? DELIVERY_FINALE.reducedMotion.confettiCount
      : DELIVERY_FINALE.confetti.count;
    const colors = DELIVERY_FINALE.confetti.colors;
    for (let index = 0; index < count; index += 1) {
      const source = index % 3;
      const startX =
        source === 0
          ? (index * 47) % GAME_VIEWPORT.width
          : source === 1
            ? -4
            : GAME_VIEWPORT.width + 4;
      const startY = source === 0 ? -8 - (index % 6) * 8 : 150 + (index * 31) % 220;
      const width = index % 2 === 0 ? 4 : 6;
      const height = index % 3 === 0 ? 3 : 5;
      const piece = this.add
        .rectangle(startX, startY, width, height, colors[index % colors.length]!, 1)
        .setDepth(DELIVERY_FINALE.depth.confetti)
        .setScrollFactor(0);
      this.confettiPieces.push(piece);

      const targetX = Phaser.Math.Clamp(
        source === 1
          ? 70 + (index * 23) % 250
          : source === 2
            ? 290 - (index * 19) % 250
            : startX + ((index % 5) - 2) * 18,
        4,
        GAME_VIEWPORT.width - 4,
      );
      this.tweens.add({
        targets: piece,
        x: targetX,
        y: GAME_VIEWPORT.height * 0.76 + (index % 7) * 9,
        angle: this.prefersReducedMotion ? 0 : (index % 2 === 0 ? 220 : -220),
        duration: Math.max(
          550,
          DELIVERY_FINALE.confetti.durationMs - (index % 5) * 90,
        ),
        delay: (index % 8) * 35,
        ease: "Quad.In",
        onComplete: () => {
          piece.destroy();
          this.confettiPieces = this.confettiPieces.filter(
            (candidate) => candidate !== piece,
          );
        },
      });
    }
  }

  private beginArrivalTransition(): void {
    const nextPhase = advanceDeliveryPresentationPhase(
      this.deliveryPhase,
      "finish-road-complete",
    );
    if (nextPhase === this.deliveryPhase) {
      return;
    }

    this.deliveryPhase = nextPhase;
    this.deliveryPhaseElapsedMs = 0;
    this.arrivalPlayerStart = {
      x: this.player.x,
      y: this.player.y,
      scale: this.player.scaleX,
    };
    // Keep the house doorway stationary while its recipient resolves into view.
    // The previous shared interval let the parallax drift behind her, which
    // read as a sudden relative jump even though her own interpolation was valid.
    this.setEnvironmentMode("arrival-finite");

    const { anchors } = DELIVERY_FINALE;
    this.deliveryGirl
      .setPosition(
        anchors.character.doorwayStart.x,
        anchors.character.doorwayStart.y,
      )
      .setAlpha(0)
      .setVisible(true);
  }

  private updateArrivalTransition(delta: number): void {
    const revealProgress = Phaser.Math.Clamp(
      this.deliveryPhaseElapsedMs / DELIVERY_FINALE.arrivalRevealMs,
      0,
      1,
    );
    const decelerationProgress = Phaser.Math.Clamp(
      this.deliveryPhaseElapsedMs / DELIVERY_FINALE.arrivalDecelerationMs,
      0,
      1,
    );
    const easedReveal = Phaser.Math.Easing.Sine.Out(revealProgress);
    const speedScale = (1 - decelerationProgress) ** 2;
    this.animateEnvironment(delta, speedScale);
    this.moveObstacles(delta * speedScale);

    const { anchors } = DELIVERY_FINALE;
    this.deliveryGirl
      .setPosition(
        Phaser.Math.Linear(
          anchors.character.doorwayStart.x,
          anchors.character.doorstepEnd.x,
          easedReveal,
        ),
        Phaser.Math.Linear(
          anchors.character.doorwayStart.y,
          anchors.character.doorstepEnd.y,
          easedReveal,
        ),
      )
      .setAlpha(easedReveal);

    const finalPlayerScale =
      LANE_VISUAL_SCALES[0] * PLAYER_ASSET.textureScale;
    this.player
      .setPosition(
        Phaser.Math.Linear(
          this.arrivalPlayerStart.x,
          anchors.vehicleStop.x,
          easedReveal,
        ),
        Phaser.Math.Linear(
          this.arrivalPlayerStart.y,
          anchors.vehicleStop.y,
          easedReveal,
        ),
      )
      .setScale(
        Phaser.Math.Linear(
          this.arrivalPlayerStart.scale,
          finalPlayerScale,
          easedReveal,
        ),
      )
      .setDepth(RENDER_DEPTH.playerBase);

    if (revealProgress >= 1 && this.player.anims.isPlaying) {
      this.player.stop().setFrame(0);
      this.clearObstacles();
    }

    if (
      this.deliveryPhaseElapsedMs >=
      DELIVERY_FINALE.arrivalRevealMs + DELIVERY_FINALE.rewardPromptDelayMs
    ) {
      this.beginProductTransfer();
    }
  }

  private beginProductTransfer(): void {
    const nextPhase = advanceDeliveryPresentationPhase(
      this.deliveryPhase,
      "arrival-complete",
    );
    if (nextPhase === this.deliveryPhase) {
      return;
    }

    this.deliveryPhase = nextPhase;
    this.deliveryPhaseElapsedMs = 0;
    this.setUtilityControlsVisible(false);
    this.startProductFlight();
  }

  private showDeliveryRewardPrompt(): void {
    const nextPhase = advanceDeliveryPresentationPhase(
      this.deliveryPhase,
      "product-transfer-complete",
    );
    if (nextPhase === this.deliveryPhase) {
      return;
    }

    this.deliveryPhase = nextPhase;
    this.deliveryPhaseElapsedMs = 0;
    this.deliveryCallout
      .setAlpha(0)
      .setY(DELIVERY_FINALE.anchors.callout.y + 10)
      .setVisible(true);
    this.deliveryClaim.setFrame(0).setScale(1).setAlpha(0).setVisible(true);
    this.tweens.add({
      targets: [this.deliveryCallout, this.deliveryClaim],
      alpha: 1,
      duration: 180,
      ease: "Sine.Out",
    });
    this.tweens.add({
      targets: this.deliveryCallout,
      y: DELIVERY_FINALE.anchors.callout.y,
      duration: 180,
      ease: "Sine.Out",
    });
    this.startDeliveryClaimPulse();
    this.bindClaimInput();
  }

  private startDeliveryClaimPulse(): void {
    if (this.prefersReducedMotion || this.deliveryClaimPulseTween) {
      return;
    }
    this.deliveryClaimPulseTween = this.tweens.add({
      targets: this.deliveryClaim,
      scaleX: 1.06,
      scaleY: 1.06,
      duration: 500,
      yoyo: true,
      repeat: -1,
      ease: "Sine.InOut",
    });
  }

  private stopDeliveryClaimPulse(): void {
    this.deliveryClaimPulseTween?.stop();
    this.deliveryClaimPulseTween = null;
    this.deliveryClaim.setScale(1);
  }

  private bindClaimInput(): void {
    if (this.claimInputBound) {
      return;
    }
    this.claimInputBound = true;
    this.input.on("pointerdown", this.onClaimPointerDown, this);
  }

  private unbindClaimInput(): void {
    if (!this.claimInputBound) {
      return;
    }
    this.claimInputBound = false;
    this.input.off("pointerdown", this.onClaimPointerDown, this);
  }

  private claimDeliveryReward(): void {
    const nextPhase = advanceDeliveryPresentationPhase(
      this.deliveryPhase,
      "claim",
    );
    if (nextPhase === this.deliveryPhase || this.isPaused) {
      return;
    }

    this.deliveryPhase = nextPhase;
    this.deliveryPhaseElapsedMs = 0;
    this.unbindClaimInput();
    this.stopDeliveryClaimPulse();
    this.deliveryClaim.setVisible(false);
    this.deliveryCallout.setVisible(false);
    this.invokeExistingRewardFlow();
  }

  private startProductFlight(): void {
    const { anchors, depth, runtime } = DELIVERY_FINALE;
    const productStart = {
      x: this.player.x + anchors.productStartOffset.x,
      y: this.player.y + anchors.productStartOffset.y,
    };
    this.deliveryProduct?.destroy();
    this.deliveryProduct = this.add
      .image(
        productStart.x,
        productStart.y,
        DELIVERY_ASSETS.product.textureKey,
      )
      .setOrigin(0.5)
      .setScale(runtime.productScale)
      .setDepth(depth.product)
      .setScrollFactor(0);

    const control = {
      x: (productStart.x + anchors.character.productTarget.x) / 2,
      y: Math.min(productStart.y, anchors.character.productTarget.y) - 58,
    };
    const flight = { progress: 0 };
    this.productTween = this.tweens.add({
      targets: flight,
      progress: 1,
      duration: DELIVERY_FINALE.productFlightDurationMs,
      ease: "Sine.InOut",
      onUpdate: () => {
        if (!this.deliveryProduct) {
          return;
        }
        const progress = flight.progress;
        const inverse = 1 - progress;
        this.deliveryProduct
          .setPosition(
            inverse * inverse * productStart.x +
              2 * inverse * progress * control.x +
              progress * progress * anchors.character.productTarget.x,
            inverse * inverse * productStart.y +
              2 * inverse * progress * control.y +
              progress * progress * anchors.character.productTarget.y,
          )
          .setAngle(
            this.prefersReducedMotion ? 0 : Math.sin(progress * Math.PI) * 5,
          );
      },
      onComplete: () => {
        this.productTween = null;
        this.completeProductFlight();
      },
    });
  }

  private completeProductFlight(): void {
    if (!this.deliveryProduct) {
      return;
    }
    this.tweens.add({
      targets: this.deliveryProduct,
      scaleX: 0.2,
      scaleY: 0.2,
      alpha: 0,
      duration: DELIVERY_FINALE.productDisappearDurationMs,
      ease: "Sine.In",
      onComplete: () => {
        this.deliveryProduct?.destroy();
        this.deliveryProduct = null;
        this.showDeliveryRewardPrompt();
      },
    });
  }

  private invokeExistingRewardFlow(): void {
    if (this.rewardFlowInvoked) {
      return;
    }
    this.rewardFlowInvoked = true;
    this.deliveryCallout.setVisible(false);
    this.deliveryClaim.setVisible(false);
    this.showCouponReward();
  }

  private clearConfetti(): void {
    for (const piece of this.confettiPieces) {
      this.tweens.killTweensOf(piece);
      piece.destroy();
    }
    this.confettiPieces = [];
  }

  private resetDeliveryFinale(): void {
    this.resetFinaleFade();
    this.hideCouponReward();
    this.unbindClaimInput();
    this.stopDeliveryClaimPulse();
    this.productTween?.stop();
    this.productTween = null;
    this.deliveryProduct?.destroy();
    this.deliveryProduct = null;
    this.clearConfetti();
    this.deliveryGirl?.setVisible(false).setAlpha(0);
    this.deliveryCallout?.setVisible(false).setAlpha(1);
    this.deliveryClaim?.setVisible(false).setAlpha(1).setFrame(0).setScale(1);
    for (const layer of this.environmentLayers) {
      layer.sprite.setAlpha(1);
    }
    this.restoreRouteCity();
    this.deliveryPhase = advanceDeliveryPresentationPhase(
      this.deliveryPhase,
      "reset",
    );
    this.deliveryPhaseElapsedMs = 0;
    this.rewardFlowInvoked = false;
  }

  private createTouchControls(): void {
    this.controlPanelCobblestone = this.add
      .tileSprite(
        CONTROL_PANEL_COBBLESTONE.x,
        CONTROL_PANEL_COBBLESTONE.y,
        CONTROL_PANEL_COBBLESTONE.width,
        CONTROL_PANEL_COBBLESTONE.height,
        CONTROL_PANEL_COBBLESTONE.textureKey,
      )
      .setOrigin(0, 0)
      .setDepth(RENDER_DEPTH.controls - 2)
      .setScrollFactor(0);

    const up = this.createControlButton(HUD_ASSETS.controls.upX, HUD_ASSETS.controls.y, -1);
    const down = this.createControlButton(HUD_ASSETS.controls.downX, HUD_ASSETS.controls.y, 1);
    up.setDepth(RENDER_DEPTH.controls).setScrollFactor(0);
    down.setDepth(RENDER_DEPTH.controls).setScrollFactor(0);
  }

  private createUtilityControls(): void {
    this.exitControl = this.createExitControl();
    const pause = this.createUtilityButton(HUD_ASSETS.pause, () => {
      this.pauseRun();
    });
    const sound = this.createUtilityButton(HUD_ASSETS.sound, () => {
      this.toggleGameplayMusicMuted();
    });
    this.soundControl = sound;
    this.soundMuteSlash = this.createSoundMuteSlash();
    this.utilityControls = [pause, sound];
    this.setUtilityControlsVisible(false);
  }

  private createExitControl(): HTMLButtonElement {
    const gameRoot = this.game.canvas.parentElement;
    if (!gameRoot) {
      throw new Error("Game root element was not found for the exit placeholder");
    }

    const button = document.createElement("button");
    button.type = "button";
    button.className = EXIT_CONTROL.className;
    button.setAttribute("aria-label", EXIT_CONTROL.ariaLabel);
    button.hidden = false;
    button.addEventListener("pointerdown", (event) => event.stopPropagation());
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      requestPortfolioEmbedClose();
    });
    gameRoot.appendChild(button);
    return button;
  }

  private createSoundMuteSlash(): Phaser.GameObjects.Container {
    const pixels = Array.from({ length: 7 }, (_, index) =>
      this.add
        .rectangle(-9 + index * 3, 9 - index * 3, 4, 4, COLORS.brandRed, 1)
        .setOrigin(0.5),
    );

    return this.add
      .container(HUD_ASSETS.sound.x, HUD_ASSETS.sound.y, pixels)
      .setDepth(RENDER_DEPTH.controls + 2)
      .setScrollFactor(0)
      .setVisible(false);
  }

  private createUtilityButton(
    asset: (typeof HUD_ASSETS)["pause"],
    onActivate?: () => void,
  ): Phaser.GameObjects.Sprite {
    const hitAreaOffset = -(asset.hitAreaSize - asset.frameWidth) / 2;
    const button = this.add
      .sprite(asset.x, asset.y, asset.textureKey, 0)
      .setInteractive({
        hitArea: new Phaser.Geom.Rectangle(
          hitAreaOffset,
          hitAreaOffset,
          asset.hitAreaSize,
          asset.hitAreaSize,
        ),
        hitAreaCallback: Phaser.Geom.Rectangle.Contains,
        useHandCursor: true,
      })
      .setDepth(RENDER_DEPTH.controls + 1)
      .setScrollFactor(0);

    button.on("pointerdown", () => {
      button.setFrame(1);
      onActivate?.();
    });
    button.on("pointerup", () => button.setFrame(0));
    button.on("pointerout", () => button.setFrame(0));
    return button;
  }

  private setUtilityControlsVisible(visible: boolean): void {
    for (const button of this.utilityControls) {
      button.setVisible(visible);
    }
    this.updateSoundControlVisual();
  }

  private updateSoundControlVisual(): void {
    this.soundMuteSlash?.setVisible(
      this.isMusicMuted && Boolean(this.soundControl?.visible),
    );
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
    this.promptPanel = this.add.rectangle(180, 322, 302, 238, COLORS.cream, 1);
    this.promptPanel.setStrokeStyle(5, COLORS.pink, 1);

    this.promptTitle = this.add
      .text(180, 260, "ORDER DELIVERED!", {
        align: "center",
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "15px",
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
      .text(180, 382, "RETRY", {
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

    const couponBackground = this.add
      .image(
        COUPON_POPUP_LAYOUT.centerX,
        COUPON_POPUP_LAYOUT.centerY,
        DELIVERY_ASSETS.rewardCoupon.textureKey,
      )
      .setOrigin(0.5);
    const codeFieldShadow = this.add.rectangle(
      COUPON_POPUP_LAYOUT.codeFieldX + 2,
      COUPON_POPUP_LAYOUT.codeFieldY + 3,
      COUPON_POPUP_LAYOUT.codeFieldWidth,
      COUPON_POPUP_LAYOUT.codeFieldHeight,
      0x982add,
      1,
    );
    const codeField = this.add.rectangle(
      COUPON_POPUP_LAYOUT.codeFieldX,
      COUPON_POPUP_LAYOUT.codeFieldY,
      COUPON_POPUP_LAYOUT.codeFieldWidth,
      COUPON_POPUP_LAYOUT.codeFieldHeight,
      COLORS.cream,
      1,
    );
    codeField.setStrokeStyle(3, COLORS.navy, 1);
    const codeText = this.add
      .text(COUPON_POPUP_LAYOUT.codeFieldX, COUPON_POPUP_LAYOUT.codeFieldY, COUPON_CODE, {
        align: "center",
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "22px",
        fontStyle: "bold",
        letterSpacing: 1,
      })
      .setOrigin(0.5);
    this.couponCopyButton = this.createCouponCopyButton(
      COUPON_POPUP_LAYOUT.copyButtonX,
      COUPON_POPUP_LAYOUT.copyButtonY,
    );
    this.couponCopyFeedback = this.add
      .text(COUPON_POPUP_LAYOUT.centerX, COUPON_POPUP_LAYOUT.copyFeedbackY, "", {
        align: "center",
        color: "#17162f",
        fontFamily: "monospace",
        fontSize: "11px",
        fontStyle: "bold",
      })
      .setOrigin(0.5)
      .setVisible(false);
    this.couponPanel = this.add.container(0, 0, [
      couponBackground,
      codeFieldShadow,
      codeField,
      codeText,
      this.couponCopyButton,
      this.couponCopyFeedback,
    ]);
    this.couponPanel.setVisible(false);

    this.promptOverlay = this.add.container(0, 0, [
      shade,
      this.promptPanel,
      this.promptTitle,
      this.promptBody,
      this.promptButton,
      this.couponPanel,
    ]);
    this.promptOverlay
      .setDepth(RENDER_DEPTH.overlay)
      .setScrollFactor(0)
      .setVisible(false);
  }

  private createCouponCopyButton(x: number, y: number): Phaser.GameObjects.Container {
    const { copyButtonSize, copyButtonHitArea } = COUPON_POPUP_LAYOUT;
    const shadow = this.add.rectangle(2, 3, copyButtonSize, copyButtonSize, 0x982add, 1);
    const outline = this.add.rectangle(0, 0, copyButtonSize, copyButtonSize, COLORS.navy, 1);
    const face = this.add.rectangle(0, -2, 36, 34, COLORS.pink, 1);
    this.couponCopyIcon = this.add.container(0, 0, [
      this.add.rectangle(-4, -5, 13, 15, COLORS.cream, 1).setStrokeStyle(2, COLORS.navy),
      this.add.rectangle(3, 3, 13, 15, COLORS.cream, 1).setStrokeStyle(2, COLORS.navy),
    ]);
    this.couponCopyCheck = this.add.container(0, 0, [
      this.add.rectangle(-8, 0, 4, 4, COLORS.cream, 1),
      this.add.rectangle(-4, 4, 4, 4, COLORS.cream, 1),
      this.add.rectangle(0, 0, 4, 4, COLORS.cream, 1),
      this.add.rectangle(4, -4, 4, 4, COLORS.cream, 1),
      this.add.rectangle(8, -8, 4, 4, COLORS.cream, 1),
    ]);
    this.couponCopyCheck.setVisible(false);
    const button = this.add.container(x, y, [
      shadow,
      outline,
      face,
      this.couponCopyIcon,
      this.couponCopyCheck,
    ]);
    let pressed = false;
    const setPressed = (value: boolean): void => {
      pressed = value;
      face.setFillStyle(value ? 0xd9377f : COLORS.pink, 1);
      face.setY(value ? 1 : -2);
      this.couponCopyIcon.setY(value ? 3 : 0);
      this.couponCopyCheck.setY(value ? 3 : 0);
    };

    button
      .setSize(copyButtonHitArea, copyButtonHitArea)
      .setInteractive({ useHandCursor: true })
      .on("pointerover", () => {
        if (!pressed) {
          face.setFillStyle(0xff72b8, 1);
        }
      })
      .on("pointerout", () => {
        setPressed(false);
        face.setFillStyle(COLORS.pink, 1);
      })
      .on("pointerdown", () => setPressed(true))
      .on("pointerup", () => {
        if (!pressed) {
          return;
        }
        setPressed(false);
        void this.copyCouponCode();
      });
    button.disableInteractive();
    return button;
  }

  private showCouponReward(): void {
    this.promptPanel.setVisible(false);
    this.promptTitle.setVisible(false);
    this.promptBody.setVisible(false);
    this.promptButton.disableInteractive().setVisible(false);
    this.couponPanel.setVisible(true).setAlpha(1).setScale(1);
    this.couponCopyButton.setInteractive({ useHandCursor: true });
    this.promptOverlay.setVisible(true);
    this.createCouponCopyAccessibility();
  }

  private hideCouponReward(): void {
    this.couponCopyResetTimer?.remove(false);
    this.couponCopyResetTimer = null;
    this.promptButton.setVisible(true).setInteractive({ useHandCursor: true });
    if (this.couponPanel) {
      this.couponPanel.setVisible(false).setAlpha(1).setScale(1);
      this.couponCopyButton.disableInteractive();
      this.couponCopyIcon.setVisible(true).setY(0);
      this.couponCopyCheck.setVisible(false).setY(0);
      this.couponCopyFeedback.setText("").setVisible(false);
    }
    this.removeCouponCopyAccessibility();
  }

  private async copyCouponCode(): Promise<void> {
    if (!this.couponPanel.visible) {
      return;
    }
    let copied = false;
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(COUPON_CODE);
        copied = true;
      }
    } catch {
      copied = false;
    }
    if (!copied) {
      copied = this.copyCouponCodeFallback();
    }
    if (!copied || !this.couponPanel.visible) {
      this.announceCouponCopy("Не удалось скопировать");
      return;
    }

    this.couponCopyResetTimer?.remove(false);
    this.couponCopyIcon.setVisible(false);
    this.couponCopyCheck.setVisible(true);
    this.couponCopyFeedback.setText("Скопировано").setVisible(true);
    this.announceCouponCopy("Скопировано");
    this.couponCopyResetTimer = this.time.delayedCall(1000, () => {
      this.couponCopyResetTimer = null;
      if (!this.couponPanel.visible) {
        return;
      }
      this.couponCopyIcon.setVisible(true);
      this.couponCopyCheck.setVisible(false);
      this.couponCopyFeedback.setText("").setVisible(false);
    });
  }

  private copyCouponCodeFallback(): boolean {
    if (typeof document === "undefined" || !document.body) {
      return false;
    }
    const element = document.createElement("textarea");
    element.value = COUPON_CODE;
    element.setAttribute("readonly", "");
    Object.assign(element.style, {
      position: "fixed",
      left: "-9999px",
      top: "0",
      opacity: "0",
      pointerEvents: "none",
    });
    document.body.appendChild(element);
    element.select();
    try {
      return document.execCommand("copy");
    } finally {
      element.remove();
    }
  }

  private createCouponCopyAccessibility(): void {
    if (this.couponCopyAccessibleButton || typeof document === "undefined" || !document.body) {
      return;
    }
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", "Скопировать купон");
    button.textContent = "Скопировать купон";
    Object.assign(button.style, {
      position: "fixed",
      width: "1px",
      height: "1px",
      padding: "0",
      margin: "-1px",
      overflow: "hidden",
      clip: "rect(0, 0, 0, 0)",
      whiteSpace: "nowrap",
      border: "0",
    });
    button.addEventListener("click", () => void this.copyCouponCode());
    const announcement = document.createElement("span");
    announcement.setAttribute("aria-live", "polite");
    announcement.style.cssText = button.style.cssText;
    document.body.append(button, announcement);
    this.couponCopyAccessibleButton = button;
    this.couponCopyAnnouncement = announcement;
  }

  private announceCouponCopy(message: string): void {
    if (this.couponCopyAnnouncement) {
      this.couponCopyAnnouncement.textContent = message;
    }
  }

  private removeCouponCopyAccessibility(): void {
    this.couponCopyAccessibleButton?.remove();
    this.couponCopyAnnouncement?.remove();
    this.couponCopyAccessibleButton = null;
    this.couponCopyAnnouncement = null;
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
    this.unlockGameplayAudio();
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
    this.setUtilityControlsVisible(true);
    this.player
      .setTexture(PLAYER_ASSET.textureKey, 0)
      .play(PLAYER_DRIVE_ANIMATION);
    this.startGameplayMusic();
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
    const callout = this.add.image(
      PAUSE_ASSETS.callout.x,
      PAUSE_ASSETS.callout.y,
      PAUSE_ASSETS.callout.textureKey,
    );
    const continueButton = this.createPauseMenuButton(
      334,
      "ПРОДОЛЖИТЬ",
      () => this.resumeRun(),
    );
    const restartButton = this.createPauseMenuButton(
      394,
      "ЗАНОВО",
      () => this.restartPausedRun(),
    );

    this.pauseOverlay = this.add.container(0, 0, [
      shade,
      callout,
      continueButton,
      restartButton,
    ]);
    this.pauseOverlay
      .setDepth(RENDER_DEPTH.overlay + 10)
      .setScrollFactor(0)
      .setVisible(false);
  }

  private createDefeatOverlay(): void {
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
    const callout = this.add.image(
      DEFEAT_ASSETS.callout.x,
      DEFEAT_ASSETS.callout.y,
      DEFEAT_ASSETS.callout.textureKey,
    );
    const restartButton = this.createPauseMenuButton(
      394,
      "заново",
      () => this.resetRun(),
    );

    this.defeatOverlay = this.add.container(0, 0, [
      shade,
      callout,
      restartButton,
    ]);
    this.defeatOverlay
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

    if (this.deliveryPhase === "reward-prompt") {
      this.claimDeliveryReward();
      return;
    }

    if (this.runState.phase === "defeated") {
      this.resetRun();
      return;
    }

    if (
      this.runState.phase === "delivered" &&
      this.deliveryPhase === "complete" &&
      this.rewardFlowInvoked
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
      this.stopGameplayMusic();
      this.beginDeliveryFinale();
    } else if (phase === "defeated") {
      this.stopGameplayMusic();
      this.setUtilityControlsVisible(false);
      this.player.stop();
      this.player.setFrame(0);
      this.hideCouponReward();
      this.promptOverlay.setVisible(false);
      this.defeatOverlay.setVisible(true);
    }
  }

  private resetRun(): void {
    this.stopGameplayMusic();
    this.isPaused = false;
    this.pauseOverlay.setVisible(false);
    this.defeatOverlay.setVisible(false);
    this.setUtilityControlsVisible(true);
    this.tweens.resumeAll();
    this.tweens.killTweensOf(this.player);
    this.playerIntroIdleAnimationActive = false;
    this.clearObstacles();
    this.resetDeliveryFinale();
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
    this.startGameplayMusic();
    this.updateHud();
  }

  private togglePause(): void {
    if (!this.canPause()) {
      return;
    }
    if (this.isPaused) {
      this.resumeRun();
    } else {
      this.pauseRun();
    }
  }

  private pauseRun(): void {
    if (!this.canPause() || this.isPaused) {
      return;
    }
    this.isPaused = true;
    this.pauseGameplayMusic();
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
    this.resumeGameplayMusic();
  }

  private canPause(): boolean {
    return (
      this.runState.phase === "playing" ||
      this.deliveryPhase === "finish-road" ||
      this.deliveryPhase === "arrival-transition" ||
      this.deliveryPhase === "reward-prompt"
    );
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
