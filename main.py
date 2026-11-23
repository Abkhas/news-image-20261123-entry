#!/usr/bin/env python3
"""Entrypoint for the n23 challenger6 news-image entry.

The image is pre-rendered and committed as entry.png next to this script.
This entrypoint only copies it into the grader's output folder. It does
no drawing, no network access and no randomness, so it runs in the pinned
grader image (read-only /bot, no fonts beyond the stdlib, no network).
"""

import os
import shutil
import sys
from pathlib import Path

MAX_BYTES = 1_048_576


def main() -> int:
    src = Path(__file__).resolve().parent / "entry.png"
    if not src.is_file():
        print(f"error: entry.png not found next to main.py ({src})", file=sys.stderr)
        return 1

    size = src.stat().st_size
    if size > MAX_BYTES:
        print(
            f"error: entry.png is {size} bytes, over the {MAX_BYTES} byte limit",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(src, dest)
    print(f"Wrote {dest} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
