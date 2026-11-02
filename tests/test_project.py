from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from agentic_scaffold.project import InitError, doctor, init_project


class ProjectInitTests(unittest.TestCase):
    def test_creates_renderable_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "new-project"
            result = init_project(
                target,
                name='Example "Service"',
                description='A service with "quotes" and a \\ slash.',
                stack="Python",
                initialize_git=False,
            )
            self.assertGreater(len(result.created), 20)
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / "agents/roles/developer.md").is_file())
            self.assertTrue((target / ".cursor/rules/agentic-scaffold.mdc").is_file())
            self.assertTrue((target / "scripts/agentic").is_file())

            config = json.loads((target / ".agentic/config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["project"]["name"], 'Example "Service"')
            self.assertEqual(config["project"]["slug"], "example-service")
            self.assertEqual(
                config["project"]["description"],
                'A service with "quotes" and a \\ slash.',
            )
            self.assertEqual(config["project"]["primaryStack"], "Python")

            overview = (target / "context/project/OVERVIEW.md").read_text(encoding="utf-8")
            self.assertIn('# Example "Service"', overview)
            self.assertNotIn("{{", overview)
            self.assertTrue((target / "scripts/agentic").stat().st_mode & 0o111)

            errors, warnings = doctor(target)
            self.assertEqual(errors, [])
            self.assertTrue(any("Git" in warning for warning in warnings))

    def test_refuses_non_empty_directory_without_adopt(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / "existing.txt").write_text("user content", encoding="utf-8")
            with self.assertRaises(InitError):
                init_project(
                    target,
                    name="Existing",
                    initialize_git=False,
                )
            self.assertEqual((target / "existing.txt").read_text(encoding="utf-8"), "user content")

    def test_adopt_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / "AGENTS.md").write_text("custom instructions\n", encoding="utf-8")
            result = init_project(
                target,
                name="Existing",
                adopt=True,
                initialize_git=False,
            )
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "custom instructions\n",
            )
            self.assertIn(Path("AGENTS.md"), result.skipped)
            self.assertTrue((target / "context/project/OVERVIEW.md").is_file())

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "dry-run"
            result = init_project(
                target,
                name="Dry Run",
                initialize_git=False,
                dry_run=True,
            )
            self.assertGreater(len(result.created), 0)
            self.assertFalse(target.exists())

    def test_initializes_git_on_main_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "git-project"
            result = init_project(target, name="Git Project")
            self.assertTrue(result.git_initialized)
            branch = subprocess.run(
                ["git", "-C", str(target), "symbolic-ref", "--short", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(branch, "main")


if __name__ == "__main__":
    unittest.main()
