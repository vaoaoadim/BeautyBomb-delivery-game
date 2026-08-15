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

## Integration boundary

Preferred production embedding is an iframe-backed widget because it isolates canvas sizing, dependencies, styles, and failures from the client's website.

The future host contract should expose:

- commands: open, close, pause, resume, configure campaign;
- events: ready, started, hit, defeated, delivered, prize received, closed;
- identifiers: widget version and campaign ID;
- no secret, session token, or real promo code in logs.

The standalone portfolio demo uses the same interface with a local adapter.

## Rendering and performance

- Logical canvas: `360 × 640`.
- Scale mode: fit and center.
- Pixel art and rounded pixels enabled.
- Image smoothing disabled.
- Parallax layers reuse tileable textures.
- Collision boxes are simpler than visible sprites.
- Target: stable 60 FPS, graceful 30 FPS on slower mobile devices.
- Initial budgets are targets, not release claims: JavaScript under 350 KB gzip excluding lazy audio, initial critical assets under 1.5 MB, no layout shift on the host page.

## Art asset contract

- `docs/ART_BIBLE.md` owns perspective, pixel grid, palette, shape, UI, parallax, animation, and export rules.
- `docs/ASSET_MANIFEST.md` owns stable asset IDs, production batches, native canvases, status, and handoff requirements.
- Editable masters do not belong in runtime atlases.
- Runtime asset directories are created only when their first approved export exists.
- Animated frames keep fixed bounds and origins; Phaser must not compensate for inconsistent art at runtime.

## Verification strategy

- Pure domain rules: unit tests.
- Phaser scene wiring: focused integration tests or manual greybox checks.
- Responsive/iframe behavior: one browser smoke pass when integration exists.
- Visual fidelity: compare at `360 × 640` against the selected concept.
- Full build: phase completion and build/configuration changes only.
