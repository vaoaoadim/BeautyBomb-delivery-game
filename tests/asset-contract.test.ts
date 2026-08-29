import { describe, expect, it } from "vitest";

import driveMetadata from "../public/assets/game/vehicles/veh-001-courier-clean-drive-v6.json";
import introIdleMetadata from "../public/assets/game/vehicles/veh-001-courier-clean-intro-idle-v1.json";
import staticMetadata from "../public/assets/game/vehicles/veh-001-courier-clean-static-v5.json";
import greenWagonMetadata from "../public/assets/game/vehicles/obs-003-green-wagon-static-v2.json";
import pinkHatchbackMetadata from "../public/assets/game/vehicles/obs-001-pink-hatchback-static-v2.json";
import yellowSedanMetadata from "../public/assets/game/vehicles/obs-002-yellow-sedan-static-v2.json";
import greenWagonDriveMetadata from "../public/assets/game/vehicles/obs-003-green-wagon-drive-v2.json";
import pinkHatchbackDriveMetadata from "../public/assets/game/vehicles/obs-001-pink-hatchback-drive-v2.json";
import yellowSedanDriveMetadata from "../public/assets/game/vehicles/obs-002-yellow-sedan-drive-v2.json";
import environmentSkyMetadata from "../public/assets/game/environment/env-001-sky-v5.json";
import environmentCoherentCityMetadata from "../public/assets/game/environment/env-004-neighborhood-city-v8.json";
import environmentRoadMetadata from "../public/assets/game/environment/env-006-road-v6.json";
import environmentForegroundMetadata from "../public/assets/game/environment/env-008-foreground-accents-v5.json";
import environmentSkyV4Metadata from "../public/assets/game/environment/env-001-sky-v4.json";
import environmentRoadV4Metadata from "../public/assets/game/environment/env-006-road-v4.json";
import environmentForegroundV4Metadata from "../public/assets/game/environment/env-008-foreground-accents-v4.json";
import environmentMasterMetadata from "../visual-references/env-001-parallax-coherent-v4-candidate.json";
import environmentNeighborhoodMasterMetadata from "../visual-references/env-001-parallax-neighborhood-v6-alpha-master.json";
import hudHeartMetadata from "../public/assets/game/ui/ico-001-life-heart-v1.json";
import hudProgressMetadata from "../public/assets/game/ui/ui-003-progress-bar-v1.json";
import hudControlsMetadata from "../public/assets/game/ui/ui-004-touch-controls-v2.json";
import hudPanelMetadata from "../public/assets/game/ui/ui-008-control-panel-v1.json";
import hudTitleMetadata from "../public/assets/game/ui/ui-009-game-title-v1.json";
import hudPauseMetadata from "../public/assets/game/ui/ui-010-pause-button-v2.json";
import hudExitMetadata from "../public/assets/game/ui/ui-011-exit-button-v1.json";
import hudSoundMetadata from "../public/assets/game/ui/ui-012-sound-button-v2.json";
import pauseCalloutMetadata from "../public/assets/game/ui/ui-015-pause-callout-v2.json";
import defeatCalloutMetadata from "../public/assets/game/ui/ui-006-defeat-callout-v1.json";
import deliveryCalloutMetadata from "../public/assets/game/ui/ui-016-delivery-callout-v5.json";
import deliveryClaimMetadata from "../public/assets/game/ui/ui-017-claim-v1.json";
import rewardCouponMetadata from "../public/assets/game/ui/ui-018-reward-coupon-v5.json";
import deliveryDestinationCityMetadata from "../public/assets/game/environment/env-009-delivery-destination-city-v3.json";
import deliveryHouseMetadata from "../public/assets/game/environment/dst-001-arrival-house-v1.json";
import deliveryGirlMetadata from "../public/assets/game/characters/chr-003-lowpoly-recipient-v1.json";
import deliveryProductMetadata from "../public/assets/game/products/prd-003-delivery-transfer-v1.json";
import { GAME_VIEWPORT, LANE_VISUAL_SCALES } from "../src/game/config";
import { ENVIRONMENT_PARALLAX } from "../src/game/content/environmentParallax";

describe("approved-master asset contract", () => {
  it("keeps the approved courier static tied to one deterministic master export", () => {
    expect(staticMetadata.canvas).toEqual({ width: 208, height: 160 });
    expect(staticMetadata.runtimeScale).toBe(0.5);
    expect(staticMetadata.collision.includesRoofProduct).toBe(false);
    expect(staticMetadata.production).toMatchObject({
      designMaster:
        "visual-references/veh-001-courier-clean-concept-v7.png",
      buildScript: "scripts/build_courier_clean_asset.py",
      assetMode: "high-detail-pixel-style-raster",
      offlineResizeCount: 1,
      resizeFilter: "nearest-neighbor",
      paletteQuantization: false,
      phaserTextureFilter: "nearest",
      status: "approved-static-master",
    });
    expect(staticMetadata.production.designMasterSha256).toMatch(/^[a-f0-9]{64}$/);
    expect(staticMetadata.production.runtimeSha256).toMatch(/^[a-f0-9]{64}$/);
    expect(staticMetadata.production.laneTextureScales).toEqual(
      LANE_VISUAL_SCALES.map((scale) => scale * staticMetadata.runtimeScale),
    );
  });

  it("derives the drive sheet from the approved master without using a runtime export as input", () => {
    expect(driveMetadata.frame).toEqual({ width: 208, height: 160, count: 4 });
    expect(driveMetadata.animation).toEqual({
      frameRate: 9,
      loop: true,
      firstFrameMatchesApprovedStatic: true,
    });
    expect(driveMetadata.collision.includesRoofProduct).toBe(false);
    expect(driveMetadata.production).toMatchObject({
      designMaster:
        "visual-references/veh-001-courier-clean-concept-v7.png",
      approvedStaticTexture: "veh-001-courier-clean-static-v5.png",
      staticRuntimeUsage: "approval anchor only; not an export input",
      buildScript: "scripts/build_courier_clean_asset.py",
      offlineResizeCountPerFrame: 1,
      resizeFilter: "nearest-neighbor",
      phaserTextureFilter: "nearest",
    });
    expect(driveMetadata.production.designMasterSha256).toBe(
      staticMetadata.production.designMasterSha256,
    );
    expect(driveMetadata.production.approvedStaticRuntimeSha256).toBe(
      staticMetadata.production.runtimeSha256,
    );
    expect(driveMetadata.production.laneTextureScales).toEqual(
      LANE_VISUAL_SCALES.map((scale) => scale * driveMetadata.runtimeScale),
    );
  });

  it("keeps the intro courier motion identical to driving except for wheel hubs", () => {
    expect(introIdleMetadata.frame).toEqual({
      width: 208,
      height: 160,
      count: 4,
    });
    expect(introIdleMetadata.animation).toMatchObject({
      frameRate: 9,
      loop: true,
      bodyAndTubeMotion: "matches-drive-v6",
      wheelHubs: "frozen-from-approved-static-frame",
      firstFrameMatchesApprovedStatic: true,
    });
    expect(introIdleMetadata.production).toMatchObject({
      designMaster:
        "visual-references/veh-001-courier-clean-concept-v7.png",
      buildScript: "scripts/build_courier_clean_asset.py",
      offlineResizeCountPerFrame: 1,
      resizeFilter: "nearest-neighbor",
      phaserTextureFilter: "nearest",
      status: "produced-intro-idle",
    });
  });

  it("keeps every approved obstacle master on a one-resize static export path", () => {
    const obstacleMetadata = [
      pinkHatchbackMetadata,
      yellowSedanMetadata,
      greenWagonMetadata,
    ];

    for (const metadata of obstacleMetadata) {
      expect(metadata.canvas.width).toBeGreaterThan(0);
      expect(metadata.canvas.height).toBeGreaterThan(0);
      expect(metadata.visibleBounds.width).toBeGreaterThan(0);
      expect(metadata.visibleBounds.height).toBeGreaterThan(0);
      expect(metadata.collision.width).toBeGreaterThan(0);
      expect(metadata.collision.height).toBeGreaterThan(0);
      expect(metadata.production).toMatchObject({
        buildScript: "scripts/build_obstacle_static_v2.py",
        assetMode: "high-detail-pixel-style-raster",
        alphaNoiseThreshold: 16,
        offlineResizeCount: 1,
        resizeFilter: "nearest-neighbor",
        paletteQuantization: false,
        phaserTextureFilter: "nearest",
        animationFrames: 1,
        status: "approved-static-master",
      });
      expect(metadata.production.designMaster).toMatch(
        /^visual-references\/obs-00[1-3]-.*-concept-v2\.png$/,
      );
      expect(metadata.production.designMasterSha256).toMatch(/^[a-f0-9]{64}$/);
      expect(metadata.production.runtimeSha256).toMatch(/^[a-f0-9]{64}$/);
      expect(metadata.production.laneVisualScales).toEqual([...LANE_VISUAL_SCALES]);
    }
  });

  it("derives every obstacle drive sheet from its approved static master", () => {
    const pairs = [
      [pinkHatchbackMetadata, pinkHatchbackDriveMetadata],
      [yellowSedanMetadata, yellowSedanDriveMetadata],
      [greenWagonMetadata, greenWagonDriveMetadata],
    ] as const;

    for (const [staticMetadata, driveMetadata] of pairs) {
      expect(driveMetadata.frame).toEqual({
        width: staticMetadata.canvas.width,
        height: staticMetadata.canvas.height,
        count: 4,
      });
      expect(driveMetadata.frameVisibleBounds).toEqual(
        Array.from({ length: 4 }, () => staticMetadata.visibleBounds),
      );
      expect(driveMetadata.animation).toEqual({
        frameRate: 7,
        loop: true,
        firstFrameMatchesApprovedStatic: true,
        motion: "hub rotation only; body and wheel baseline remain stable",
      });
      expect(driveMetadata.production).toMatchObject({
        designMaster: staticMetadata.production.designMaster,
        approvedStaticTexture: staticMetadata.texture,
        approvedStaticRuntimeSha256: staticMetadata.production.runtimeSha256,
        staticRuntimeUsage: "approval anchor only; not an export input",
        buildScript: "scripts/build_obstacle_drive_v2.py",
        offlineResizeCountPerFrame: 1,
        resizeFilter: "nearest-neighbor",
        phaserTextureFilter: "nearest",
        status: "approved-drive-cycle",
      });
    }
  });

  it("keeps the city coherent and restores the approved full-height road", () => {
    expect(ENVIRONMENT_PARALLAX.route.baseDisplaySpeedPxPerSecond).toBe(72);
    expect(environmentMasterMetadata).toMatchObject({
      assetId: "ENV-SCENE-001",
      version: "v4",
      status: "approved-master",
      canvas: { width: 2172, height: 724 },
      runtimeViewport: { width: 360, height: 640 },
      runtimeBandGuides: {
        roadTop: 282,
        roadBottom: 522,
        laneSeparators: [363, 437],
      },
    });
    expect(environmentMasterMetadata.sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(environmentNeighborhoodMasterMetadata).toMatchObject({
      assetId: "ENV-SCENE-001",
      version: "v6",
      status: "approved-master",
      canvas: { width: 2172, height: 724 },
      runtimeBandGuides: { cityBottom: 282, roadTop: 282 },
      alpha: { mode: "RGBA" },
    });
    expect(environmentNeighborhoodMasterMetadata.sha256).toMatch(
      /^[a-f0-9]{64}$/,
    );

    const layers = [
      [environmentSkyMetadata, { width: 2048, height: 512 }, "v5", "scripts/build_environment_parallax_v5.py"],
      [environmentCoherentCityMetadata, { width: 2048, height: 512 }, "v8", "scripts/build_environment_city_v8.py"],
      [environmentRoadMetadata, { width: 2048, height: 512 }, "v9", "scripts/build_environment_road_v6.py"],
      [environmentForegroundMetadata, { width: 2048, height: 128 }, "v5", "scripts/build_environment_parallax_v5.py"],
    ] as const;

    for (const [metadata, canvas, version, script] of layers) {
      expect(metadata.status).toBe("integrated");
      expect(metadata.version).toBe(version);
      expect(metadata.runtime.textureCanvas).toEqual(canvas);
      expect(metadata.runtime.loopPeriodTexturePx).toBe(canvas.width);
      expect(metadata.runtime.contentRect.height).toBeLessThanOrEqual(
        canvas.height,
      );
      expect(Number.isInteger(Math.log2(canvas.width))).toBe(true);
      expect(Number.isInteger(Math.log2(canvas.height))).toBe(true);
      expect(metadata.production).toMatchObject({
        script,
        contentSource: "src/game/content/environmentParallax.json",
        offlineResizeCount: 1,
        resizeFilter: "nearest-neighbor",
        paletteQuantization: "none",
        phaserTextureFilter: "nearest",
      });
      expect(metadata.runtime.sha256).toMatch(/^[a-f0-9]{64}$/);
      expect(metadata.runtimePlacement.displaySpeedPxPerSecond).toBeGreaterThan(
        0,
      );
      expect(metadata.seamContract.edgeMismatchRows).toEqual({ cycleWrap: 0 });
    }

    for (const metadata of [
      environmentSkyMetadata,
      environmentCoherentCityMetadata,
    ]) {
      expect(metadata.runtime.contentRect).toMatchObject({
        x: 0,
        width: 2048,
      });
      expect(metadata.seamContract).toMatchObject({
        mode: "direct-approved-loop",
        safeGutterTexturePx: 0,
      });
    }
    expect(environmentForegroundMetadata.runtime.contentRect).toMatchObject({
      x: 128,
      width: 1792,
    });
    expect(environmentForegroundMetadata.seamContract).toMatchObject({
      mode: "safe-gutter-direct-panorama",
      safeGutterTexturePx: 128,
    });

    expect(environmentSkyMetadata.production).toMatchObject({
      approvedMaster:
        "visual-references/env-001-parallax-coherent-v4-candidate.png",
      approvedMasterSha256: environmentMasterMetadata.sha256,
    });
    expect(environmentCoherentCityMetadata.production).toMatchObject({
      approvedMaster:
        "visual-references/env-001-parallax-neighborhood-v6-alpha-master.png",
      approvedMasterSha256: environmentNeighborhoodMasterMetadata.sha256,
    });
    expect(environmentForegroundMetadata.production.approvedMaster).toBe(
      "visual-references/env-001-gameplay-still-concept-v2.png",
    );
    expect(environmentRoadMetadata.production).toMatchObject({
      approvedMaster: "visual-references/env-001-parallax-seamless-v3.png",
      sourceBox: [0, 540, 1774, 887],
    });
    expect(environmentRoadMetadata.runtime).toMatchObject({
      textureCanvas: { width: 2048, height: 512 },
      contentRect: { x: 128, width: 1792, height: 406 },
    });
    expect(environmentRoadMetadata.seamContract).toMatchObject({
      mode: "safe-gutter-direct-panorama",
      safeGutterTexturePx: 128,
    });
    expect(environmentSkyMetadata.runtime.sha256).toBe(
      environmentSkyV4Metadata.runtime.sha256,
    );
    expect(environmentRoadMetadata.runtime.sha256).not.toBe(
      environmentRoadV4Metadata.runtime.sha256,
    );
    expect(environmentRoadMetadata.curbContract).toEqual({
      top: "white neutral pixel curb",
      bottom: "white neutral pixel curb",
      laneMarkingsChanged: false,
      roadSurfaceChanged: false,
    });
    expect(environmentForegroundMetadata.runtime.sha256).toBe(
      environmentForegroundV4Metadata.runtime.sha256,
    );

    expect(ENVIRONMENT_PARALLAX.layers.map((layer) => layer.assetId)).toEqual([
      "ENV-001",
      "ENV-004",
      "ENV-006",
      "ENV-008",
    ]);
    expect(environmentCoherentCityMetadata.production).toMatchObject({
      alphaExtraction: "approved-alpha-city",
      maskMethod:
        "versioned transparent master derived from a flat magenta imagegen source via the installed remove_chroma_key helper",
      sourceBox: [123, 0, 2005, 693],
    });
    expect(environmentCoherentCityMetadata.alphaContract).toMatchObject({
      cityComposition: "unified-neighborhood-skyline-to-sidewalk",
      runtimeColorDeletion: "none",
      detachedCloudsRetained: false,
    });

    for (const layer of ENVIRONMENT_PARALLAX.layers) {
      expect(layer.textureCanvas.width).toBe(
        layer.contentCanvas.width + layer.seamGutterTexturePx * 2,
      );
      expect(layer.textureCanvas.width).toBeGreaterThanOrEqual(
        GAME_VIEWPORT.width,
      );
      expect(layer.depth).toBeLessThan(40);
      expect(layer.alphaMode).not.toBe("remove-cyan-sky");
    }
    expect(environmentCoherentCityMetadata.runtimePlacement.fullCycleSeconds).toBeGreaterThanOrEqual(
      18,
    );
  });

  it("keeps the branded HUD candidate on the locked gameplay geometry", () => {
    const hudAssets = [
      [hudHeartMetadata, "scripts/build_hud_ui_v1.py"],
      [hudProgressMetadata, "scripts/build_hud_ui_v1.py"],
      [hudControlsMetadata, "scripts/build_touch_controls_v2.py"],
      [hudPanelMetadata, "scripts/build_hud_ui_v1.py"],
      [hudTitleMetadata, "scripts/build_hud_ui_v1.py"],
      [hudPauseMetadata, "scripts/build_utility_buttons_v2.py"],
      [hudExitMetadata, "scripts/build_hud_ui_v1.py"],
      [hudSoundMetadata, "scripts/build_utility_buttons_v2.py"],
    ] as const;

    for (const [metadata, buildScript] of hudAssets) {
      expect(metadata.status).toBe("integrated");
      const generatedUtilityAsset =
        metadata === hudPauseMetadata || metadata === hudSoundMetadata;
      expect(metadata.production).toMatchObject(
        generatedUtilityAsset
          ? {
              buildScript,
              assetMode: "generated-master-derived-pixel-art",
              offlineResizeCountPerFrame: 1,
              resizeFilter: "nearest-neighbor",
              antialiasing: false,
              paletteQuantization: false,
              phaserTextureFilter: "nearest",
            }
          : {
              buildScript,
              assetMode: "authored-low-resolution-pixel-art",
              offlineResizeCount: 0,
              antialiasing: false,
              paletteQuantization: false,
              phaserTextureFilter: "nearest",
            },
      );
      expect(metadata.production.runtimeSha256).toMatch(/^[a-f0-9]{64}$/);
    }

    expect(hudHeartMetadata).toMatchObject({
      assetId: "ICO-001",
      canvas: { width: 40, height: 18 },
      frame: {
        width: 20,
        height: 18,
        count: 2,
        states: ["full", "empty"],
      },
      runtime: {
        position: { x: 18, y: 106 },
        gapPx: 2,
        maxLives: 3,
      },
    });
    expect(hudProgressMetadata).toMatchObject({
      assetId: "UI-003",
      canvas: { width: 324, height: 16 },
      runtime: {
        position: { x: 18, y: 134 },
        fillRect: { x: 20, centerY: 142, width: 320, height: 8 },
      },
    });
    expect(hudControlsMetadata).toMatchObject({
      assetId: "UI-004",
      canvas: { width: 76, height: 192 },
      frame: {
        width: 76,
        height: 48,
        count: 4,
        states: ["up", "up-pressed", "down", "down-pressed"],
      },
      runtime: {
        centers: [{ x: 111, y: 572 }, { x: 249, y: 572 }],
        layout: { left: "down", right: "up" },
        displayScale: 1.5,
        hitArea: { width: 114, height: 72 },
        bottomClearancePx: 32,
      },
    });
    expect(hudPanelMetadata).toMatchObject({
      assetId: "UI-008",
      canvas: { width: 360, height: 118 },
      runtime: {
        position: { x: 0, y: 522 },
        fixedToCamera: true,
      },
    });
    expect(hudTitleMetadata).toMatchObject({
      assetId: "UI-009",
      canvas: { width: 242, height: 28 },
      runtime: {
        position: { x: 180, y: 38 },
        origin: { x: 0.5, y: 0.5 },
        fixedToCamera: true,
        text: "BEAUTY BOMB DELIVERY",
      },
    });
    expect(hudPauseMetadata).toMatchObject({
      assetId: "UI-010",
      canvas: { width: 32, height: 64 },
      frame: {
        width: 32,
        height: 32,
        count: 2,
        states: ["idle", "pressed"],
      },
      runtime: {
        center: { x: 332, y: 32 },
        edgeInsets: { top: 16, right: 12 },
        hitArea: { width: 44, height: 44 },
        fixedToCamera: true,
        action: "existing-pause-flow",
      },
    });
    expect(hudExitMetadata).toMatchObject({
      assetId: "UI-011",
      canvas: { width: 32, height: 64 },
      frame: {
        width: 32,
        height: 32,
        count: 2,
        states: ["idle", "pressed"],
      },
      runtime: {
        center: { x: 28, y: 32 },
        edgeInsets: { top: 16, left: 12 },
        fixedToCamera: true,
        behavior: "visual-placeholder",
        futureAction: "exit-game",
      },
    });
    expect(hudSoundMetadata).toMatchObject({
      assetId: "UI-012",
      canvas: { width: 32, height: 64 },
      frame: {
        width: 32,
        height: 32,
        count: 2,
        states: ["idle", "pressed"],
      },
      runtime: {
        center: { x: 332, y: 78 },
        edgeInsets: { right: 12, belowPauseGap: 14 },
        hitArea: { width: 44, height: 44 },
        fixedToCamera: true,
        behavior: "visual-placeholder",
        futureAction: "toggle-sound",
      },
    });
  });

  it("keeps the pause copy in a tail-free local-font comic callout", () => {
    expect(pauseCalloutMetadata).toMatchObject({
      assetId: "UI-015",
      version: "v2",
      status: "integrated",
      canvas: { width: 332, height: 272 },
      copy: "Не тормози! Нужно успеть вовремя :)",
      font: { family: "Press Start 2P", sizePx: 15 },
      production: {
        buildScript: "scripts/build_pause_callout_v2.py",
        assetMode: "authored-low-resolution-pixel-art",
        offlineResizeCount: 0,
        antialiasing: false,
        phaserTextureFilter: "nearest",
      },
      runtime: {
        center: { x: 180, y: 318 },
        fixedToCamera: true,
        tail: "none",
        visibleBounds: { x: 16, y: 184, width: 328, height: 267 },
        continueButtonCenter: { x: 180, y: 334 },
        restartButtonCenter: { x: 180, y: 394 },
      },
    });
    expect(pauseCalloutMetadata.production.runtimeSha256).toMatch(/^[a-f0-9]{64}$/);
  });

  it("keeps the delivery finale on versioned one-resize asset contracts", () => {
    expect(deliveryHouseMetadata).toMatchObject({
      status: "integrated",
      production: {
        buildScript: "scripts/build_delivery_finale_assets_v1.py",
        offlineResizeCount: 1,
        resizeFilter: "nearest-neighbor",
        paletteQuantization: false,
        phaserTextureFilter: "nearest",
      },
    });
    expect(deliveryHouseMetadata.production.designMasterSha256).toMatch(
      /^[a-f0-9]{64}$/,
    );
    expect(deliveryHouseMetadata.production.runtimeSha256).toMatch(
      /^[a-f0-9]{64}$/,
    );

    expect(deliveryGirlMetadata).toMatchObject({
      assetId: "CHR-003",
      version: "v1",
      status: "integrated",
      canvas: { width: 28, height: 44 },
      visibleBounds: { width: 16, height: 40 },
      runtimePlacement: { x: 319, y: 284, originX: 0.5, originY: 1 },
      production: {
        designMaster:
          "visual-references/chr-003-lowpoly-recipient-master-v1.png",
        buildScript: "scripts/build_delivery_girl_lowpoly_v1.py",
        offlineResizeCount: 1,
        resizeFilter: "nearest-neighbor",
        paletteQuantization: false,
        phaserTextureFilter: "nearest",
        runtimeScale: 1,
      },
    });
    expect(deliveryGirlMetadata.production.designMasterSha256).toMatch(
      /^[a-f0-9]{64}$/,
    );
    expect(deliveryGirlMetadata.production.runtimeSha256).toMatch(
      /^[a-f0-9]{64}$/,
    );

    expect(deliveryProductMetadata).toMatchObject({
      assetId: "PRD-003",
      canvas: { width: 32, height: 64 },
      orientation: "vertical; approved roof tube rotated clockwise",
      production: {
        designMaster: "visual-references/veh-001-courier-clean-concept-v7.png",
        buildScript: "scripts/build_delivery_product_v1.py",
        offlineResizeCount: 1,
        resizeFilter: "nearest-neighbor",
        phaserTextureFilter: "nearest",
        runtimeSource: "approved master; not screenshot or runtime sprite",
      },
    });

    expect(deliveryCalloutMetadata).toMatchObject({
      assetId: "UI-016",
      version: "v5",
      canvas: { width: 332, height: 104 },
      runtimePosition: { x: 14, y: 338, originX: 0, originY: 0 },
      copy: "Большое спасибо! Теперь можешь забрать награду!",
      tailTarget: "CHR-001 v2",
      tailPointLocal: { x: 276, y: 0 },
      tailTargetRuntime: { x: 290, y: 324 },
      tailPlacement: "UI-013 geometry reflected upward; continuous top join",
      production: {
        buildScript: "scripts/build_delivery_finale_ui_v5.py",
        offlineResizeCount: 0,
        antialiasing: false,
        phaserTextureFilter: "nearest",
        singleContinuousJoin: true,
        highlightCrossesTail: false,
        pinkTailOutline: false,
      },
    });
    expect(deliveryClaimMetadata).toMatchObject({
      assetId: "UI-017",
      frame: { width: 168, height: 36, count: 3 },
      runtimeCenter: { x: 180, y: 466 },
      input: ["pointer-anywhere", "Enter", "Space"],
    });
    expect(rewardCouponMetadata).toMatchObject({
      assetId: "UI-018",
      version: "v5",
      status: "integrated",
      canvas: { width: 304, height: 456 },
      runtimePlacement: { x: 180, y: 320, originX: 0.5, originY: 0.5 },
      master: {
        path: "visual-references/ui-018-reward-coupon-master-v5.png",
        transparentBackground: true,
        alpha: "binary; exterior border-connected near-white component only",
      },
      runtime: {
        path: "public/assets/game/ui/ui-018-reward-coupon-v5.png",
        dimensions: { width: 304, height: 456 },
        phaserTextureFilter: "nearest",
      },
      wordmark: {
        text: "beautybomb",
        logicalTop: 100,
      },
      build: {
        buildScript: "scripts/build_reward_coupon_v5.py",
        resizeCount: 1,
        resizeFilter: "nearest-neighbor",
      },
      liveOverlay: {
        couponCode: "XQZ-20476",
        tearOffArea: "empty",
      },
    });
    expect(rewardCouponMetadata.master.sha256).toMatch(
      /^[a-f0-9]{64}$/,
    );
    expect(rewardCouponMetadata.runtime.sha256).toMatch(
      /^[a-f0-9]{64}$/,
    );
    expect(defeatCalloutMetadata).toMatchObject({
      assetId: "UI-006",
      version: "v1",
      canvas: { width: 332, height: 272 },
      copy: "ДТП!\nДавай еще раз!",
      font: { family: "Press Start 2P", sizePx: 15 },
      production: {
        buildScript: "scripts/build_defeat_callout_v1.py",
        styleSource: "UI-015 v2 exact panel geometry and palette",
        offlineResizeCount: 0,
        antialiasing: false,
        phaserTextureFilter: "nearest",
      },
      runtime: {
        center: { x: 180, y: 318 },
        restartButtonCenter: { x: 180, y: 394 },
        restartButtonLabel: "заново",
        restartFlow: "existing resetRun",
      },
    });
    expect(deliveryDestinationCityMetadata).toMatchObject({
      assetId: "ENV-009",
      version: "v3",
      canvas: { width: 2048, height: 512 },
      runtime: {
        tileScale: { x: 0.36, y: 0.55078125 },
        depth: 1,
        switchTrigger: "delivery progress complete",
        startOffsetTexturePx: 526,
        reducedMotionFinalOffsetTexturePx: 701,
        expectedFinalHouseCenterX: 297,
      },
      production: {
        chromaMasterSha256: expect.stringMatching(/^[a-f0-9]{64}$/),
        alphaMasterSha256: expect.stringMatching(/^[a-f0-9]{64}$/),
        offlineResizeCount: 1,
        resizeFilter: "nearest-neighbor",
        phaserTextureFilter: "nearest",
      },
      integration: {
        independentHouseSprite: false,
        sharedCityTransform: true,
        continuousSidewalk: true,
        rectangularHouseBackdrop: false,
        doorstepGapFilled: true,
        curbSampleBox: [1451, 506, 1493, 512],
        curbDestination: [1493, 506],
      },
    });
  });
});
