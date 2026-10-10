import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_SCRIPT = REPOSITORY_ROOT / "scripts" / "apply-git-standards.sh"


def run(*command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


class GitStandardsIntegrationTests(unittest.TestCase):
    def test_bootstrap_baseline_hook_range_and_context_export(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            run("git", "init", "-q", cwd=repository)
            run(str(BOOTSTRAP_SCRIPT), str(repository), cwd=REPOSITORY_ROOT)

            baseline_file = repository / ".commit-documentation-baseline"
            self.assertFalse(baseline_file.exists())
            self.assertTrue((repository / "docs" / "commit-convention.md").exists())
            self.assertTrue((repository / "docs" / "commit-workflow.md").exists())

            run("git", "config", "user.name", "Test User", cwd=repository)
            run("git", "config", "user.email", "test@example.com", cwd=repository)
            (repository / "example.txt").write_text("legacy\n", encoding="utf-8")
            run("git", "add", "example.txt", cwd=repository)
            run("git", "commit", "--no-verify", "-qm", "legacy snapshot", cwd=repository)

            run(str(BOOTSTRAP_SCRIPT), str(repository), cwd=REPOSITORY_ROOT)
            baseline = baseline_file.read_text(encoding="utf-8").strip()
            self.assertEqual(baseline, run("git", "rev-parse", "HEAD", cwd=repository).stdout.strip())

            (repository / "example.txt").write_text(
                "legacy\ndocumented\n",
                encoding="utf-8",
            )
            message = repository / "message.txt"
            message.write_text(
                """feat(core): add documented behavior

Why:
The repository needs a representative post-baseline decision.

What changed:
- Added one documented line.

How to verify:
- Read example.txt -> the documented line exists.
""",
                encoding="utf-8",
            )
            run("git", "add", "example.txt", cwd=repository)
            run("git", "commit", "-qF", str(message), cwd=repository)

            commit_range = f"{baseline}..HEAD"
            run(
                "python3",
                "scripts/check_commit_message.py",
                "--commit-range",
                commit_range,
                cwd=repository,
            )
            run(
                "python3",
                "scripts/export_commit_context.py",
                "--commit-range",
                commit_range,
                "--output",
                "context.md",
                cwd=repository,
            )
            context = (repository / "context.md").read_text(encoding="utf-8")
            self.assertIn("feat(core): add documented behavior", context)


if __name__ == "__main__":
    unittest.main()