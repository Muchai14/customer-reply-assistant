"""Block selected secret patterns and private runtime files in staged Git blobs.

Exit 1 for findings, 2 for scanner errors. Never prints matched secret values.
This narrow guardrail is not a comprehensive secret scanner.
"""
from pathlib import Path
import re
import subprocess
import shutil
import sys

PATTERNS = [
    ("private-key header", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token pattern", re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("AWS access-key pattern", re.compile(rb"\bAKIA[A-Z0-9]{16}\b")),
]


def inspect(name, data):
    path = Path(name)
    reasons = []
    if path.name == ".env" or (path.name.startswith(".env.") and path.name not in {".env.example", ".env.sample"}):
        reasons.append("environment secret file")
    if path.name.endswith((".db", ".db-wal", ".db-shm")):
        reasons.append("runtime database file")
    for label, pattern in PATTERNS:
        if pattern.search(data):
            reasons.append(label)
    return reasons


def run(repo):
    git_executable = shutil.which("git")
    if git_executable is None:
        print("Git is unavailable; commit blocked.", file=sys.stderr)
        return 2

    def git(*args):
        return subprocess.run([git_executable, "-C", str(repo), *args], check=True, capture_output=True).stdout
    try:
        names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0")
        findings = []
        for raw in filter(None, names):
            name = raw.decode("utf-8", errors="surrogateescape")
            # Read the exact staged blob, not the potentially different working file.
            size = int(git("cat-file", "-s", ":" + name))
            if size > 5_000_000:
                findings.append((name, "file exceeds 5 MB guardrail limit; review manually"))
                continue
            data = git("show", ":" + name)
            findings.extend((name, reason) for reason in inspect(name, data))
    except (subprocess.CalledProcessError, OSError, ValueError):
        print("Guardrail could not inspect staged files; commit blocked.", file=sys.stderr)
        return 2
    for name, reason in findings:
        print(f"BLOCKED {name!r}: {reason}", file=sys.stderr)
    if findings:
        return 1
    print("Staged-file guardrail passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()))
