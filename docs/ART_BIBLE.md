# BeautyBomb Delivery — Pixel Art Bible

## Authority and scope

This document governs final art, UI styling, parallax, and animation for the independent BeautyBomb Delivery portfolio concept. It does not grant brand approval or permission to reuse official campaign artwork.

Authority order:

1. Owner-approved product, logo, and selected gameplay references in `visual-references/`.
2. Stable visual and verbal traits observed on the official BeautyBomb site on 2026-08-15.
3. The rules in this document.
4. Artist judgment that does not contradict the first three levels.

Seasonal banners, collaboration characters, product photography, and site illustrations are analysis material only. They must not be copied into shipped game assets.

## Brand analysis translated into game rules

Observed on the official website:

- white structural backgrounds with high-contrast black typography;
- bold uppercase display lettering and Montserrat for supporting text;
- yellow rounded actions (`#FFEF5C`) with near-black text;
- recurring pink (`#FF4FAB`), purple (`#982ADD`), red (`#E30613`), and bright cyan (`#54E0FF`);
- large collection-specific scenes, collage cutouts, stickers, brush marks, emojis, wavy edges, and deliberate visual surprise;
- direct second-person voice focused on choice, experimentation, uniqueness, and current trends;
- Waterbomb shown as a turquoise product on a pale lavender field with purple headings and black explanatory text.

Pixel adaptation:

- translate collage cutouts into crisp pixel stickers with stepped white borders and dark-violet shadows;
- translate emojis into authored pixel icons; never use platform emoji inside the canvas;
- translate brush marks and waves into blocky, tileable silhouettes;
- preserve bold black/near-black lettering and high color commitment;
- use expressive brand devices mainly on intro, victory, and prize screens; keep the road readable during active play;
- treat the product tube and courier vehicle as the primary brand signature.

## Art direction

### Thesis

An energetic BeautyBomb campaign has been compressed into a premium 16-bit delivery game: turquoise city, sticker-like UI, assertive black lettering, pink and yellow hits, and a hero Waterbomb product that remains recognizable at gameplay scale.

### View and perspective

- Logical viewport: `360 × 640`, portrait.
- Camera: shallow 2.5D three-quarter side view.
- Vehicles face right; the environment and traffic move right-to-left.
- The courier stays near `x = 74–82` logical pixels.
- Vehicle wheel baselines are `350`, `424`, and `508`, positioned near the lower edge of each road section instead of at its geometric center.
- Visual depth scale targets: far lane `1.12`, middle lane `1.22`, near lane `1.32`.
- Lane changes interpolate visual scale and baseline position. Collision rectangles use the authored body guides at `84%` of visual scale so the larger art remains readable without making avoidance unfair.
- Roofs, hoods, and top faces are visible; avoid a flat orthographic side view and avoid an isometric camera.

### Pixel grid and master-derived exception

- Authored low-resolution pixel art uses one source pixel per logical canvas pixel at native game scale.
- Draw, position, and export authored low-resolution assets on integer coordinates only.
- `VEH-001` static `v4` is the approved fidelity-first master frame: a `208 × 160` pixel-style raster exported directly from the approved `v6` alpha master and rendered at `0.5` base texture scale. Do not describe it as a hand-authored `104 × 80` sprite. Drive sheet `v5` derives all four frames from that same master with one nearest-neighbor resize per frame; frame zero is byte-identical to `v4`.
- Runtime scaling uses nearest-neighbor filtering; no bilinear filtering. The courier's documented lane scales are the only scaling after the single production export.
- Animated frames share an identical canvas, origin, baseline, and transparent padding.
- No automatic vector-to-pixel conversion for the final logo or product; redraw them manually on the grid.
- Shading uses discrete color ramps, never smooth gradients or airbrush texture.

### Shape language

- Main silhouettes are compact, slightly chunky, and readable before internal detail.
- Exterior sprite outlines: usually `2 px`, deep violet; `1 px` only for controlled internal details.
- UI panels resemble cut paper or stickers: stepped corners, `2–3 px` outline, optional `2 px` offset shadow.
- Buttons use pixel-stepped rounded corners derived from the site's rounded yellow controls, not generic browser pills.
- Wavy/scalloped edges are reserved for screen transitions, sky dividers, and Waterbomb-themed panels.
- Gameplay obstacles must differ by roofline, hood, cabin, and length; color swaps alone are insufficient.

## Palette

These are concept tokens informed by the official site and supplied product reference, not an official brand book.

| Token | Hex | Role |
|---|---:|---|
| `bb-ink` | `#1D1D1B` | Logo, primary UI text, strongest outlines |
| `bb-deep-violet` | `#1E1D3E` | Sprite outlines, deep shadows, road contrast |
| `bb-white` | `#FFFFFF` | Sticker fields, highlights, product label |
| `bb-lavender` | `#EEF0FF` | Waterbomb panels and quiet UI fields |
| `bb-water-cyan` | `#00B7D6` | Courier vehicle and Waterbomb body |
| `bb-sky-cyan` | `#54E0FF` | Sky accents and bright collection fields |
| `bb-pink` | `#FF4FAB` | Secondary actions, delight, reward emphasis |
| `bb-purple` | `#982ADD` | Headings, prize and victory emphasis |
| `bb-yellow` | `#FFEF5C` | Primary CTA and selected controls |
| `bb-progress-lime` | `#C8F000` | Delivery progress only; not a general UI color |
| `bb-danger` | `#E30613` | Collision/failure state only |
| `road-base` | `#4C4C6C` | Road surface |

Usage balance during gameplay:

- cyan/turquoise environment and vehicle: `30–40%`;
- road, ink, and deep violet: `25–35%`;
- white/lavender breathing space: `15–25%`;
- pink, purple, yellow, lime, and red combined: normally below `20%`.

Never place yellow text on white, cyan text on sky cyan, or pink text on purple. Text must target WCAG AA contrast where practical; large decorative pixel headings must remain clearly legible at `360 × 640`.

## Typography and iconography

- The BeautyBomb wordmark is an image asset, not typeset text.
- Produce a compact bitmap UI alphabet covering `А–Я`, `Ё`, `A–Z`, `0–9`, currency/percent signs, arrows, and punctuation.
- Display labels: bold uppercase, tight line spacing, pixel-stepped geometry inspired by the site's assertive display type without copying a proprietary font file.
- Supporting copy: a more open bitmap face with a minimum rendered cap height of `12 px` and normal body size of `14–16 px`.
- Limit gameplay HUD to one line per metric and short Russian labels.
- Icon family: heart, route/progress, sound, pause, arrow up/down, retry, home, parcel, star, and location pin.
- Icons use the same pixel grid and outline weights as sprites; do not mix vector UI icons or OS emoji with pixel art.

## Hero object rules

### Courier vehicle

- Turquoise/blue body, facing right.
- Near side profile with only a narrow front plane, keeping the long side panel dominant.
- Use only the specified two-line `BEAUTY BOMB` side treatment: acid-yellow lettering (`#FFEF5C`) with a deep-violet outline (`#1E1D3E`) and, if retained by the review candidate, a restrained pink shadow. Do not add flowers, further lettering, or replacement symbols.
- Waterbomb tube lies horizontally on the roof, cap facing left/back, with no intermediate neck between the cap and body.
- Each wheel uses one small triangular pale highlight as a rotation phase marker.
- Product must be secured by a simple rack or straps so it does not look pasted onto the roof.
- Silhouette must remain readable at all three lane scales.
- Vehicle must not resemble an ice-cream truck or ambulance.

### Waterbomb tube

- Preserve the reference tube silhouette when shown vertically; in the horizontal gameplay version, use a broad turquoise face-cream body, a wide ribbed white cap, a direct cap-to-body seam, and full-length gradual widening with no toothpaste-like narrow neck or sudden shoulder.
- `VEH-001 v6` may retain the reference-derived `WATERBOMB` / `BEAUTY BOMB` package hierarchy because it is part of the owner-requested review candidate. A later standalone hero product still requires its own approval gate.
- Do not invent claims or packaging copy beyond the approved reference-derived hierarchy.
- No invented claims or packaging copy.

### Traffic

- Minimum five silhouettes: compact hatchback, sedan, taxi-like box, small delivery van, and sporty coupe.
- Every silhouette needs a distinct roofline and wheelbase.
- Use brand-compatible colors but keep the courier uniquely turquoise.
- Traffic can use pink, yellow, green, purple, coral, cream, and dark blue; avoid a second Waterbomb-cyan hero vehicle.
- The first playable trio is a pink compact hatchback, yellow sedan, and green boxy wagon, all facing left against the courier.
- Same-lane traffic silhouettes must keep at least `16 px` of visible horizontal clearance at runtime; body pixels may not overlap while driving at one speed.

## Environment and parallax

Layer stack from back to front:

| Layer | Relative speed | Content | Runtime tile contract |
|---|---:|---|---:|
| Sky | `0.03` | reconstructed cyan sky and source clouds | `2048 × 512` direct POT cycle |
| Coherent city | `0.56` | varied neighborhood facades, medium blocks, restrained skyline, trees, and sidewalk as one composition | `2048 × 512` approved-alpha POT cycle |
| Road markings | `1.00` | approved v3 lane marks, full-height asphalt, and white top/bottom curbs | `1792 × 406` panorama in a `2048 × 512` POT cycle |
| Foreground accents | `1.15` | control-safe neutral pavement | `1792 × 128` panorama in a `2048 × 128` POT cycle |
| Control-panel cobblestone | `1.28` | simple curb-gray pixel pavers behind the fixed lane controls | `512 × 128` direct POT cycle, clipped to `360 × 118` UI panel |

Rules:

- no official store facade or copied campaign banner;
- `ENV-004 v8` derives from the immutable `env-001-parallax-neighborhood-v6-alpha-master.png` as one skyline-to-sidewalk layer; distant towers, medium blocks, facades, trees, roof props, awnings, and storefronts must never receive independent horizontal offsets;
- the v6 master supplies approved alpha, so runtime derivation performs no color deletion. Detached clouds and the cyan sky stay exclusively in unchanged `ENV-001`; the v8 source period joins two complete facade walls directly, preserves the sidewalk, and may not introduce an empty seam zone, mirrored landmark, or clipped foreground object;
- `ENV-006 road v6` preserves the approved v3 panorama and exact `y=282–522` gameplay band. Only the top `0–5` and bottom `388–397` curb rows use neutral white pixel shading; asphalt, lane markings, position, scale, and speed remain unchanged;
- repeated tiles must hide seams and avoid obvious landmark repetition within ten seconds; a cyclic panorama may mirror only an object-free edge gutter, never a tree, storefront, building, lamp post, or other foreground landmark;
- Phaser 3.90 `TileSprite` runtime textures use a power-of-two canvas, an explicit useful-content rectangle, and a documented horizontal period; do not reintroduce an NPOT source texture into a cyclic layer;
- near-layer props cannot cover controls, lives, or the courier collision area;
- scenery contrast is lower than vehicle contrast;
- Waterbomb references appear through palette and shapes, not repeated logos on every building.

## UI screens

### Intro

- Reuse the actual `360 × 640` gameplay composition in a frozen `ready` state: sky, coherent city, road, HUD, courier, lower console, and lane buttons retain their normal positions, while parallax, traffic, and route time remain stopped.
- `UI-013` v3 is a native `332 × 207` lavender comic callout placed at `x=16, y=154`. Its dark-violet stepped outline, pink lower edge, white highlight, and tail belong to the existing sticker language; the tail tip must point unambiguously toward the courier roof tube. The lower-right interior is continuous opaque lavender with no decorative mark.
- The Russian instruction is rasterized in uppercase Press Start 2P from a repository-local SIL OFL source. Keep the approved eight-line copy and inner margins; do not substitute a runtime system font or external font CDN.
- `UI-014` is a centered `112 × 36` three-frame `ЖМИ` prompt at `x=180, y=354`. Its chevrons and yellow/pink/cyan states remain visible without covering the courier or HUD.
- During ordinary waiting, `ЖМИ` uses a restrained `1.00 → 1.06 → 1.00` `Sine.InOut` pulse over `1,000 ms`; the courier uses the approved `VEH-001` body-and-tube drive motion at the same cadence, while both wheel hubs remain fixed to frame `0`.
- A first canvas press, `Enter`, or `Space` triggers one guarded `1,000 ms` three-color transition. Route time remains zero until completion, then the callout is hidden and standard gameplay motion resumes.
- Under `prefers-reduced-motion`, remove CTA scaling and courier motion while retaining the static instruction and a calm color change before play.

### Pause

- `UI-015` v2 is a centered native `332 × 272` lavender comic callout at `x=180, y=318`; v1 is retained unchanged. It uses the exact stepped front-body geometry and offset `+3,+4 px` pink extrusion from the integrated intro cloud, extended only vertically and without a tail or pointer.
- The copy is rasterized with the same repository-local Press Start 2P source as the intro: `Не тормози! Нужно успеть вовремя :)`, split into three centered uppercase pixel lines. Do not replace it with runtime system text or a web font.
- The existing `ПРОДОЛЖИТЬ` and `ЗАНОВО` buttons retain their construction, labels, and pressed feedback; they appear below the copy at centers `180,334` and `180,394`, wholly inside the lavender inner body.
- Keep the bottom console and lane controls visible but inert before play. Pause, exit, and sound controls are not rendered. Do not add a fullscreen shade, separate START button, or the former start popup.

### Gameplay HUD

- Three hot-pink sticker hearts sit at top-left without a `LIVES` label; lost lives switch to the matching pale-violet empty frame instead of disappearing.
- The `324 × 16` progress bar remains across the upper safe area: turquoise base, acid-yellow fill, deep-violet stepped frame, one small end sparkle, and a white pixel highlight at the live fill edge.
- Yellow touch buttons retain their native `76 × 48` pixel-art frames and separate up/down normal and pressed states, but render at `1.5×` with matching `114 × 72` hit areas. The v2 treatment uses a clean yellow face, solid black arrow, stepped black frame, and one restrained pink extrusion. Down is centered at `111, 572` on the left; up is centered at `249, 572` on the right, leaving a `24 px` gap between buttons and `32 px` of free space below the `y=522–640` control panel.
- The fixed lower control console ends at the bottom of the viewport. `ENV-010` fills it with simple curb-gray cobblestone and overlaps the road by exactly `2 px`, so no underlay or color strip can appear at the join. The cobblestone starts only with active gameplay, pauses with the existing parallax lifecycle, freezes under reduced motion, and never moves the buttons or their `114 × 72` hit areas.
- `UI-010` v2 and `UI-012` v2 are compact top-right `32 × 32` yellow utility controls with black icons, a dark stepped frame, and restrained pink extrusion. Pause sits at `x=332, y=32`; sound sits directly below at `x=332, y=78`. Both use `44 × 44` hit areas; the visible gap and hit areas remain separate from the title and progress bar. Pause uses the existing pause flow. During gameplay, sound toggles the background track and its muted state adds a crisp red seven-step pixel slash over the existing icon without moving, scaling, redrawing, or changing the hit area of the approved button. Keyboard `P` and `Esc` retain their existing pause entry point.
- The exit placeholder is a direct HTML/CSS control rather than the retained pixel-art `UI-011` texture: a simple anti-aliased red `×` with a `1 px` black outline, no background or shadow, at logical center `x=28, y=32`. Its transparent logical `44 × 44` hit target scales with the game surface, stays clear of the title and progress HUD, and intentionally has no exit behavior yet. It follows the existing utility-control visibility contract: hidden during the intro and finale prompt, visible only during active gameplay.
- The title stays horizontally centered at `x=180, y=38`.
- The game uses no decorative outer frame; the logical `360 × 640` canvas remains visually unframed against the host background.
- The run timer remains internal gameplay authority and is never rendered as seconds or a countdown in the gameplay HUD; progress is communicated only by the progress bar.
- HUD uses solid fields and silhouettes; no translucent glass effects.

### Defeat

- Deep-violet overlay, red/pink collision accent, concise retry action.
- Failure remains playful rather than punitive.

### Delivery and victory

- The 100% progress frame leads into a `1,500 ms` obstacle-free victory drive with bounded rectangular confetti in yellow, pink, cyan, violet, and white.
- `ENV-009` v3 is the finale-only continuation of `ENV-004`: it keeps the same `2048 × 512` runtime canvas, `0.36/0.55078125` scale, depth, and city motion. The approved house architecture is part of one unified generated panorama with complete neighboring facades and one continuous sidewalk. The exact doorstep interval is filled from the adjacent approved curb at runtime-export resolution; never reintroduce a separately pasted house, cleared rectangular slot, cyan/sky backing plate, covered facade, clipped neighbor, or empty street-level interval. Its compact greenery remains part of the integrated lot.
- `CHR-003` v1 is the approved full-body blonde recipient in a simple pink dress, authored as a compact `112 × 176` low-poly/pixel-art hybrid master and exported once into a `28 × 44` canvas. Large faceted color planes, minimal facial detail, simplified hair, hands, clothing, and shoes keep the `16 × 40` visible silhouette readable at runtime. She preserves origin `(0.5, 1)`, baseline, left-facing orientation, cubic reveal, and `700 ms` duration, but now begins transparently at the door (`307,276`) and moves to the doorstep (`319,284`) while fading in. No door redraw or animation is added. Her cream-receiving anchor is `319,262`, matching the new final pose; she remains separate from the city texture so depth and delivery choreography stay controllable.
- `UI-016` v5 repeats the lavender/deep-violet/pink intro-cloud language and local Press Start 2P rasterization at its native `332 × 104` grid. Its upper tail reuses the approved `UI-013` v3 comic-tail silhouette reflected upward and translated to the recipient; outer and inner tail shapes overlap the body's top contour in the same draw order, so the join reads as one continuous bubble and no highlight crosses it. The tail uses only deep violet and lavender, with no pink outline; the body retains its pink extrusion. It rises to `x=14, y=338`, points to the girl, and keeps the recipient and destination unobscured. Its copy is `Большое спасибо! Теперь можешь забрать награду!`; `UI-017` is centered at `180,466`.
- `UI-017` is a three-frame `<ЗАБРАТЬ>` sibling of `UI-014`, centered below the callout at `x=180, y=488`, with the same yellow/pink/cyan order and restrained pulse. Its scaled visible bottom remains above `y=508`, leaving at least `14 px` before the control panel at `y=522`.
- `PRD-003` derives from the immutable clean courier master, rotates the same roof tube vertically, and follows a short arc to the girl's receiving anchor before disappearing.
- `UI-018` keeps its approved transparent ticket master immutable. Its live upper section reuses the exact `BEAUTY BOMB` crop from `UI-009` at native scale. The ticket uses a deliberate, mirrored visual system rather than scattered doodles: paired bomb emblems, paired framed kaleidoscope tiles, and one centered burst seal. These yellow, pink, cyan, and deep-violet marks remain on the native pixel grid inside the coupon's measured opaque core only; they stay behind interactive content and never enter the transparent stepped edge, code row, copy-feedback line, perforation, or lower explanatory-copy safe zone.
- Arrival uses product-focused framing before the future roulette transition. The victory palette shifts toward lavender, purple, pink, yellow, and white.

### Prize screen

- Out of the current production batch, but the art system reserves a purple/pink sticker wheel with yellow selected states.
- Demo rewards must remain explicitly fictional until a client-owned server exists.

## Animation grammar

| Motion | Target | Frames / duration | Rule |
|---|---|---:|---|
| Vehicle idle/drive | courier | `4 frames`, `8–10 fps` | wheel rotation plus restrained body bounce |
| Lane change | courier | `180 ms` | position/scale tween plus one-frame lean; no blur |
| Tube secondary motion | product | `4 frames` | `1–2 px` delayed bounce, straps remain attached |
| Traffic drive | obstacles | `2–4 frames`, `6–8 fps` | wheel cycle; body mostly stable |
| Hit | courier/UI | `300–450 ms` | outline/tint, short knock, particles; no rapid full-screen flash |
| Invulnerability | courier | `1.1 s` | slow outline pulse or alternating tint at no more than `2 Hz` |
| Arrival | courier/girl | `6–8 frames` | brake, settle, greeting gesture |
| UI press | buttons | `80–120 ms` | `1–2 px` depression and shadow reduction |

The current greybox alpha flicker must be replaced before visual completion because it flashes faster than the target motion-safety rule.

Reduced-motion mode:

- disables camera shake and foreground parallax;
- replaces bounce with static poses;
- keeps lane movement and obstacle motion because they convey gameplay state;
- uses a solid outline/tint for invulnerability.

## Export and runtime rules

- Runtime sprites: transparent PNG or lossless WebP only after visual comparison proves no degradation.
- Keep editable masters outside the runtime atlas; export files contain no guides or reference layers.
- Animated frames are not trimmed or rotated by the atlas packer.
- Minimum `2 px` transparent padding around frames and `4 px` between atlas regions.
- Prefer atlases no larger than `1024 × 1024`; hard ceiling `2048 × 2048`.
- Critical gameplay art target: below `900 KB` compressed; all first-load critical assets remain below the existing `1.5 MB` budget.
- Separate intro/victory/prize art so it can load after the first playable screen.
- File names use lowercase kebab case and stable asset IDs from `docs/ASSET_MANIFEST.md`.

## Acceptance criteria

Art is ready for integration only when:

- vehicle, broad reference-derived Waterbomb tube, `BEAUTY BOMB` side treatment, and wheel phase markers remain recognizable at `360 × 640`;
- all traffic silhouettes can be distinguished in grayscale;
- all three lane scales share one perspective and baseline system;
- animation frames do not jitter because of changing bounds or origins;
- parallax tiles loop without visible seams;
- HUD remains readable over every environment layer;
- no platform emoji, smooth-gradient substitute, copied site art, or unofficial campaign claim appears;
- assets pass a native-size review and a final in-game screenshot review.

## Sources reviewed

- Official homepage: <https://beautybomb.ru/>.
- Official brand page: <https://beautybomb.ru/about/>.
- Official Waterbomb product page: <https://beautybomb.ru/catalog/sos-maska-dlya-litsa-waterbomb/>.
- Review date: 2026-08-15.
