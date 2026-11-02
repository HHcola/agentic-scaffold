from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentic_scaffold.project import init_project
from agentic_scaffold.tasks import TaskError, TaskStore


class TaskStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        init_project(
            self.root,
            name="Task Test",
            initialize_git=False,
        )
        self.store = TaskStore.from_root(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_create_task_with_initial_artifacts(self) -> None:
        task = self.store.create(
            '实现 "搜索" 功能',
            priority="P0",
            description="返回相关结果。",
            tags=["search", "api"],
        )
        task_dir = self.store.root / task["id"]
        self.assertEqual(task["state"], "INTAKE")
        self.assertEqual(task["owner"], "orchestrator")
        self.assertTrue((task_dir / "task.json").is_file())
        self.assertTrue((task_dir / "brief.md").is_file())
        self.assertTrue((task_dir / "plan.md").is_file())
        self.assertTrue((task_dir / "journal.md").is_file())
        self.assertEqual(task["tags"], ["search", "api"])

    def test_full_delivery_transition_creates_stage_documents(self) -> None:
        task = self.store.create("Full flow")
        task_id = task["id"]
        for state in (
            "DISCOVERY",
            "DESIGN",
            "IMPLEMENTATION",
            "REVIEW",
            "VERIFICATION",
            "RELEASE",
            "DONE",
        ):
            task = self.store.move(task_id, state, note=f"enter {state}")

        self.assertEqual(task["state"], "DONE")
        task_dir = self.store.root / task_id
        for filename in (
            "brief.md",
            "design.md",
            "implementation.md",
            "review.md",
            "verification.md",
            "release.md",
        ):
            self.assertTrue((task_dir / filename).is_file(), filename)
        self.assertEqual(len(task["history"]), 8)

    def test_rejects_invalid_transition(self) -> None:
        task = self.store.create("Invalid")
        with self.assertRaises(TaskError):
            self.store.move(task["id"], "RELEASE")

    def test_block_and_resume(self) -> None:
        task = self.store.create("Blocked")
        task_id = task["id"]
        self.store.move(task_id, "DISCOVERY")
        blocked = self.store.move(task_id, "BLOCKED", note="waiting for access")
        self.assertEqual(blocked["previousState"], "DISCOVERY")
        self.assertEqual(blocked["blockedReason"], "waiting for access")
        resumed = self.store.move(task_id, "DESIGN", note="access granted")
        self.assertEqual(resumed["state"], "DESIGN")
        self.assertIsNone(resumed["previousState"])
        self.assertIsNone(resumed["blockedReason"])

    def test_force_is_recorded(self) -> None:
        task = self.store.create("Forced")
        moved = self.store.move(task["id"], "REVIEW", note="incident", force=True)
        self.assertTrue(moved["history"][-1]["forced"])

    def test_dashboard_escapes_task_content(self) -> None:
        self.store.create("<script>alert(1)</script>")
        dashboard = self.store.render_dashboard()
        self.assertIn("&lt;script&gt;", dashboard)
        self.assertNotIn("<script>alert(1)</script>", dashboard)


if __name__ == "__main__":
    unittest.main()
