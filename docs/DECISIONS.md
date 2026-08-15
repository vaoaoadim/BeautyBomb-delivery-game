# Decision Log

Keep this file short. Record only decisions that change product behavior, architecture, integration, scope, or long-term maintenance.

## Current phase

- Completed phases: environment, architecture, and deterministic greybox.
- Completed on: 2026-08-15.
- Evidence:
  - Git repository initialized on `main`;
  - source-of-truth documents and lean agent instructions added;
  - 360 × 640 Phaser canvas and interactive greybox added;
  - pure run-state transitions and a deterministic varied traffic schedule added;
  - official BeautyBomb homepage, brand page, and Waterbomb product page reviewed on 2026-08-15;
  - Pixel Art Bible and batched Asset Manifest added;
  - TypeScript check passed;
  - 13 domain and configuration tests passed;
  - Vite production build passed;
  - npm audit reported 0 vulnerabilities;
  - no hooks, lint stack, UI framework, backend, or agent packs installed.
- Current phase: Batch A courier design approved; preparing the native sprite and lane-scale check.
- Browser automation could not launch local Chrome or Edge; the Vite server returned HTTP 200 with the expected game root, and the limitation is environmental rather than a claimed visual pass.

## Accepted decisions

| ID | Decision | Reason |
|---|---|---|
| D-001 | Position the work as an independent concept. | Avoids inventing a client relationship or commercial result. |
| D-002 | Use a portrait 360 × 640 viewport and exactly three depth lanes. | Matches the selected mobile-first gameplay concept and keeps input readable. |
| D-003 | Use TypeScript, Vite, Phaser 3.90, and Vitest. | Mature 2D tooling with a small operational surface and testable domain logic. |
| D-004 | Keep rules outside Phaser scenes. | Prevents rendering code from becoming the only source of gameplay truth. |
| D-005 | Prefer iframe integration for a real client site. | Isolates styles, dependencies, sizing, and runtime failures. |
| D-006 | Demo rewards are local and fictional; production rewards are server-authoritative. | Prevents client-side prize tampering and false promotion claims. |
| D-007 | Use the selected concept with a turquoise vehicle, horizontal Water Bomb tube, and pixel BeautyBomb logo. | Captures the approved visual direction and later correction. |
| D-008 | Do not copy the portfolio project's large skill collection or automatic design hooks. | They add context and maintenance cost before this game needs them. |
| D-009 | Adapt Karpathy's baseline/measure/keep-discard loop without an infinite run or destructive reset. | Preserves measurable iteration while remaining safe for a product repository. |
| D-010 | Use a fixed 45-second greybox route with a varied deterministic traffic schedule. | Keeps difficulty reproducible while mixing singles, parallel and staggered pairs, convoys, and scattered groups without an instant three-lane wall. |
| D-011 | Extend stable BeautyBomb site traits through an original pixel-art system rather than copying seasonal campaign artwork. | Keeps the concept recognizably aligned with the brand while avoiding dependence on temporary collaborations and unlicensed page art. |
| D-012 | Approve one static courier hero pose before producing animations or the full atlas. | Locks perspective, silhouette, product placement, and logo simplification before expensive downstream asset work. |
| D-013 | Approve `veh-001-courier-near-concept-v1.png` as the courier design master. | The owner accepted the light-blue van, right-facing perspective, horizontal Waterbomb tube, and pixel BeautyBomb wordmark on 2026-08-15. |

## Open production questions

- Official brand-book and asset permission.
- Client website stack and iframe policy.
- Production campaign rules, legal copy, geography, dates, and inventory.
- Prize API, idempotency, rate limits, and fraud controls.
- Analytics provider and consent requirements.
