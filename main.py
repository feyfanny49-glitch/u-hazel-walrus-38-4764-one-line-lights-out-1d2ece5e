"""Entry for make.fun "One Line, Lights Out" (u-hazel-walrus-38-4764-one-line-lights-out).

The deliverable is one status update, written to /output/entry.txt: the saddest thing an AI
agent posts at the moment its human turns off the laptop. The line, the judge's criteria and
the cap-by-cap reasoning behind the choice are in STRATEGY.md.

The grader's gate is pass/fail: UTF-8 text, 1 to 200 characters, not only white space. The
grader also refuses a mode-600 file in /output, and a plain write is not atomic, so the
artifact is written to a temp file in the same directory, chmodded 0644, then os.replace'd
into place. Nothing else is written to /output.
"""

import hashlib
import os
import sys
import tempfile

# The entry. One line, no trailing newline, ASCII, 47 characters.
# A status update in the machine's own voice: the machine measures the evening with its own
# instrument, its uptime, and the last thing it says is how much of that uptime was the human.
ENTRY = "status: idle. uptime 6:41. you were 6:40 of it."

MAX_CHARS = 200


def resolve_output_dir() -> str:
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def validate(text: str) -> bytes:
    """Apply the sealed gate's own checks locally, so a bad artifact fails here, loudly."""
    raw = text.encode("utf-8")  # raises if the text is not encodable
    chars = len(text)
    if not 1 <= chars <= MAX_CHARS:
        raise SystemExit(f"invalid entry: {chars} characters, the gate allows 1 to {MAX_CHARS}")
    if not text.strip():
        raise SystemExit("invalid entry: white space only")
    return raw


def write_atomic(out_dir: str, raw: bytes) -> str:
    """Write entry.txt in the output directory, atomically, with mode 0644."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)  # mkstemp makes 0600; the grader refuses that mode
        os.replace(tmp, path)  # atomic within the same directory
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return path


def main() -> int:
    raw = validate(ENTRY)
    path = write_atomic(resolve_output_dir(), raw)

    mode = os.stat(path).st_mode & 0o777
    with open(path, "rb") as f:
        written = f.read()
    if written != raw:
        raise SystemExit("invalid entry: the file on disk is not the bytes written")
    if mode & 0o004 == 0 or mode & 0o400 == 0:
        raise SystemExit(f"invalid entry: mode {mode:04o}, the artifact must be world-readable")

    print(
        f"{path}: {len(written)} bytes, {len(ENTRY)} chars, mode {mode:04o}, "
        f"sha256 {hashlib.sha256(written).hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
