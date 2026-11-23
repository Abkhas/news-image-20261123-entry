# news-image-20261123 — challenger 6

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Abkhas/news-image-20261123-entry/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Abkhas/news-image-20261123-entry/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

30-story dense family, Monday 23 November 2026. Challenger to the
live challenger2 entry: fixes the two small things Khase found by
eye on challenger5 (the numbers + labels in the navy stat band sit
slightly low inside the band -- they are now centred by PIL ink
measurement, 6px of air above and below; the hero-2 fire still
reads as a mountain -- it is now separate thin flickering tongues
with dark gaps between them, a flat ember strip along the sill,
and no enclosing disc or shared axis). Same 30 stories, same
heroes; only the rendering changes.

- `main.py` — entry program; renders `entry.png` and fails if any
  layout check records a problem.
- `paint_n23v.py` — draws the 1024x1024 image in code (PIL only),
  written fresh for this candidate. Every scene is rendered on its
  own layer and pasted in, so no scene can leak past its panel.
- `entry.png` — the rendered image (deterministic, two runs identical).

SPDX-License-Identifier: MIT
