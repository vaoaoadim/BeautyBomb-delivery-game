# Asset Manifest

Status values: `specified`, `concept`, `approved`, `produced`, `integrated`, `verified`.

The manifest describes deliverables, not empty folders. Create runtime directories only when the first asset in that group is exported.

## Batch A — hero kit

This is the next production batch and the visual quality gate for all later art.

| ID | Asset | Native canvas / frames | Deliverables | Status |
|---|---|---:|---|---|
| `BRD-001` | Pixel BeautyBomb wordmark | `64 × 18`, static | master PNG, gameplay PNG | concept |
| `PRD-001` | Waterbomb tube, horizontal | `72 × 24`, static | gameplay PNG, roof-aligned origin guide | concept |
| `PRD-002` | Waterbomb tube, hero | `128 × 192`, static | detailed transparent PNG | specified |
| `VEH-001` | Courier van driving | `104 × 80`, `4` frames | sprite sheet, origin/collision guide | concept |
| `VEH-002` | Courier van hit | `104 × 80`, `4` frames | sprite sheet | specified |
| `VEH-003` | Courier van arrival | `104 × 80`, `6–8` frames | sprite sheet | specified |
| `VFX-001` | Hit particles | `32 × 32`, `4` frames | sprite sheet | specified |
| `OBS-001` | Compact hatchback | `80 × 56`, `2–4` frames | sprite sheet, collision guide | specified |
| `OBS-002` | Sedan | `88 × 56`, `2–4` frames | sprite sheet, collision guide | specified |

Batch A gate:

- first approve one static near-lane courier pose with logo and product;
- then approve one far-lane scale check beside both obstacle silhouettes;
- only then produce the animation frames.

Current review master: `visual-references/veh-001-courier-near-concept-v1.png`. It is a high-resolution concept, not a runtime sprite export.

## Batch B — complete traffic set

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `OBS-003` | Taxi-like box car | `82 × 58`, `2–4` frames | specified |
| `OBS-004` | Small delivery van | `92 × 62`, `2–4` frames | specified |
| `OBS-005` | Sporty coupe | `86 × 52`, `2–4` frames | specified |
| `OBS-006` | Traffic color variants | existing silhouettes, max `2` variants each | specified |

## Batch C — environment and parallax

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `ENV-001` | Sky and block clouds | `512 × 180`, tileable | specified |
| `ENV-002` | Far skyline | `512 × 128`, tileable | specified |
| `ENV-003` | Mid city | `512 × 160`, tileable | specified |
| `ENV-004` | Near street strip A | `768 × 220`, tileable | specified |
| `ENV-005` | Near street strip B | `768 × 220`, tileable | specified |
| `ENV-006` | Road and lane markings | `512 × 240`, tileable | specified |
| `ENV-007` | Street props atlas | `512 × 256` atlas | specified |
| `ENV-008` | Foreground accents | `512 × 128`, sparse tile | specified |

Environment gate: assemble a still `360 × 640` gameplay frame with all layers and verify courier/traffic contrast before animating parallax.

## Batch D — UI and bitmap type

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `FNT-001` | Bitmap UI alphabet | glyph cell documented at export | specified |
| `ICO-001` | HUD icon set | `16 × 16` and `24 × 24` | specified |
| `UI-001` | Yellow primary button, 9-slice | `96 × 48` source | specified |
| `UI-002` | White/lavender sticker panel, 9-slice | `160 × 120` source | specified |
| `UI-003` | Progress bar | `320 × 12` source | specified |
| `UI-004` | Touch up/down controls | `64 × 48` each, pressed state | specified |
| `UI-005` | Intro composition | `360 × 640` layout masters | specified |
| `UI-006` | Defeat composition | `360 × 640` layout masters | specified |

Required icon coverage: heart, progress/route, sound, pause, up, down, retry, home, parcel, star, and location pin.

## Batch E — delivery finale

| ID | Asset | Native canvas / frames | Status |
|---|---|---:|---|
| `DST-001` | Destination house/storefront | max `240 × 220`, static | specified |
| `CHR-001` | Waiting girl idle | `64 × 88`, `4` frames | specified |
| `CHR-002` | Waiting girl greeting | `64 × 88`, `6` frames | specified |
| `VFX-002` | Delivery success particles | `64 × 64`, `6` frames | specified |
| `UI-007` | Victory composition | `360 × 640` layout masters | specified |

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
- exported runtime path;
- native width/height and frame count;
- origin/pivot and collision guide when relevant;
- palette tokens used;
- frame rate and loop behavior;
- license/source note;
- native-size preview;
- in-game screenshot at all required lane scales;
- owner approval status.

## Immediate next action

Produce one static `VEH-001` near-lane concept containing `BRD-001` and `PRD-001`. Do not animate or build the remaining atlas until that silhouette, perspective, logo simplification, and roof-mounted product are approved.
