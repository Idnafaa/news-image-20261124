# main.py — entrypoint for "The World in One Day — 24 November 2026".
#
# render.py produces the poster at build time and it ships in the repo
# as entry.png. Running this program only places that exact file at
# /output/entry.png, byte for byte. It uses nothing but the Python
# 3.13 standard library, touches no network, and always gives the
# same result for the same input.
import shutil
import sys
from pathlib import Path


def run():
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    destination = Path("/output") / "entry.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    size = destination.stat().st_size
    print("wrote %s (%d bytes)" % (destination, size))
    return 0


if __name__ == "__main__":
    sys.exit(run())
