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
  - 16 domain and configuration tests passed;
  - Vite production build passed;
  - npm audit reported 0 vulnerabilities;
  - no hooks, lint stack, UI framework, backend, or agent packs installed.
- Current phase: the approved static courier and three obstacle candidates are integrated; the traffic trap is fixed and the three-lane scale check is implemented. Next is owner approval of the scale gate before animation production.
- The in-app browser smoke test on 2026-08-15 confirmed that the local Phaser scene loads the courier and obstacle PNGs, interpolates lane position and scale, and renders the far and near lane states correctly; full-route feel remains an owner playtest gate.

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
| D-014 | Replace the front-heavy `v1` perspective with the side-profile `veh-001-courier-side-concept-v2.png`. | A horizontal left-to-right runner needs the long side plane to dominate; the new candidate uses an `85–90%` side view and only a narrow front plane. |
| D-015 | Approve `veh-001-courier-side-tapered-tube-concept-v3.png` as the courier design master. | The owner accepted the side-profile van and corrected tube taper on 2026-08-15; runtime production can use this version as its visual source. |
| D-016 | Limit each traffic formation to two vehicles and require an open lane within every `1,200 ms` spawn window. | Prevents the scattered three-car sequence and neighboring groups from creating an unfair full-road trap. |
| D-017 | Use a pink hatchback, yellow sedan, and green boxy wagon as the first playable traffic trio. | Distinct color, roofline, and wheelbase make obstacle recognition faster without competing with the turquoise courier. |
| D-018 | Use shared lane scale factors `0.88`, `0.94`, and `1.00` for vehicle visuals and collision rectangles. | Keeps the shallow 2.5D depth cue readable without allowing visible art and gameplay hitboxes to drift apart. |

## Open production questions

- Official brand-book and asset permission.
- Client website stack and iframe policy.
- Production campaign rules, legal copy, geography, dates, and inventory.
- Prize API, idempotency, rate limits, and fraud controls.
- Analytics provider and consent requirements.
