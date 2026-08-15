# Development Program

This file adapts the small, measurable loop from Andrej Karpathy's \`autoresearch\` repository to product development. It is intentionally short.

## Start

1. Read \`AGENTS.md\`, \`docs/PROJECT.md\`, \`docs/ARCHITECTURE.md\`, and the current section of \`docs/DECISIONS.md\`.
2. Inspect Git status and preserve unrelated changes.
3. Define one concrete outcome and its acceptance criteria.
4. Run the smallest baseline check that can measure the outcome.

## Iteration loop

For each implementation hypothesis:

1. State the hypothesis in one sentence.
2. Change one coherent area only.
3. Run the targeted check.
4. Compare against the baseline and acceptance criteria.
5. Keep the change if it improves correctness, clarity, performance, or maintainability without disproportionate complexity.
6. Otherwise, discard only that change through a safe patch or revert. Never use \`git reset --hard\`.
7. Record only material kept decisions in \`docs/DECISIONS.md\`; do not turn the log into a diary.

## Fixed evaluation rules

- Do not weaken a test or acceptance criterion to make an implementation pass.
- Do not change the product requirement and its implementation in the same step without recording the decision.
- For gameplay work, prefer deterministic tests over visual judgment where possible.
- For visual work, compare against the selected concept at the target viewport.
- For performance work, record the same metric before and after.

## Simplicity criterion

When two approaches satisfy the same acceptance criteria, keep the one with fewer dependencies, fewer moving parts, and clearer ownership. Small gains do not justify a large maintenance cost.

## Stop condition

Stop when the current task is complete or a decision requires owner input. This project does not use an unattended infinite loop.
