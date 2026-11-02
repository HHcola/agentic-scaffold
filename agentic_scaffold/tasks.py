"""Local-first task storage and workflow state machine."""

from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .project import load_config


STATES = (
    "INTAKE",
    "DISCOVERY",
    "DESIGN",
    "IMPLEMENTATION",
    "REVIEW",
    "VERIFICATION",
    "RELEASE",
    "DONE",
    "BLOCKED",
    "CANCELLED",
)

DEFAULT_OWNER = {
    "INTAKE": "orchestrator",
    "DISCOVERY": "product",
    "DESIGN": "architect",
    "IMPLEMENTATION": "developer",
    "REVIEW": "reviewer",
    "VERIFICATION": "qa",
    "RELEASE": "release",
    "DONE": "orchestrator",
    "BLOCKED": "orchestrator",
    "CANCELLED": "orchestrator",
}

TRANSITIONS = {
    "INTAKE": {"DISCOVERY", "BLOCKED", "CANCELLED"},
    "DISCOVERY": {"DESIGN", "BLOCKED", "CANCELLED"},
    "DESIGN": {"DISCOVERY", "IMPLEMENTATION", "BLOCKED", "CANCELLED"},
    "IMPLEMENTATION": {"DESIGN", "REVIEW", "BLOCKED", "CANCELLED"},
    "REVIEW": {"IMPLEMENTATION", "VERIFICATION", "BLOCKED", "CANCELLED"},
    "VERIFICATION": {
        "IMPLEMENTATION",
        "RELEASE",
        "BLOCKED",
        "CANCELLED",
    },
    "RELEASE": {"VERIFICATION", "DONE", "BLOCKED", "CANCELLED"},
    "DONE": set(),
    "BLOCKED": {
        "INTAKE",
        "DISCOVERY",
        "DESIGN",
        "IMPLEMENTATION",
        "REVIEW",
        "VERIFICATION",
        "RELEASE",
        "CANCELLED",
    },
    "CANCELLED": set(),
}

STAGE_ARTIFACTS = {
    "DISCOVERY": "brief.md",
    "DESIGN": "design.md",
    "IMPLEMENTATION": "implementation.md",
    "REVIEW": "review.md",
    "VERIFICATION": "verification.md",
    "RELEASE": "release.md",
}

ARTIFACT_TEMPLATES = {
    "brief.md": """# 需求简报

## 问题与目标

<!-- 描述用户问题、业务目标和不做什么。 -->

## 已知事实

- [待补充]

## 待确认问题

- [ ] [待补充]

## 验收摘要

- [ ] [待补充可验证的验收条件]
""",
    "plan.md": """# 交付计划

## 范围

- [待补充]

## 里程碑

1. [待补充]

## 风险与依赖

| 风险 | 影响 | 缓解措施 | Owner |
| --- | --- | --- | --- |
| [待补充] | [待补充] | [待补充] | [待补充] |
""",
    "design.md": """# 技术设计

## 方案摘要

<!-- 先给结论，再给关键理由。 -->

## 约束与权衡

- [待补充]

## 接口与数据变化

- [待补充；没有则写“无”]

## 安全、隐私与兼容性

- [待补充]

## 测试策略

- [待补充]
""",
    "implementation.md": """# 实现记录

## 变更清单

- [待补充：文件 + 行为变化]

## 本地验证

| 命令 | 结果 | 说明 |
| --- | --- | --- |
| [待补充] | [待补充] | [待补充] |

## 未完成项与已知限制

- [无 / 待补充]
""",
    "review.md": """# 独立评审

## 结论

- [ ] 通过
- [ ] 需要修改

## 发现

| 级别 | 位置 | 问题 | 建议 |
| --- | --- | --- | --- |
| [待补充] | [待补充] | [待补充] | [待补充] |

## 回归风险

- [待补充]
""",
    "verification.md": """# 验收报告

## 环境

- [待补充]

## 自动化验证

| 命令 | 结果 | 证据 |
| --- | --- | --- |
| [待补充] | [待补充] | [待补充] |

## 人工验证

- [ ] [待补充]

## 缺陷

- [无 / 待补充]
""",
    "release.md": """# 发布计划

## 发布内容

- [待补充]

## 发布步骤

1. [待补充]

## 回滚方案

1. [待补充]

## 观测项

- [待补充]
""",
}


class TaskError(RuntimeError):
    """Raised for invalid task operations."""


@dataclass(frozen=True)
class TaskStore:
    root: Path

    @classmethod
    def from_root(cls, root: Path) -> "TaskStore":
        config = load_config(root)
        workflow = config.get("workflow", {})
        task_root = workflow.get("taskRoot", "work")
        return cls((root / task_root).resolve())

    def create(
        self,
        title: str,
        *,
        task_type: str = "feature",
        priority: str = "P1",
        owner: str | None = None,
        description: str = "",
        tags: Iterable[str] = (),
    ) -> dict[str, Any]:
        if not title.strip():
            raise TaskError("任务标题不能为空")
        if task_type not in {"feature", "bug", "spike", "chore"}:
            raise TaskError("任务类型必须是 feature、bug、spike 或 chore")
        if priority not in {"P0", "P1", "P2", "P3"}:
            raise TaskError("优先级必须是 P0、P1、P2 或 P3")

        self.root.mkdir(parents=True, exist_ok=True)
        for _ in range(10_000):
            task_id = self._next_id()
            task_dir = self.root / task_id
            try:
                task_dir.mkdir()
                break
            except FileExistsError:
                continue
        else:
            raise TaskError("无法分配任务 ID")

        now = _now()
        task = {
            "schemaVersion": 1,
            "id": task_id,
            "title": title.strip(),
            "type": task_type,
            "priority": priority,
            "state": "INTAKE",
            "owner": owner or DEFAULT_OWNER["INTAKE"],
            "createdAt": now,
            "updatedAt": now,
            "previousState": None,
            "blockedReason": None,
            "tags": [tag.strip() for tag in tags if tag.strip()],
            "links": [],
            "history": [
                {
                    "at": now,
                    "from": None,
                    "to": "INTAKE",
                    "owner": owner or DEFAULT_OWNER["INTAKE"],
                    "note": "创建任务",
                }
            ],
        }
        self._write(task_dir / "task.json", task)
        self._write(
            task_dir / "brief.md",
            _with_task_header(
                task,
                ARTIFACT_TEMPLATES["brief.md"],
                description=description,
            ),
        )
        self._write(task_dir / "plan.md", _with_task_header(task, ARTIFACT_TEMPLATES["plan.md"]))
        self._write(
            task_dir / "journal.md",
            f"# 执行日志 · {task_id}\n\n"
            f"- {now} · orchestrator · 创建任务，状态为 `INTAKE`。\n",
        )
        return task

    def get(self, task_id: str) -> dict[str, Any]:
        task_dir = self.find(task_id)
        try:
            data = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TaskError(f"任务元数据无法读取: {task_dir / 'task.json'}") from exc
        if not isinstance(data, dict) or data.get("id") != task_id:
            raise TaskError(f"任务元数据格式错误: {task_id}")
        return data

    def find(self, task_id: str) -> Path:
        if not re.fullmatch(r"TASK-\d{8}-\d{3,}", task_id):
            raise TaskError(f"非法任务 ID: {task_id}")
        path = self.root / task_id
        if not (path / "task.json").is_file():
            raise TaskError(f"任务不存在: {task_id}")
        return path

    def move(
        self,
        task_id: str,
        new_state: str,
        *,
        note: str = "",
        owner: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        new_state = new_state.upper()
        if new_state not in STATES:
            raise TaskError(f"未知状态: {new_state}")
        task = self.get(task_id)
        old_state = task["state"]
        allowed = TRANSITIONS.get(old_state, set())
        if new_state == old_state:
            raise TaskError(f"任务已处于 {new_state}")
        if new_state not in allowed and not force:
            choices = ", ".join(sorted(allowed)) or "无"
            raise TaskError(
                f"不允许从 {old_state} 流转到 {new_state}；允许: {choices}。"
                "如确需跳转，使用 --force。"
            )

        now = _now()
        previous_state = task.get("previousState")
        if new_state == "BLOCKED":
            task["previousState"] = old_state
            task["blockedReason"] = note or "未说明阻塞原因"
        elif old_state == "BLOCKED":
            task["previousState"] = None
            task["blockedReason"] = None
        else:
            previous_state = task.get("previousState")
            task["previousState"] = previous_state

        task["state"] = new_state
        task["owner"] = owner or DEFAULT_OWNER[new_state]
        task["updatedAt"] = now
        task.setdefault("history", []).append(
            {
                "at": now,
                "from": old_state,
                "to": new_state,
                "owner": task["owner"],
                "note": note,
                "forced": bool(force and new_state not in allowed),
            }
        )
        task_dir = self.find(task_id)
        self._write(task_dir / "task.json", task)

        artifact = STAGE_ARTIFACTS.get(new_state)
        if artifact and not (task_dir / artifact).exists():
            self._write(task_dir / artifact, _with_task_header(task, ARTIFACT_TEMPLATES[artifact]))
        self._journal(
            task_dir,
            f"- {now} · {task['owner']} · `{old_state}` → `{new_state}`"
            + (f" · {note}" if note else ""),
        )
        return task

    def list(self) -> list[dict[str, Any]]:
        if not self.root.exists():
            return []
        tasks: list[dict[str, Any]] = []
        for task_dir in sorted(self.root.glob("TASK-*")):
            if not (task_dir / "task.json").is_file():
                continue
            try:
                tasks.append(self.get(task_dir.name))
            except TaskError:
                continue
        return tasks

    def summary(self) -> dict[str, Any]:
        tasks = self.list()
        counts = {state: 0 for state in STATES}
        for task in tasks:
            counts[task["state"]] = counts.get(task["state"], 0) + 1
        active_states = set(STATES) - {"DONE", "CANCELLED"}
        return {
            "total": len(tasks),
            "active": sum(counts[state] for state in active_states),
            "blocked": counts["BLOCKED"],
            "done": counts["DONE"],
            "byState": counts,
        }

    def render_dashboard(self) -> str:
        tasks = self.list()
        summary = self.summary()
        cards = [
            ("任务总数", summary["total"]),
            ("进行中", summary["active"]),
            ("阻塞", summary["blocked"]),
            ("已完成", summary["done"]),
        ]
        card_html = "".join(
            f'<section class="metric"><span>{html.escape(label)}</span><strong>{value}</strong></section>'
            for label, value in cards
        )
        rows = []
        for task in tasks:
            rows.append(
                "<tr>"
                f"<td><code>{html.escape(task['id'])}</code></td>"
                f"<td>{html.escape(task['title'])}</td>"
                f"<td><span class=\"state state-{html.escape(task['state'].lower())}\">"
                f"{html.escape(task['state'])}</span></td>"
                f"<td>{html.escape(task['owner'])}</td>"
                f"<td>{html.escape(task['priority'])}</td>"
                f"<td>{html.escape(task['updatedAt'])}</td>"
                "</tr>"
            )
        body_rows = "\n".join(rows) or (
            '<tr><td colspan="6" class="empty">暂无任务。'
            "运行 <code>agentic-scaffold task new \"首个任务\"</code> 开始。</td></tr>"
        )
        generated = html.escape(_now())
        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agentic Scaffold · Delivery Board</title>
  <style>
    :root {{ color-scheme: light; --ink: #122019; --muted: #607067; --line: #dce5df;
      --green: #146b47; --paper: #f4f7f4; --white: #fff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--ink); background: var(--paper);
      font: 15px/1.55 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    main {{ width: min(1180px, calc(100% - 40px)); margin: 48px auto 80px; }}
    header {{ display: flex; justify-content: space-between; align-items: end; gap: 24px; }}
    h1 {{ margin: 0; font-size: clamp(28px, 5vw, 52px); letter-spacing: -0.04em; }}
    .eyebrow {{ color: var(--green); font-weight: 750; text-transform: uppercase;
      letter-spacing: .12em; font-size: 12px; }}
    .generated {{ color: var(--muted); text-align: right; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 30px 0; }}
    .metric {{ padding: 20px; border: 1px solid var(--line); border-radius: 16px;
      background: var(--white); box-shadow: 0 8px 24px rgb(22 48 33 / 5%); }}
    .metric span {{ display: block; color: var(--muted); }}
    .metric strong {{ display: block; margin-top: 8px; font-size: 34px; }}
    .panel {{ overflow: auto; border: 1px solid var(--line); border-radius: 16px; background: var(--white); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 820px; }}
    th, td {{ padding: 15px 18px; text-align: left; border-bottom: 1px solid var(--line); }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    tr:last-child td {{ border-bottom: 0; }}
    .state {{ display: inline-block; padding: 4px 9px; border-radius: 999px;
      color: #17442f; background: #e5f1e9; font-size: 12px; font-weight: 700; }}
    .state-blocked {{ color: #7b2b14; background: #fee9df; }}
    .state-done {{ color: #fff; background: var(--green); }}
    .empty {{ padding: 44px; color: var(--muted); text-align: center; }}
    code {{ font: 13px ui-monospace, SFMono-Regular, Menlo, monospace; }}
    @media (max-width: 720px) {{
      main {{ width: min(100% - 24px, 1180px); margin-top: 28px; }}
      header {{ align-items: start; flex-direction: column; }}
      .generated {{ text-align: left; }}
      .metrics {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div><div class="eyebrow">Agentic Scaffold</div><h1>交付工作台</h1></div>
      <div class="generated">本地生成 · {generated}</div>
    </header>
    <div class="metrics">{card_html}</div>
    <div class="panel">
      <table>
        <thead><tr><th>ID</th><th>标题</th><th>状态</th><th>Owner</th><th>优先级</th><th>更新时间</th></tr></thead>
        <tbody>{body_rows}</tbody>
      </table>
    </div>
  </main>
</body>
</html>
"""

    def _next_id(self) -> str:
        date = datetime.now().strftime("%Y%m%d")
        prefix = f"TASK-{date}-"
        max_number = 0
        for path in self.root.glob(f"{prefix}*"):
            match = re.fullmatch(rf"{re.escape(prefix)}(\d+)", path.name)
            if match:
                max_number = max(max_number, int(match.group(1)))
        return f"{prefix}{max_number + 1:03d}"

    @staticmethod
    def _write(path: Path, data: str | dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, dict):
            content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        else:
            content = data
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(content, encoding="utf-8")
        os.replace(temp, path)

    @staticmethod
    def _journal(task_dir: Path, line: str) -> None:
        journal = task_dir / "journal.md"
        with journal.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _with_task_header(task: dict[str, Any], body: str, description: str = "") -> str:
    header = (
        f"# {task['title']}\n\n"
        f"> 任务：`{task['id']}` · 类型：`{task['type']}` · 优先级：`{task['priority']}`\n"
        f"> Owner：`{task['owner']}` · 状态：`{task['state']}`\n\n"
    )
    if description:
        header += f"## 初始描述\n\n{description.strip()}\n\n---\n\n"
    title_end = body.find("\n")
    return header + body[title_end + 1 :].lstrip()
