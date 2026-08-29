# Design QA — coupon and defeat popup

- Source visual truth: `C:\Users\пк\Downloads\Снимок экрана 2026-08-29 172419.png` plus the owner's placement and copy requirements in the current task.
- Coupon implementation screenshot: `visual-references/qa/ui-018-v6-implementation.png`.
- Defeat implementation screenshot: `visual-references/qa/ui-006-v2-implementation.png`.
- Combined comparison: `visual-references/qa/ui-018-v6-comparison.png`.
- Runtime viewport: logical `360 × 640`; backing canvas `720 × 1280`; browser presentation `360 × 640` CSS px.
- Source pixels: `540 × 867`; implementation capture: `1280 × 720`, with the game region cropped to `360 × 640` CSS px.
- Density normalization: the source reference was proportionally resized to `399 × 640` for the combined comparison. Because the supplied source is vertically cropped, final placement judgment uses the coupon region rather than the missing lower viewport.
- State: reward coupon open; defeat popup checked separately in its open state.

## Full-view comparison evidence

The coupon keeps the supplied silhouette, perforation, palette, pixel density, overlay ownership, and centered placement. The requested structural change is visible: branded copy occupies the large upper ticket and the code row sits wholly inside the lower tear-off. The code field, copy control, and confirmation position remain clear of the outer border and lower-panel edge.

The defeat popup keeps its existing `332 × 272` shell, dim layer, restart-button placement, and visual hierarchy. All five text lines fit above the restart control without clipping.

## Focused-region comparison evidence

The combined coupon comparison confirms:

- `BeautyBomb` uses capital `B` characters and the established yellow face, violet outline, and pink extrusion;
- the information copy is centered and wrapped into five short lines, with no contact with side decorations;
- `промокод 20%` and `на все товары.` are separate narrow lines;
- the compact code row has visible left and right breathing room within the lower tear-off;
- no coupon content crosses the perforation or outer silhouette.

The defeat capture confirms that the added guidance uses the same Press Start 2P family and exact `15 px` size as the existing `ДТП! Давай еще раз!` copy.

## Comparison history

1. Initial implementation placed the added defeat guidance at a smaller size and allowed the longest coupon sentence to approach the side decoration. Result: blocked by P1 typography and spacing differences.
2. The defeat guidance was changed to the same `15 px` font size as the existing text. The coupon sentence was split into `промокод 20%` and `на все товары.` while preserving the exact requested wording. Post-fix captures show both issues resolved.
3. Browser verification exposed an existing exception while creating the accessible copy announcement. Replacing indexed `CSSStyleDeclaration` assignment with `cssText` preserved the visual UI and allowed the coupon to render. A clean defeat-state tab reported no console errors.

## Required fidelity surfaces

- Fonts and typography: passed. Coupon display and information copy use the project-local Press Start 2P source; defeat title and guidance both use `15 px`.
- Spacing and layout rhythm: passed. Upper copy, perforation, lower code row, and button preserve distinct zones with visible padding.
- Colors and visual tokens: passed. Existing coupon and popup palettes are unchanged.
- Image quality and asset fidelity: passed. Both assets are deterministic PNG exports with binary alpha and nearest-neighbor runtime filtering.
- Copy and content: passed. Required Russian text, capitalization, discount value, and defeat guidance are present without truncation.

## Findings

No actionable P0, P1, or P2 differences remain in the requested scope.

## Primary interactions checked

- Coupon overlay renders with the live code and copy control.
- Copy control remains a `44 × 44` interactive target around the compact `40 × 40` visual button.
- Defeat restart control remains inside the popup and retains the existing reset action.
- Browser console checked for errors during the rendered popup states.

final result: passed
