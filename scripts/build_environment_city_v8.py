"""Build the v8 city runtime with a gap-free, facade-safe cyclic crop."""

from pathlib import Path

import build_environment_city_v6 as builder


builder.REVIEW_ALPHA = Path("visual-references/environment-parallax-v8-alpha-review.png")
builder.REVIEW_COMPARISON = Path("visual-references/environment-parallax-v8-before-after.png")
builder.REVIEW_LOOP = Path("visual-references/environment-parallax-v8-loop-review.png")
builder.REVIEW_MOTION = Path("visual-references/environment-parallax-v8-motion-review.png")
builder.REVIEW_SEAM = Path("visual-references/environment-parallax-v8-seam-review.png")


if __name__ == "__main__":
    builder.main()
