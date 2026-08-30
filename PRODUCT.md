# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- Portfolio visitors evaluating the concept as a product-design and frontend case.
- In a hypothetical production campaign, BeautyBomb website visitors on mobile or desktop who want a short playful interaction rather than a long game session.

## Product Purpose

BeautyBomb Delivery is an independent browser-game concept. The player delivers a Waterbomb product through city traffic, reaches the recipient, and unlocks a fictional demonstration reward. Success means the mechanic is immediately understandable, the 45-second run feels fair and replayable, and the experience expresses the brand without claiming an official campaign.

Detailed product behavior is maintained in `docs/PROJECT.md`.

## Positioning

The case demonstrates a complete playable promotional mechanic, including a credible path from standalone demo to an iframe-based client integration, rather than presenting only a static campaign mockup.

## Operating Context

- Portrait `360 × 640` logical game canvas embedded in a standalone page or modal.
- Keyboard arrows on desktop and on-screen up/down controls on touch devices.
- Three-lane delivery run, three lives, progress, victory, defeat, and unlimited retry.
- Final production scenario separates the client-owned prize service from the browser game.

## Capabilities and Constraints

- TypeScript, Vite, Phaser 3, and Vitest.
- Final visual language is crisp premium pixel art; current geometry is a greybox.
- The courier vehicle is turquoise, faces right, and carries a broad horizontal turquoise face-cream tube with a closed white flip-top cap toward the rear. The integrated van body and tube are intentionally clean, with no text, logos, or decorative prints.
- No real promo codes, personal data, checkout, payment, or official campaign claim in the portfolio demo.
- Art must remain readable in three depth lanes and performant on ordinary mobile devices.

## Brand Commitments

- Preserve the supplied tube silhouette, turquoise body, and broad white flip-top cap with a recessed thumb-lift. Keep the integrated courier body and tube free of text, logos, icons, and decorative prints unless the owner explicitly approves a new version.
- If the supplied BeautyBomb wordmark is reused outside the vehicle sprite, preserve its proportions in the pixel adaptation.
- Extend stable traits observed on the official BeautyBomb site: high-energy color, black display lettering, yellow rounded actions, collage/sticker composition, playful direct voice, and strong collection-specific worlds.
- Do not copy seasonal campaign art or third-party collaboration characters into the game.

## Evidence on Hand

- Selected game concept: `visual-references/selected-gameplay-concept-v1.png`.
- Waterbomb product reference: `visual-references/beautybomb-water-bomb-reference.png`.
- BeautyBomb logo reference: `visual-references/beautybomb-logo-reference.png`.
- Pixel-art references in `visual-references/`.
- Official site: <https://beautybomb.ru/>.
- Official brand page: <https://beautybomb.ru/about/>.
- Official Waterbomb product page: <https://beautybomb.ru/catalog/sos-maska-dlya-litsa-waterbomb/>.
- No client approval, official brand book, campaign metrics, or production prize contract is available; future work must not fabricate them.

## Product Principles

1. Make the delivery mechanic understandable within seconds.
2. Keep challenge varied but visibly fair.
3. Let the product and vehicle carry the brand, not decorative clutter.
4. Prefer a small, polished asset system over a large inconsistent one.
5. Keep portfolio fiction clearly separated from a real client integration.

## Accessibility & Inclusion

- Controls must work without precise pointer gestures.
- Important states cannot rely on color alone.
- Text and controls require readable contrast at the target viewport.
- Reduced-motion mode must remove shake, aggressive flashing, and nonessential parallax while preserving gameplay information.
