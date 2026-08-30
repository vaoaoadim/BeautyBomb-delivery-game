# Architecture

## Stack

- TypeScript in strict mode.
- Vite for development and production builds.
- Phaser 3.90 for rendering, input, scene lifecycle, audio, and pixel-art scaling.
- Vitest for deterministic game-domain tests.
- No frontend framework, state library, backend, database, or animation dependency in the demo baseline.

Phaser 3 is selected instead of Phaser 4 for the first version because its API and ecosystem are mature and sufficient for a small 2D lane game. The choice can be revisited only if the greybox exposes a concrete limitation.

## Design principles

1. Game rules stay independent from rendering.
2. Phaser is an adapter, not the source of business truth.
3. Tunable content is data, not scattered scene constants.
4. Integration is isolated from the standalone demo.
5. Production prize issuance is server-authoritative.
6. The smallest complete module wins over speculative abstractions.

## Target structure

```text
src/
  app/                 application bootstrap and lifecycle
  game/
    content/           tunable campaign and gameplay data
    domain/            pure state transitions and game rules
    scenes/            Phaser scene adapters
    systems/           spawning, movement, collision and progress
    config.ts          locked viewport and timing constants
  integration/         host-page and future prize API boundary
  ui/                  modal/HUD DOM only when canvas UI is insufficient
  main.ts
  styles.css
public/assets/
  brand/
  game/
  audio/
tests/
```

Create a folder only when its first real module is added; the tree above is a boundary map, not a requirement to produce empty abstractions.

## Runtime flow

```text
Host or standalone page
        |
        v
Application bootstrap
        |
        v
Phaser scenes <----> pure game state and rules
        |
        v
Integration adapter
        |
        +---- demo prize provider (local, fictional)
        |
        +---- production prize API (future, client-owned)
```

## Game states

`boot -> preload -> intro -> playing -> paused | defeated | delivered -> prize -> complete`

Rules:

- only `playing` advances delivery progress;
- losing a life enters temporary invulnerability;
- zero lives enters `defeated`;
- reaching full progress enters `delivered`;
- a prize request can occur once per completed run;
- restarting creates a fresh run state.

`delivered` remains the single domain authority for a successful route. The Phaser scene owns only the local presentation sequence `inactive -> finish-road -> arrival-transition -> product-transfer -> reward-prompt -> complete`; it cannot issue a prize or create a second delivered state. Tunings and logical `360 × 640` anchors live in `src/game/content/deliveryFinale.json`, while `src/game/content/deliveryFinale.ts` exposes guarded pure transitions for deterministic tests. Claiming after the transfer hands control back to the existing reward-flow contract exactly once.

## Integration boundary

Preferred production embedding is an iframe-backed widget because it isolates canvas sizing, dependencies, styles, and failures from the client's website.

The public portfolio embed is deployed as a separate static Vite project on
Vercel. Its response permits framing only by the configured portfolio origin
through `Content-Security-Policy: frame-ancestors`; the existing Sites build
remains a standalone publication and is not used as the iframe source.

The future host contract should expose:

- commands: open, close, pause, resume, configure campaign;
- events: ready, started, hit, defeated, delivered, prize received, closed;
- identifiers: widget version and campaign ID;
- no secret, session token, or real promo code in logs.

The standalone portfolio demo uses the same interface with a local adapter.

## Rendering and performance

- Logical scene coordinates remain `360 × 640`; gameplay, collision, layout, and asset manifests use this coordinate space.
- The renderer uses a `2×` backing canvas (`720 × 1280`) and a matching camera zoom with a top-left origin. CSS presents it at the existing portrait size, so the game gains two physical samples per logical pixel without changing gameplay geometry or pointer mapping.
- Scale mode remains fit and center. The final canvas uses normal browser resampling instead of forcing a second nearest-neighbor pass over the whole composed frame.
- Authored pixel textures keep explicit `NEAREST` filtering. A texture that is deliberately animated with fractional scale may use `LINEAR` only after an in-browser comparison proves that it removes stroke crawling without changing its approved silhouette; `UI-014` is the first documented exception.
- Pixel art and rounded camera pixels remain enabled; mipmaps are not introduced.
- Parallax layers reuse tileable textures.
- In Phaser 3.90, cyclic `TileSprite` assets use power-of-two runtime canvases, explicit useful-content bounds, and a finite texture-space repeat period; the Scene renders viewport-sized TileSprites and scrolls them through `tilePositionX`.
- Collision boxes are simpler than visible sprites.
- Target: stable 60 FPS, graceful 30 FPS on slower mobile devices.
- Initial budgets are targets, not release claims: JavaScript under 350 KB gzip excluding lazy audio, initial critical assets under 1.5 MB, no layout shift on the host page.

## Art asset contract

- `docs/ART_BIBLE.md` owns perspective, pixel grid, palette, shape, UI, parallax, animation, and export rules.
- `docs/ASSET_MANIFEST.md` owns stable asset IDs, production batches, native canvases, status, and handoff requirements.
- Editable masters do not belong in runtime atlases.
- Runtime asset directories are created only when their first approved export exists.
- Animated frames keep fixed bounds and origins; Phaser must not compensate for inconsistent art at runtime.

### Approved-master pipeline

An owner-approved visual master is immutable and is the visual source of truth for that asset version. Approval authorizes deterministic export; it does not authorize a new generative variation, a redraw from memory, or replacement geometry. A design change requires a new master version and a recorded decision before runtime work resumes.

The only valid production path is:

```text
approved master
  -> deterministic background/alpha extraction when needed
  -> one production resize/export
  -> lossless runtime texture plus metadata
  -> explicit Phaser preload and texture filter
  -> documented lane/runtime scale
  -> in-game review at the 360 x 640 viewport
```

Rules:

- previews, guide sheets, screenshots, and already-downscaled runtime files are review evidence only and must never become export inputs;
- deterministic code-authored pixel UI may be produced directly on its final runtime grid with zero resize and no antialiasing while it is a review candidate; owner approval freezes that version's runtime hashes, and later visual edits require a new version rather than overwriting the approved files;
- preserve source aspect ratio, silhouette, palette, component placement, and alpha bounds; palette quantization or geometry simplification requires separate owner approval;
- perform at most one offline resize from the approved master to the runtime texture; never chain downscale/upscale operations;
- classify the asset before export as either authored low-resolution pixel art or high-detail pixel-style raster, and record that mode, native dimensions, resize filter, runtime scale, origin, baseline, collider, source path, and export script in adjacent metadata;
- set the concrete Phaser texture filter explicitly. `NEAREST` is required for authored pixel art and for the current courier candidate; a different filter requires a visual comparison and a recorded decision;
- cyclic environment assets may construct a seam-safe period from approved pixels only when the construction is deterministic, versioned, documented in adjacent metadata, and does not add generated geometry or a second resize; foreground landmarks must remain a direct panorama, while mirroring is permitted only inside a documented object-free edge gutter;
- environment alpha extraction must classify removable background by connectivity to the master boundary or use an explicit versioned matte; broad color deletion and vertically filled skyline profiles are forbidden when clouds and cyan architecture share the source image;
- a flat coherent-city master remains one skyline-to-sidewalk runtime layer unless the owner approves true alpha-native depth planes; do not simulate depth by splitting connected towers, facades, trees, lamps, or sidewalks into independently scrolling masks, and never use global RGB/chroma-key deletion;
- keep visual scaling independent from collision authority. Roof products, shadows, and other non-body decoration do not enter a body collider unless gameplay explicitly requires it;
- an asset is not `verified` until a comparison sheet shows the master, prior runtime when one exists, new native runtime, nearest-neighbor preview, and real Phaser screenshots at every required lane scale with no crop, halo, bleeding, blur, or console error;
- approve one static frame before producing animation. Animation frames must derive from that approved static design and preserve fixed bounds, origin, baseline, and collider guides.

## Verification strategy

- Pure domain rules: unit tests.
- Phaser scene wiring: focused integration tests or manual greybox checks.
- Responsive/iframe behavior: one browser smoke pass when integration exists.
- Visual fidelity: compare at `360 × 640` against the selected concept.
- Full build: phase completion and build/configuration changes only.
