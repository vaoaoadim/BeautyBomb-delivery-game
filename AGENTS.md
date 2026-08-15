# Repository Instructions

## Product

This repository contains an independent portfolio concept for a BeautyBomb promotional browser game. Never present it as an official BeautyBomb commission, campaign, partnership, or production integration.

## Source of truth

Read these files before non-trivial work:

1. \`docs/PROJECT.md\` for product behavior and locked visual decisions.
2. \`docs/ARCHITECTURE.md\` for module boundaries and integration rules.
3. \`docs/DECISIONS.md\` for the current phase and accepted decisions.
4. \`program.md\` for the iteration loop.

When documents conflict, stop and report the conflict. Do not silently choose the most convenient version.

## Working method

- Inspect the affected files before editing.
- Establish a baseline relevant to the task.
- Make one coherent, reviewable change at a time.
- Keep a change only when its acceptance criteria are met.
- Prefer deletion or a simpler implementation when quality is equal.
- Preserve unrelated user files and visual references.
- Do not add dependencies, hooks, agent packs, or new documentation layers without a concrete need.
- Do not publish, deploy, push, or change hosting without an explicit request.
- Never use destructive Git commands to discard user work.

## Architecture boundaries

- Keep deterministic game rules in framework-independent TypeScript.
- Phaser scenes render state and translate input; they must not own prize authority or host-site business logic.
- Keep host communication in \`src/integration/\`.
- Keep campaign content and tunable values in \`src/game/content/\` once that module is introduced.
- Demo rewards may be local and visibly marked as demonstrations. Production rewards must be issued by a server owned or approved by the client.
- The logical viewport remains portrait \`360 × 640\` unless the owner changes the product decision.

## Verification

Run only checks proportional to the change:

- TypeScript or game-rule change: \`npm run typecheck\` and relevant tests.
- Build/configuration change: \`npm run build\`.
- Functional phase completion: \`npm run verify\`.
- Documentation or reference-only change: inspect the diff; no full build required.

Do not add pre-commit hooks or automatic deep-review hooks. Report checks that actually ran.

## Definition of done

A change is complete when:

- it satisfies the current phase and task acceptance criteria;
- product behavior still matches \`docs/PROJECT.md\`;
- module boundaries remain consistent with \`docs/ARCHITECTURE.md\`;
- relevant checks pass;
- material decisions are recorded once in \`docs/DECISIONS.md\`;
- no placeholder business claims, real promo codes, secrets, or unlicensed production assets were introduced.

