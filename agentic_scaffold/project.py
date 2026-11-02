"""Project initialization and health checks."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import Any


CONFIG_PATH = Path(".agentic/config.json")
REQUIRED_FILES = (
    Path("AGENTS.md"),
    Path("agents/ORCHESTRATION.md"),
    Path("agents/shared/PRINCIPLES.md"),
    Path("workflows/delivery.md"),
    Path("context/project/OVERVIEW.md"),
)


class InitError(RuntimeError):
    """Raised when a project cannot be initialized safely."""


@dataclass
class InitResult:
    target: Path
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    git_initialized: bool = False


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def _template_root() -> Path:
    return Path(str(files("agentic_scaffold").joinpath("templates/project")))


def _render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
    if unresolved:
        raise InitError(f"模板中存在未解析变量: {', '.join(unresolved)}")
    return text


def _is_effectively_empty(path: Path) -> bool:
    if not path.exists():
        return True
    return not any(item.name != ".git" for item in path.iterdir())


def _initialize_git(target: Path) -> bool:
    if (target / ".git").exists():
        return False
    try:
        subprocess.run(
            ["git", "init", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(target), "symbolic-ref", "HEAD", "refs/heads/main"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        message = getattr(exc, "stderr", "") or str(exc)
        raise InitError(f"Git 仓库初始化失败: {message.strip()}") from exc
    return True


def init_project(
    target: Path,
    *,
    name: str,
    description: str = "",
    stack: str = "待补充",
    language: str = "zh-CN",
    adopt: bool = False,
    initialize_git: bool = True,
    dry_run: bool = False,
) -> InitResult:
    """Copy and render the project scaffold into ``target``."""
    target = target.expanduser().resolve()
    if target.exists() and not target.is_dir():
        raise InitError(f"目标不是目录: {target}")
    if not adopt and not _is_effectively_empty(target):
        raise InitError(
            f"目标目录非空: {target}。接入现有项目请使用 --adopt；"
            "接入时只会创建缺失文件，不覆盖已有文件。"
        )

    created_at = datetime.now().astimezone().isoformat(timespec="minutes")
    values = {
        "PROJECT_NAME": name,
        "PROJECT_SLUG": _slugify(name),
        "PROJECT_DESCRIPTION": description or "待补充项目简介。",
        "PRIMARY_STACK": stack or "待补充",
        "LANGUAGE": language,
        "CREATED_AT": created_at,
    }
    json_values = {
        key: json.dumps(value, ensure_ascii=False)[1:-1] for key, value in values.items()
    }
    result = InitResult(target=target)
    source_root = _template_root()

    for source in sorted(source_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(source_root)
        destination = target / relative
        if destination.exists():
            result.skipped.append(relative)
            continue
        render_values = json_values if relative == CONFIG_PATH else values
        rendered = _render(source.read_text(encoding="utf-8"), render_values)
        result.created.append(relative)
        if dry_run:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        if relative == Path("scripts/agentic"):
            os.chmod(destination, 0o755)

    if dry_run:
        return result

    if initialize_git and not adopt:
        result.git_initialized = _initialize_git(target)
    return result


def load_config(root: Path) -> dict[str, Any]:
    config_path = root.resolve() / CONFIG_PATH
    if not config_path.exists():
        raise InitError(f"缺少配置文件: {config_path}")
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InitError(f"配置文件无法读取: {exc}") from exc
    if not isinstance(data, dict):
        raise InitError("配置文件顶层必须是 JSON object")
    return data


def doctor(root: Path) -> tuple[list[str], list[str]]:
    """Return repository health errors and advisory warnings."""
    root = root.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"缺少必需文件: {relative}")

    try:
        config = load_config(root)
    except InitError as exc:
        return errors + [str(exc)], warnings

    if config.get("schemaVersion") != 1:
        errors.append("仅支持 schemaVersion=1")
    project = config.get("project")
    if not isinstance(project, dict) or not project.get("name"):
        errors.append(".agentic/config.json 缺少 project.name")
    workflow = config.get("workflow")
    if not isinstance(workflow, dict):
        errors.append(".agentic/config.json 缺少 workflow")
    else:
        task_root = workflow.get("taskRoot")
        if not isinstance(task_root, str) or not task_root.strip():
            errors.append("workflow.taskRoot 必须是非空字符串")
        elif Path(task_root).is_absolute() or ".." in Path(task_root).parts:
            errors.append("workflow.taskRoot 必须是项目内相对路径")

    overview = root / "context/project/OVERVIEW.md"
    if overview.exists() and "待补充" in overview.read_text(encoding="utf-8"):
        warnings.append("context/project/OVERVIEW.md 仍有“待补充”内容")
    if not (root / ".gitignore").exists():
        warnings.append("缺少 .gitignore")
    if not (root / ".git").exists():
        warnings.append("当前目录尚未初始化 Git 仓库")
    return errors, warnings
