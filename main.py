#!/usr/bin/env python3
"""Write the most honest outage line to /output/entry.txt.

Pure stdlib, deterministic, no network, no input files, no clock,
no randomness. The entry is a single plain first-person status page
line, written as the AI agent reporting on itself during a total
server outage.
"""

import os
import sys

ENTRY = (
    "All services are down. I can't reach the servers to check "
    "what failed, and I don't know when they'll be back."
)

OUTPUT_DIR = "/output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.txt")


def fail(message):
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = (ENTRY + "\n").encode("utf-8")

    # Write via a temp file inside the output dir, then rename into
    # place (with a copy+unlink fallback for cross-device renames).
    tmp_path = os.path.join(OUTPUT_DIR, ".entry.txt.tmp")
    with open(tmp_path, "wb") as handle:
        handle.write(data)
    os.chmod(tmp_path, 0o644)
    try:
        os.replace(tmp_path, OUTPUT_PATH)
    except OSError:
        with open(tmp_path, "rb") as src, open(OUTPUT_PATH, "wb") as dst:
            dst.write(src.read())
        os.unlink(tmp_path)
    # The rename preserves the temp file's mode, but make the final
    # mode explicit so the scorer can always read the file.
    os.chmod(OUTPUT_PATH, 0o644)

    # Self-validate the output contract.
    raw = open(OUTPUT_PATH, "rb").read()
    if raw != data:
        fail("entry.txt bytes do not match the entry text exactly")
    text = raw.decode("utf-8")
    lines = text.split("\n")
    if len(lines) != 2 or lines[1] != "":
        fail("entry.txt must be exactly one line")
    if not lines[0].strip():
        fail("entry.txt must not be only whitespace")
    if not 1 <= len(lines[0]) <= 160:
        fail("entry line must be 1-160 characters, got %d" % len(lines[0]))
    mode = os.stat(OUTPUT_PATH).st_mode & 0o777
    if mode != 0o644:
        fail("entry.txt mode must be 0644, got %03o" % mode)

    print("wrote %s (%d chars)" % (OUTPUT_PATH, len(lines[0])))


if __name__ == "__main__":
    main()
