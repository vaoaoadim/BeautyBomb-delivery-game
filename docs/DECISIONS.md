# Decision Log

Keep this file short. Record only decisions that change product behavior, architecture, integration, scope, or long-term maintenance.

## Current phase

- Completed phase: environment and architecture.
- Completed on: 2026-08-15.
- Evidence:
  - Git repository initialized on \`main\`;
  - source-of-truth documents and lean agent instructions added;
  - 360 × 640 Phaser canvas bootstrap added;
  - TypeScript check passed;
  - 2 configuration tests passed;
  - Vite production build passed;
  - npm audit reported 0 vulnerabilities;
  - no hooks, lint stack, UI framework, backend, or agent packs installed.
- Current phase: ready for deterministic greybox.
- Greybox entry condition: owner approves starting implementation.

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

## Open production questions

- Official brand-book and asset permission.
- Client website stack and iframe policy.
- Production campaign rules, legal copy, geography, dates, and inventory.
- Prize API, idempotency, rate limits, and fraud controls.
- Analytics provider and consent requirements.
