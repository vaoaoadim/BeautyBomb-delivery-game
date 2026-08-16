# Product Source of Truth

## Status and positioning

- Project: browser mini-game concept for BeautyBomb.
- Purpose: portfolio case and a possible future brand pitch.
- Status: independent unsolicited concept, not an official campaign.
- Delivery order: standalone demo first, portfolio embedding second, client-site integration only as a production scenario.

Required portfolio disclaimer:

> Независимый продуктовый концепт / unsolicited concept. Проект не является официальной рекламной кампанией BeautyBomb и создан в образовательных и демонстрационных целях.

## Product promise

The player delivers a Water Bomb cream order, avoids traffic, reaches the destination, and then sees a demonstration prize wheel with discounts of 20%, 25%, 30%, or 35%.

## User flow

1. Host page opens the game in a modal or standalone demo.
2. Welcome screen explains the goal and controls.
3. Player starts the delivery.
4. The courier vehicle changes between three lanes and avoids traffic.
5. Progress reaches the destination in a successful run.
6. The vehicle stops at a house where a girl is waiting.
7. Victory opens the prize wheel.
8. Demo mode displays a clearly fictional promo code; production mode requests a prize from the client's server.

## Locked gameplay decisions

- Portrait logical viewport: `360 × 640`.
- Camera: horizontal 2D/2.5D three-quarter side view.
- Vehicle stays near the left side; the road and environment scroll right-to-left.
- Exactly three depth lanes.
- One input moves the vehicle to one adjacent lane.
- Traffic mixes single cars, parallel pairs, staggered pairs, same-lane convoys, and scattered pairs instead of repeating one formation.
- A formation contains at most two cars, and a `1,200 ms` safety window must always leave at least one lane open.
- Same-lane convoy cars use a `750 ms` spawn interval and retain at least `16 px` of visible space at the largest approved vehicle scale.
- The first obstacle set cycles through a pink hatchback, yellow sedan, and green boxy wagon.
- Final art follows `docs/ART_BIBLE.md`; asset production and approvals follow `docs/ASSET_MANIFEST.md`.
- Lane transition: 180 ms with one buffered command.
- Desktop controls: arrow keys; mobile controls: on-screen up/down buttons.
- Successful session target: 45–60 seconds.
- Starting lives: 3.
- Invulnerability after a hit: 1.1 seconds.
- Unlimited retry.
- Prize is available only after victory.
- Demo prize weights: 20% = 50, 25% = 30, 30% = 15, 35% = 5.

## Locked visual direction

- Crisp premium 16-bit pixel art with a consistent pixel grid.
- Primary scene: turquoise city, layered skyline, bright shopfronts, trees, dark-violet outlines, acid-lime controls, and pink UI accents.
- Player vehicle: turquoise/blue rather than pink.
- Vehicle body carries a manually redrawn pixel version of the BeautyBomb logo.
- Water Bomb tube matches the supplied product reference in silhouette, turquoise body, white cap, and label hierarchy.
- The tube is mounted horizontally on the roof, cap facing backward by default.
- Fine packaging copy becomes controlled pixel blocks at gameplay scale; a separate large product asset may retain more detail.
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

The approved courier static PNG and three obstacle candidates are integrated. Vehicles use wheel baselines `350`, `424`, and `508` plus visual scales `1.12`, `1.22`, and `1.32`, filling each road section while preserving depth. Authored body colliders use only `84%` of visual scale, the roof-mounted Waterbomb remains excluded, and the green wagon has an optical size correction so it is not smaller than the pink hatchback. The traffic schedule still guarantees an escape lane. The next gate is owner approval of `visual-references/vehicle-lane-scale-check-v2.png` and the local playtest before animation begins. Prize roulette and client-site integration remain later phases.
