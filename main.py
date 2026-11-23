#!/usr/bin/env python3
"""Entrypoint for news-image-20261123 challenger6.

Renders entry.png (1024x1024, Monday 23 November 2026) by running
paint_n23v.py, then exits non-zero if any layout check recorded a
problem (overflowing text, crowded map pins, DATE CHECK text
touching its border, smoke escaping the hero-2 panel, the stat
strip off-centre inside its band, or any pixel clipped at the
canvas edge). The image is fully deterministic: two runs produce
identical bytes.
"""

from paint_n23v import main

if __name__ == "__main__":
    info = main()
    raise SystemExit(1 if info["problems"] else 0)
