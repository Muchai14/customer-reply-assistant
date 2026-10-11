"""Demonstrate actual Git hook execution in a disposable repository only."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]


def main():
    executable = shutil.which("git")
    if executable is None:
        raise RuntimeError("Git is required")
    with TemporaryDirectory(prefix="reply-hook-demo-") as directory:
        repo = Path(directory)
        def git(*args):
            return subprocess.run([executable, "-C", str(repo), *args], capture_output=True, text=True, timeout=15)
        def checked(*args):
            result = git(*args)
            assert result.returncode == 0, result.stderr
            return result
        checked("init")
        checked("config", "user.name", "Fictional Demo")
        checked("config", "user.email", "demo@example.invalid")
        checked("config", "commit.gpgsign", "false")
        for folder in ("agent-hooks", ".githooks"):
            shutil.copytree(ROOT / folder, repo / folder)
        (repo / ".githooks/pre-commit").chmod(0o755)
        checked("config", "core.hooksPath", ".githooks")
        # Deliberately fake token, constructed here; never use a credential.
        (repo / "blocked.txt").write_text("ghp_" + "X" * 36 + "\n")
        checked("add", "blocked.txt")
        blocked = git("commit", "-m", "Must be blocked")
        assert blocked.returncode != 0 and "GitHub token pattern" in blocked.stderr
        assert git("rev-parse", "--verify", "HEAD").returncode != 0
        (repo / "blocked.txt").write_text("Fictional demo content only.\n")
        checked("add", "blocked.txt")
        accepted = checked("commit", "-m", "Safe fictional content")
        assert "guardrail passed" in accepted.stdout + accepted.stderr
        evidence = {"observed_at": datetime.now(timezone.utc).isoformat(),
                    "scope": "temporary repository; real project hook configuration unchanged",
                    "blocked_exit": blocked.returncode, "blocked_output": blocked.stderr.strip(),
                    "safe_commit_exit": accepted.returncode, "safe_commit_created": True,
                    "actual_pre_commit_hook_executed": True, "real_credentials_used": False}
    (ROOT / "docs/evidence/guardrail-demo.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: real pre-commit hook blocked a synthetic token and allowed safe content.")


if __name__ == "__main__":
    main()
