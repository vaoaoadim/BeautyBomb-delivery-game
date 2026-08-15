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
| Pink accent | `#FF4F9B` |
| Lime control | `#C8F000` |
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

The deterministic greybox is implemented. It includes three-lane movement, one buffered input, curated obstacle waves, collision, three lives, temporary invulnerability, delivery progress, victory, defeat, and unlimited retry.

The next phase is gameplay validation and tuning at the target viewport, followed by production of the approved pixel-art assets and animation set. Prize roulette and client-site integration remain outside the greybox.
