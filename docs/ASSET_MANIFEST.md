# Asset Manifest

Status values: `specified`, `concept`, `approved`, `produced`, `integrated`, `verified`.

The manifest describes deliverables, not empty folders. Create runtime directories only when the first asset in that group is exported.

## Batch A — hero kit

This is the next production batch and the visual quality gate for all later art.

| ID | Asset | Native canvas / frames | Deliverables | Status |
|---|---|---:|---|---|
| `BRD-001` | Pixel BeautyBomb wordmark | `64 × 18`, static | master PNG, gameplay PNG | approved |
| `PRD-001` | Waterbomb face-cream tube, horizontal | `72 × 24`, static | gameplay PNG, roof-aligned origin guide | concept |
| `PRD-002` | Waterbomb tube, hero | `128 × 192`, static | detailed transparent PNG | specified |
| `VEH-001` | Courier van driving | `208 × 160`, `4` frames | sprite sheet, origin/collision guide | integrated |
| `VEH-001-INTRO` | Courier van intro idle | `208 × 160`, `4` frames | master-derived sheet: drive body/tube motion with fixed wheel hubs | integrated |
| `VEH-002` | Courier van hit | `208 × 160`, `4` frames | sprite sheet | specified |
| `VEH-003` | Courier van arrival | `208 × 160`, `6–8` frames | sprite sheet | specified |
| `VFX-001` | Hit particles | `32 × 32`, `4` frames | sprite sheet | specified |
| `OBS-001` | Pink compact hatchback | `80 × 56`, `4` frames | sprite sheet, collision guide | integrated |
| `OBS-002` | Yellow sedan | `88 × 56`, `4` frames | sprite sheet, collision guide | integrated |
| `OBS-003` | Green boxy wagon | `84 × 58`, `4` frames | sprite sheet, collision guide | integrated |

Batch A gate:

- the owner approved the clean static courier pose with no text, logos, icons, or decorative prints on either the van body or roof tube;
- the far-, middle-, and near-lane scale checks passed with the fixed body-only collider;
- the derived four-frame drive sheet is now integrated; obstacle wheel cycles remain gated on their own approved static masters.

Previous candidates remain as historical evidence. The active design master is `visual-references/veh-001-courier-clean-concept-v7.png`: it preserves the turquoise side-view courier, broad ribbed white tube cap, roof mounts, and clean product silhouette while removing all text and printed graphics from the van and tube.

Native static scale proof: `public/assets/game/vehicles/veh-001-courier-static-v1.png` with metadata in `veh-001-courier-static-v1.json`. Review guides: `visual-references/veh-001-courier-static-v1-preview-8x.png` and `visual-references/veh-001-courier-static-v1-guide-8x.png`. It is retained as a historical scale-study reference.

The low-resolution `veh-001-courier-clean-static-v2.png` is retained only as diagnostic evidence of the rejected redraw pipeline. The active static master frame is `public/assets/game/vehicles/veh-001-courier-clean-static-v5.png` with adjacent metadata. It crops transparent padding from the `v7` alpha master and performs exactly one nearest-neighbor resize into a `208 × 160` texture, then renders at `0.5` base scale so world size, origin, baselines, and collider behavior remain unchanged.

The integrated drive sheet is `public/assets/game/vehicles/veh-001-courier-clean-drive-v6.png` with adjacent metadata. Its four fixed-canvas frames are derived from the `v7` master, not from a preview or runtime file; frame zero is byte-identical to the clean static v5 texture. Review guides: `visual-references/veh-001-courier-clean-static-v5-preview-4x.png` and `visual-references/veh-001-courier-clean-drive-v6-preview-4x.png`. The earlier Waterbomb-brand v6/v4/v5 files remain historical evidence and are not preloaded by the game.

The earlier `obs-001/002/003-*-static-v1.png` files and `obstacle-vehicles-static-v1-preview-4x.png` remain historical comparison evidence only; they are no longer the game integration.

The owner approved the separate transparent v2 masters `visual-references/obs-001-pink-hatchback-concept-v2.png`, `visual-references/obs-002-yellow-sedan-concept-v2.png`, and `visual-references/obs-003-green-wagon-concept-v2.png`. Their matching `-source.png` files preserve the original generation. `scripts/build_obstacle_static_v2.py` removes only alpha noise below 16, crops transparent padding, and performs exactly one nearest-neighbor resize into the static runtime textures and collision guides. The combined static review is `visual-references/obstacle-vehicles-static-v2-comparison.png`.

The owner approved the immutable v2 drive sheets `obs-001-pink-hatchback-drive-v2.png`, `obs-002-yellow-sedan-drive-v2.png`, and `obs-003-green-wagon-drive-v2.png`, with adjacent metadata. `scripts/build_obstacle_drive_v2.py` derives their four 7 FPS frames from the approved high-resolution masters; frame zero is byte-identical to the matching static v2 export, while only the wheel hubs rotate. Review sheet: `visual-references/obstacle-vehicles-drive-v2-comparison.png`. Any visual change requires a new versioned master and decision.

Approved-size review candidate: `visual-references/vehicle-lane-scale-check-v2.png`. It replaces the undersized `v1` comparison with wheel baselines `350/424/508`, visual scales `1.12/1.22/1.32`, and independently reduced body colliders. The green wagon uses an additional `1.18` optical multiplier so it is not smaller than the pink hatchback. The Waterbomb tube remains visible but is intentionally excluded from the courier collision area.

## Batch B — complete traffic set

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `OBS-004` | Small delivery van | `92 × 62`, `2–4` frames | specified |
| `OBS-005` | Sporty coupe | `86 × 52`, `2–4` frames | specified |
| `OBS-006` | Traffic color variants | existing silhouettes, max `2` variants each | specified |

## Batch C — environment and parallax

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `ENV-001` | Sky and block clouds | `2048 × 512` direct POT cycle | integrated v4 |
| `ENV-002` | Far skyline | included in unified `ENV-004` composition | approved |
| `ENV-003` | Mid city | included in unified `ENV-004` composition | approved |
| `ENV-004` | Coherent neighborhood city, skyline through sidewalk | `2048 × 512` approved-alpha POT cycle | integrated v8 |
| `ENV-005` | Near street strip B | `768 × 220`, tileable | specified |
| `ENV-006` | Road, lane markings, and white edge curbs | `1792 × 406` v3 panorama in a `2048 × 512` POT cycle | integrated road v6 |
| `ENV-007` | Street props atlas | `512 × 256` atlas | specified |
| `ENV-008` | Foreground accents and control-safe pavement | `2048 × 128` POT cycle / `1792 × 128` neutral pavement + `128 px` safe gutters | integrated v4 |

The owner approved `visual-references/env-001-parallax-seamless-v3.png` as the immutable route-parallax master on 2026-08-21. It anchors the road at `y=282–522` and the lane separators at `y=363/437`; its outer safe zones contain no foreground landmarks. `scripts/build_environment_parallax_v3.py` asserts every approved-master hash, uses master crops and alpha extraction where needed, performs one nearest-neighbor resize per content strip, and adds a mirrored `128 px` neutral source gutter around the direct panorama on each POT canvas. Buildings, trees, storefronts, and lamps are never mirrored. `ENV-008` remains derived from the approved v2 pavement-only master. The integrated layer set is `ENV-001–004`, `ENV-006`, and `ENV-008`; `src/game/content/environmentParallax.json` is the shared motion and placement source. Metadata is adjacent to each PNG. Review evidence: `visual-references/environment-parallax-v3-master-runtime-comparison.png` and `visual-references/environment-parallax-v3-loop-review.png`.

The owner approved `visual-references/env-001-parallax-coherent-v4-candidate.png` as the immutable v4 route master on 2026-08-21. Its three `724 px` source segments form the authored sequence `A→B→C→A`, with no empty edge gutters or mirrored landmarks. The first integration split the flat master into three independently scrolling polygon masks; in motion this displaced connected towers, facades, trees, and lamps. The corrected `scripts/build_environment_parallax_v4.py` locks the same master hash and exports one unified skyline-to-sidewalk `ENV-004` city texture instead. `ENV-002` and `ENV-003` remain represented inside that approved composition but have no standalone runtime motion. `ENV-006` reuses the approved v3 road crop and exact `y=282–522` band, while neutral `ENV-008` retains its safe-gutter construction. Review evidence: `visual-references/environment-parallax-v4-master-runtime-comparison.png`, `visual-references/environment-parallax-v4-mask-review.png`, `visual-references/environment-parallax-v4-loop-review.png`, and `visual-references/environment-parallax-v4-motion-review.png`.

Environment runtime v5 preserves the immutable v4 A/B/C master and replaces only the defective vertically filled city polygon. `scripts/build_environment_parallax_v5.py` flood-fills adaptive sky colors only from the outer boundary, inverts that connected background, and retains the single component reaching the city anchor band. This removes detached clouds and sky-colored columns while preserving cyan pixels enclosed by architectural outlines. The sky, approved v3 road, and neutral foreground v5 PNGs are byte-identical to their v4 siblings. Review evidence: `visual-references/environment-parallax-v5-alpha-review.png`, `visual-references/environment-parallax-v5-before-after.png`, `visual-references/environment-parallax-v5-motion-review.png`, `visual-references/environment-parallax-v5-seam-review.png`, and `visual-references/environment-parallax-v5-loop-review.png`.

Environment runtime v6 replaces only `ENV-004` with the approved `visual-references/env-001-parallax-neighborhood-v6-alpha-master.png`. The city is a single coherent composition with structurally readable, varied two-to-five-storey street fronts, medium blocks, a restrained distant skyline, trees, roof equipment, awnings, and one straight sidewalk baseline. `scripts/build_environment_city_v6.py` locks the RGBA master hash, crops complete street edges, performs one nearest-neighbor runtime resize, and verifies the direct POT loop. `ENV-001`, `ENV-006`, and `ENV-008` remain byte-identical to v5, so the existing sky, full-height road geometry, foreground, speeds, depths, and gameplay behavior are unchanged. Review evidence: `visual-references/environment-parallax-v6-alpha-review.png`, `visual-references/environment-parallax-v6-before-after.png`, `visual-references/environment-parallax-v6-motion-review.png`, `visual-references/environment-parallax-v6-seam-review.png`, and `visual-references/environment-parallax-v6-loop-review.png`.

Environment runtime v7 corrects the v6 export boundary without changing the approved city master. The former source box ended at `x=1907` inside the terminal beige building; the v7 source box ends at `x=2023`, after that complete facade and its sidewalk. The next cycle therefore begins with the complete first orange facade instead of following a clipped wall fragment. `scripts/build_environment_city_v7.py` preserves the existing alpha, single-layer motion, `2048 × 512` POT canvas, `0.56` multiplier, sky, road, foreground, depths, and gameplay geometry. Review evidence: `visual-references/environment-parallax-v7-motion-review.png`, `visual-references/environment-parallax-v7-seam-review.png`, and `visual-references/environment-parallax-v7-loop-review.png`.

Environment runtime v8 removes the remaining cyan street-level interval at the corrected v7 join. Its source period is `[123, 0, 2005, 693]`: the first column begins on the complete first orange facade boundary and the last column ends on the complete terminal beige facade boundary. The cyclic join therefore places two finished walls and their sidewalk sections directly beside one another, without inserting or generating a new object. `scripts/build_environment_city_v8.py` preserves the immutable city master, existing alpha, `2048 × 512` POT canvas, `0.56` multiplier, sky, road, foreground, depths, and gameplay geometry. Review evidence: `visual-references/environment-parallax-v8-motion-review.png`, `visual-references/environment-parallax-v8-seam-review.png`, and `visual-references/environment-parallax-v8-loop-review.png`.

`ENV-006 road v6` replaces only the bright-green top and bottom curb palette with neutral white grayscale shading while preserving the approved v3 source crop, one nearest-neighbor resize, asphalt, lane markings, `2048 × 512` POT construction, `y=282–522` placement, `1.00` multiplier, and collision geometry. `scripts/build_environment_road_v6.py` applies the deterministic color transform only to content rows `0–5` and `388–397`, verifies the cyclic edge, and asserts unchanged hashes for `ENV-001`, `ENV-004`, and `ENV-008`. Review evidence: `visual-references/environment-road-v6-before-after.png`, `visual-references/environment-road-v6-motion-review.png`, and `visual-references/environment-road-v6-seam-review.png`.

## Batch D — UI and bitmap type

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `FNT-001` | Bitmap UI alphabet | glyph cell documented at export | specified |
| `FNT-002` | Press Start 2P Cyrillic intro build source | local TTF + SIL OFL license; no runtime load | verified |
| `ICO-001` | HUD icon set; life-heart subset | `20 × 18`, full/empty | integrated (heart v1 candidate) |
| `UI-001` | Yellow primary button, 9-slice | `96 × 48` source | specified |
| `UI-002` | White/lavender sticker panel, 9-slice | `160 × 120` source | specified |
| `UI-003` | Progress bar | `324 × 16`, static frame + runtime fill | integrated (v1 candidate) |
| `UI-004` | Touch down/up controls | `76 × 48`, `4` normal/pressed frames | integrated (v2 candidate; v1 retained) |
| `UI-005` | Intro composition | `360 × 640` layout masters | approved |
| `UI-006` | Defeat composition | `360 × 640` layout masters | specified |
| `UI-008` | Lower control console | `360 × 118`, fixed | integrated (v1 candidate) |
| `UI-009` | Gameplay title | `242 × 28`, static | integrated (v1 candidate) |
| `UI-010` | Top-right pause control | `32 × 32`, `2` idle/pressed frames | integrated (`v2`; v1 retained) |
| `UI-011` | Top-left exit placeholder | `32 × 32`, `2` idle/pressed frames | retained, not rendered |
| `UI-012` | Top-right sound placeholder control | `32 × 32`, `2` idle/pressed frames | integrated (`v2`; v1 retained) |
| `UI-013` | Russian intro comic callout | `332 × 207`, static | verified (`v2` runtime; v1 retained) |
| `UI-014` | Intro `ЖМИ` prompt | `112 × 36`, `3` color frames | verified |
| `UI-015` | Pause comic callout | `332 × 272`, static | integrated (`v2`; v1 retained) |

Required icon coverage: heart, progress/route, sound, pause, up, down, retry, home, parcel, star, and location pin.

The branded HUD v1 candidate is authored directly on the runtime pixel grid by `scripts/build_hud_ui_v1.py`; it performs no resize, antialiasing, or palette quantization. Runtime files and adjacent metadata live in `public/assets/game/ui/`. `UI-004` v2 is independently authored by `scripts/build_touch_controls_v2.py` on the same immutable `76 × 48` runtime grid: four normal/pressed frames use the project yellow face, solid black arrows, a restrained Beauty Bomb pink extrusion, and no micro-detail. It renders at `1.5×` with matching `114 × 72` hit areas centered at `111/249, 572`; down is left and up is right, while the lower panel keeps `32 px` of bottom clearance. `UI-010` and `UI-012` v2 derive from the generated immutable `visual-references/ui-005-utility-buttons-master-v1.png` through one nearest-neighbor resize per frame. Both retain a `32 × 32` visual grid and a `44 × 44` hit area; pause is at `332, 32`, sound is directly below at `332, 78`. Pause enters the existing pause flow; sound remains the documented visual-only placeholder until a real audio contract exists. Review evidence: `visual-references/ui-utility-buttons-v2-review.png`.

`UI-009` is the one-line `BEAUTY BOMB DELIVERY` gameplay title authored by the same deterministic HUD script. Its acid-yellow face, deep-violet outline, hot-pink lower-right extrusion, and small cyan-white highlights are drawn directly on a transparent `242 × 28` runtime grid. Phaser renders the PNG at native size with `NEAREST`, centered at `x=180, y=38`, six logical pixels below the utility-button centerline; no system font or runtime text effect is involved. Review evidence: `visual-references/ui-game-title-v1-review.png`.

`UI-015` v2 is a tail-free pause-window callout, authored directly at `332 × 272` by `scripts/build_pause_callout_v2.py`; v1 is retained unchanged. It reproduces `UI-013` v3's stepped body and its exact `+3,+4 px` pink extrusion while extending the body vertically for the existing controls. Its three rasterized Press Start 2P lines read `Не тормози! Нужно успеть вовремя :)`; Phaser renders it with `NEAREST` at `x=180, y=318`. The unchanged continue/restart buttons sit at `y=334` and `y=394` wholly inside the lavender interior. No resize, antialiasing, runtime font load, or new pause-state is introduced.

The owner approved `visual-references/ui-005-intro-composition-v1.png` and its adjacent layout metadata as the `UI-005` composition master. `scripts/build_intro_ui_v1.py` locks that master and the repository-local `visual-references/fonts/press-start-2p/PressStart2P-Regular.ttf` source, whose `OFL.txt` permits the build use. The script performs zero resize, antialiasing, or palette quantization and exports the immutable `UI-013` v1 source to `public/assets/game/ui/ui-013-intro-callout-v1.png` plus the three-frame `UI-014` sheet to `public/assets/game/ui/ui-014-intro-tap-v1.png`; adjacent JSON files document dimensions and frames. `scripts/build_intro_callout_v3.py` deterministically derives the integrated `UI-013` v3 runtime by replacing only the 42 exact-yellow pixels of the lower-right decorative mark with the opaque lavender bubble surface. The font is used only during deterministic raster generation and is not downloaded or loaded by the browser. `scripts/build_courier_clean_asset.py` also produces `VEH-001-INTRO` directly from the approved `v7` courier master: its body and tube use the approved four-frame drive motion, while both wheel hubs are composited from the static source in every frame. Review evidence: `visual-references/ui-intro-v1-review.png`, `visual-references/ui-intro-stage4-waiting-360x640.png`, `visual-references/ui-intro-stage4-transition-360x640.png`, and `visual-references/ui-intro-stage4-playing-360x640.png`.

## Batch E — delivery finale

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `DST-001` | Solitary pink arrival house | `176 × 176`, static | integrated v1 |
| `ENV-009` | Unified delivery-destination city panorama | `2048 × 512`, finale-bounded | integrated v3 |
| `CHR-001` | Waiting blonde girl | `28 × 44`, static | integrated v2 |
| `CHR-002` | Waiting girl greeting | `64 × 88`, `6` frames | specified |
| `CHR-003` | Low-poly blonde recipient | `28 × 44`, static | integrated v1 |
| `VFX-002` | Delivery success confetti | bounded Phaser pixel rectangles | integrated procedural v1 |
| `UI-007` | Victory composition | `360 × 640` layout masters | specified |
| `UI-016` | Delivery thank-you callout | `332 × 104`, static | integrated v5 |
| `UI-017` | `<ЗАБРАТЬ>` prompt | `168 × 36`, `3` frames | integrated v1 |
| `UI-018` | Delivery reward coupon background | `304 × 456`, static | integrated v4 |
| `PRD-003` | Vertical delivery-transfer cream | `32 × 64`, static | integrated v1 |

`DST-001`, `CHR-001`, and `CHR-003` retain separate immutable generated masters. The integrated recipient is `CHR-003` v1, built from the compact approved `112 × 176` master `visual-references/chr-003-lowpoly-recipient-master-v1.png`; `scripts/build_delivery_girl_lowpoly_v1.py` verifies its SHA-256 and performs one nearest-neighbor export to the final `28 × 44` canvas, avoiding repeated or fractional resizing. The previous `CHR-001` assets remain versioned in the repository and are not overwritten. The standalone house remains a design reference only. `ENV-009` v3 is derived by `scripts/build_delivery_destination_city_v3.py` from the immutable unified destination master `visual-references/env-009-delivery-destination-city-alpha-master-v2.png`; that master already contains the house as a complete city lot. The runtime export performs one nearest-neighbor resize, then copies the immediately adjacent approved curb sample into only the `42 × 6` doorstep interval with opaque alpha, so no sky-colored gap remains and no facade is regenerated. `UI-016` v5 is authored directly on its final pixel grid by `scripts/build_delivery_finale_ui_v5.py`; its existing tail geometry remains spatially aligned because `CHR-003` retains the approved `290,324` placement in this stage. The tail keeps the deep-violet outline and lavender interior but receives no pink shadow; the body retains its existing pink extrusion. `UI-017` remains the v1 three-frame sheet from `scripts/build_delivery_finale_ui_v1.py`. Both use the repository-local Press Start 2P source and no runtime font. `UI-018` v3 preserves the owner-approved flat-palette, binary-alpha v2 silhouette and adds a deterministic upper-body brand layer through `scripts/build_reward_coupon_v3.py`: an enlarged `BEAUTY BOMB` wordmark in the exact `UI-009` treatment, plus hearts, starbursts, neon ribbons, cosmic grids, and a pixel gamepad inspired by the official Beauty Bomb site. The versioned `1216 × 1824` master is resized once with nearest-neighbor to `304 × 456`; v1 and v2 remain untouched. The lower tear-off area, code, copy icon, confirmation, and tear-off text remain unchanged live Phaser UI. `PRD-003` is built by `scripts/build_delivery_product_v1.py` from the product region of the immutable `veh-001-courier-clean-concept-v7.png` master, not from a screenshot or runtime sprite. Finale timings, anchors, and depth ordering are adjacent in `src/game/content/deliveryFinale.json`.

`UI-018` v4 keeps the v3 composition and extends its deterministic brand pattern through the full main ticket body, including the area below the live code row. The added pixel constellation, diamonds, neon waves, and mini-confetti cadence stop above the existing dotted tear line; the lower text area remains pixel-identical to v3. The code, copy control, reward flow, and popup layout are unchanged.

## Batch F — later prize system

Not part of the next asset-production phase.

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `RWD-001` | Prize wheel | max `300 × 300`, static plus pointer states | specified |
| `RWD-002` | Discount badges `20/25/30/35%` | `96 × 64` each | specified |
| `RWD-003` | Fictional promo-code panel | `300 × 160` | specified |
| `VFX-003` | Reward celebration | `96 × 96`, `8` frames | specified |

## Runtime target structure

```text
public/assets/game/
  brand/
  vehicles/
  environment/
  ui/
  characters/
  vfx/
```

Do not create these directories until their first approved exported asset exists.

## Per-asset handoff checklist

- asset ID and version;
- editable master location;
- approved-master hash or another immutable source identifier;
- exported runtime path;
- native width/height and frame count;
- deterministic export script, resize count, resize filter, and palette-quantization status;
- origin/pivot and collision guide when relevant;
- explicit Phaser texture filter and every runtime scale;
- palette tokens used;
- frame rate and loop behavior;
- license/source note;
- native-size preview;
- in-game screenshot at all required lane scales;
- master/runtime comparison sheet with alpha-edge and silhouette review;
- owner approval status.

## Immediate next action

Create and review the `OBS-004` small delivery-van static master; its drive cycle may be derived only after that static pose is approved.
