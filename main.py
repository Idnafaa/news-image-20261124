# main.py — entrypoint for "The World in One Day — 24 November 2026".
#
# The poster itself is rendered at build time by render.py and committed
# as entry.png. All this program does is place those exact bytes at
# /output/entry.png. Pure Python 3.13 standard library, no network,
# fully deterministic: the same input always produces the same output.
import os
import shutil
import sys


def run():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    os.makedirs("/output", exist_ok=True)
    dst = os.path.join("/output", "entry.png")
    shutil.copyfile(src, dst)
    print("wrote %s (%d bytes)" % (dst, os.path.getsize(dst)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
