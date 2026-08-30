# Product Source of Truth

## Status and positioning

- Project: browser mini-game concept for BeautyBomb.
- Purpose: portfolio case and a possible future brand pitch.
- Status: independent unsolicited concept, not an official campaign.
- Delivery order: standalone demo first, portfolio embedding second, client-site integration only as a production scenario.

Required portfolio disclaimer:

> Независимый продуктовый концепт / unsolicited concept. Проект не является официальной рекламной кампанией BeautyBomb и создан в образовательных и демонстрационных целях.

## Product promise

The player delivers a Water Bomb cream order, avoids traffic, reaches the destination, and then receives a fictional demonstration coupon with a fixed 20% discount code.

## User flow

1. Host page opens the game in a modal or standalone demo.
2. The frozen gameplay scene presents a comic callout with the goal and controls; pressing anywhere, `Enter`, or `Space` completes a one-second intro transition before the run begins.
3. Player starts the delivery.
4. The courier vehicle changes between three lanes and avoids traffic.
5. Progress reaches the destination in a successful run.
6. The vehicle stops at a house where a girl is waiting.
7. A small vertical cream first flies from the courier roof to the girl.
8. Only after the product transfer completes does a branded callout ask the player to collect the delivery reward.
9. Pressing `<ЗАБРАТЬ>` opens the existing reward flow.
10. Demo mode displays a local fictional coupon code; production mode must request a prize from the client's server.

## Locked gameplay decisions

- Portrait logical viewport: `360 × 640`.
- Camera: horizontal 2D/2.5D three-quarter side view.
- Vehicle stays near the left side; the road and environment scroll right-to-left.
- Exactly three depth lanes.
- One input moves the vehicle to one adjacent lane.
- Traffic mixes single cars, parallel pairs, staggered pairs, same-lane convoys, and scattered pairs instead of repeating one formation.
- A formation contains at most two cars, and a `1,200 ms` safety window must always leave at least one lane open.
- Every chronological adjacent same-lane pair uses the approved asset bounds, lane scale, and vehicle multiplier to retain at least `48 px` of visible space. Cross-lane obstacles within one `1,200 ms` safety window appear as one formation within `200 ms`; otherwise they are separated by the full window.
- The first obstacle set cycles through a pink hatchback, yellow sedan, and green boxy wagon.
- Final art follows `docs/ART_BIBLE.md`; asset production and approvals follow `docs/ASSET_MANIFEST.md`.
- Lane transition: 180 ms with one buffered command.
- Desktop controls: arrow keys; mobile controls: on-screen down/up buttons, with down on the left and up on the right.
- The initial `ready` state keeps route time at zero, freezes parallax and obstacles, shows courier frame `0` with only a subtle `1 px` idle bob, and leaves the bottom lane controls visible but inert.
- The intro callout and `ЖМИ` prompt sit above the frozen environment while pause, exit, and sound controls remain hidden. The former START popup is not part of the flow.
- A first pointer press anywhere on the canvas, `Enter`, or `Space` starts one guarded `1,000 ms` color-pulse transition. Repeated input cannot create another start, and lane input remains inactive until `startRun` executes at transition completion.
- Successful session target: 45–60 seconds.
- The gameplay duration remains deterministic but is not exposed as a visible seconds countdown; the progress bar is the only in-run time/progress indicator.
- Starting lives: 3.
- Invulnerability after a hit: 1.1 seconds.
- Unlimited retry.
- Prize is available only after victory.
- Demo prize weights: 20% = 50, 25% = 30, 30% = 15, 35% = 5.

## Locked visual direction

- Crisp premium 16-bit pixel art with a consistent pixel grid.
- Primary scene: turquoise city, layered skyline, bright shopfronts, trees, dark-violet outlines, acid-lime controls, and pink UI accents.
- Player vehicle: turquoise/blue rather than pink.
- The integrated courier body is clean: no text, logos, icons, flowers, or decorative prints.
- The roof tube follows the supplied face-cream silhouette through a broad turquoise body, wide white flip-top cap with a recessed thumb-lift, direct seam, and full-length gradual taper, but contains no text, logos, icons, or printed graphics at gameplay scale.
- The tube is mounted horizontally on the roof, cap facing backward by default.
- A separate large product asset still requires its own approval gate.
- Selected concept reference: `visual-references/selected-gameplay-concept-v1.png`.
- Product reference: `visual-references/beautybomb-water-bomb-reference.png`.
- Logo reference: `visual-references/beautybomb-logo-reference.png`.

Working colors are concept colors, not an official brand book:

| Role | Value |
|---|---|
| Vehicle primary | `#00B7D6` |
| Vehicle highlight | `#00CDE9` |
| Vehicle shadow | `#008EAA` |
| Deep outline | `#1E1D3E` |
| Logo | `#111111` |
| Pink accent | `#FF4FAB` |
| Official-site yellow control | `#FFEF5C` |
| Purple heading/reward | `#982ADD` |
| Sky cyan | `#54E0FF` |
| Progress-only lime | `#C8F000` |
| Road | `#4C4C6C` |
| Cream highlight | `#FFF3DC` |

## Non-goals for the first demo

- No real promo-code inventory.
- No payment, account, checkout, or personal-data flow.
- No CMS.
- No multiplayer or leaderboard.
- No landscape gameplay layout.
- No claim of official brand approval.

## Current phase

The deterministic greybox and varied traffic schedule are implemented. The Pixel Art Bible and Asset Manifest are specified from the approved references and stable traits observed on the official BeautyBomb site.

The approved intro uses `UI-013` v3 for the Russian comic callout and `UI-014` for the centered three-color `ЖМИ` prompt. UI-013 v3 preserves the approved callout and replaces only the small yellow decorative mark in its lower-right interior with the opaque lavender bubble surface. Its `ready → transition → playing` flow is integrated and verified at logical `360 × 640` and CSS widths of approximately `320` and `360 px`; no runtime font download is required.

The existing pause flow now presents `UI-015` v2: a larger tail-free lavender comic callout that repeats the intro cloud's stepped body and pink extrusion while using the same local Press Start 2P font for `Не тормози! Нужно успеть вовремя :)`. Existing `ПРОДОЛЖИТЬ` and `ЗАНОВО` controls keep their implementation and pressed behavior, appearing below the copy inside the callout; pausing, resuming, restarting, keyboard handling, and gameplay authority are unchanged.

The delivery finale keeps the deterministic route at `45,000 ms` and adds a separate `1,500 ms` presentation-only finish road after progress reaches 100%. Traffic scheduling ends `3,200 ms` before delivery so the last obstacle leaves naturally; the finish road disables spawning, collision, and lane input while road motion, courier drive frames, and bounded brand-color confetti continue. At delivery completion, the coherent city TileSprite switches from immutable route tile `ENV-004` to deterministic destination panorama `ENV-009` v3 while preserving the city scale, depth, and motion contract. The approved house architecture is generated into a complete foreground lot inside that one panorama, with neighboring buildings and a continuous shared sidewalk; the six-pixel doorstep interval extends the adjacent curb instead of revealing the sky. There is no independent house sprite, erased rectangle, or flat-sky backing plate. `CHR-003` v1 keeps its existing cubic fade-in and `700 ms` duration, but now appears at the house door (`307,276`) and finishes next to the doorstep (`319,284`) rather than entering from the road; the receiving anchor follows to `319,262`. The courier parks at `74,322` on the upper road edge. `PRD-003` still starts from a roof-local offset and flies to the recipient before `UI-016` v5 at `14,338` and `UI-017` at `180,466` appear. Claiming then opens the interactive `UI-018` v7 coupon with the local fictional code `XQZ-20476`, an accessible clipboard control in the lower tear-off, and the unchanged restart action. The coupon uses a larger native `332 × 498` composition with a 14 px horizontal and 71 px vertical logical safety margin; its explanatory bitmap copy is rendered at 12 px before the single nearest-neighbor export for clear reading at every fitted canvas size. A large 40 px `20%` reward value uses the same compact branded pixel treatment as the `BeautyBomb` heading while staying entirely above the coupon perforation.

The corrected vehicle scale and traffic clearance gates are approved. The active courier is the clean `veh-001-courier-clean-static-v6.png` / `veh-001-courier-clean-drive-v7.png` set derived from the versioned `v8` flip-top master: its rear white cap is a one-piece snap-open cosmetic cap with a visible seam, hinge, and recessed thumb-lift; both the van side and roof tube contain no text, logos, icons, or decorative prints. The four-frame drive sheet preserves the fixed `208 × 160` canvas, `0.5` base scale, world size, wheel baselines, origin, and body-only collider. `PRD-003 v2` derives from that same master, so the cream handed to the recipient has the identical cap. `ENV-010` retains its `y=520` top edge and `2 px` road overlap but is rendered at `360 × 122`; the final `2 px` are clipped beyond the logical viewport and prevent the lower rounding gap. The host page presents the logical canvas at the smaller of its `360 px` maximum, available width, and available height × `9/16`, keeping a `12 px` surround so desktop zoom and mobile browser chrome cannot crop controls. All gameplay geometry, controls, collider behavior, state transitions, and the existing environment lifecycle are unchanged.
