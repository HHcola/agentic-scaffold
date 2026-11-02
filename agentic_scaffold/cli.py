"""Command-line interface for Agentic Scaffold."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .project import InitError, doctor, init_project
from .tasks import DEFAULT_OWNER, STATES, TaskError, TaskStore


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentic-scaffold",
        description="AI 研发数字化基础设施：角色、流程、任务状态和质量门禁。",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="项目根目录，默认当前目录",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="创建或接入一个项目")
    init.add_argument("target", type=Path, help="目标目录")
    init.add_argument("--name", required=True, help="项目名称")
    init.add_argument("--description", default="", help="项目简介")
    init.add_argument("--stack", default="待补充", help="主要技术栈")
    init.add_argument("--language", default="zh-CN", help="文档语言，默认 zh-CN")
    init.add_argument(
        "--adopt",
        action="store_true",
        help="接入现有项目；仅创建缺失文件，不覆盖已有文件",
    )
    init.add_argument("--no-git", action="store_true", help="不初始化 Git 仓库")
    init.add_argument("--dry-run", action="store_true", help="只展示计划，不写入文件")
    init.set_defaults(handler=_handle_init)

    doctor_parser = subparsers.add_parser("doctor", help="检查项目脚手架完整性")
    doctor_parser.set_defaults(handler=_handle_doctor)

    task = subparsers.add_parser("task", help="任务生命周期管理")
    task_subparsers = task.add_subparsers(dest="task_command", required=True)

    new = task_subparsers.add_parser("new", help="创建任务")
    new.add_argument("title", help="任务标题")
    new.add_argument("--type", default="feature", choices=["feature", "bug", "spike", "chore"])
    new.add_argument("--priority", default="P1", choices=["P0", "P1", "P2", "P3"])
    new.add_argument("--owner", help="初始负责人")
    new.add_argument("--description", default="", help="初始描述")
    new.add_argument("--tag", action="append", default=[], help="标签，可重复")
    new.set_defaults(handler=_handle_task_new)

    list_parser = task_subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--state", choices=STATES)
    list_parser.add_argument("--json", action="store_true", help="输出 JSON")
    list_parser.set_defaults(handler=_handle_task_list)

    show = task_subparsers.add_parser("show", help="查看任务详情")
    show.add_argument("task_id")
    show.add_argument("--json", action="store_true", help="输出 JSON")
    show.set_defaults(handler=_handle_task_show)

    move = task_subparsers.add_parser("move", help="流转任务状态")
    move.add_argument("task_id")
    move.add_argument("state", help="目标状态")
    move.add_argument("--note", default="", help="流转说明")
    move.add_argument("--owner", help="新负责人")
    move.add_argument("--force", action="store_true", help="允许非常规状态跳转")
    move.set_defaults(handler=_handle_task_move)

    done = task_subparsers.add_parser("done", help="完成已发布任务")
    done.add_argument("task_id")
    done.add_argument("--note", default="验收完成", help="完成说明")
    done.add_argument("--force", action="store_true", help="跳过状态机校验")
    done.set_defaults(handler=_handle_task_done)

    status = task_subparsers.add_parser("status", help="查看任务统计")
    status.add_argument("--json", action="store_true", help="输出 JSON")
    status.set_defaults(handler=_handle_task_status)

    dashboard = subparsers.add_parser("dashboard", help="生成本地静态交付看板")
    dashboard.add_argument(
        "--output",
        type=Path,
        default=Path("work/dashboard.html"),
        help="输出 HTML 路径，默认 work/dashboard.html",
    )
    dashboard.set_defaults(handler=_handle_dashboard)
    return parser


def _store(args: argparse.Namespace) -> TaskStore:
    return TaskStore.from_root(args.root)


def _handle_init(args: argparse.Namespace) -> int:
    result = init_project(
        args.target,
        name=args.name,
        description=args.description,
        stack=args.stack,
        language=args.language,
        adopt=args.adopt,
        initialize_git=not args.no_git,
        dry_run=args.dry_run,
    )
    verb = "将创建" if args.dry_run else "已创建"
    print(f"项目: {result.target}")
    print(f"{verb} {len(result.created)} 个文件，跳过 {len(result.skipped)} 个已有文件。")
    for path in result.created:
        print(f"  + {path}")
    if result.git_initialized:
        print("Git: 已初始化 main 分支（尚未提交）")
    if result.skipped:
        print("已有文件已保留；请人工合并冲突，不会自动覆盖。")
    if not args.dry_run:
        print("下一步: agentic-scaffold --root . doctor")
    return 0


def _handle_doctor(args: argparse.Namespace) -> int:
    errors, warnings = doctor(args.root)
    for error in errors:
        print(f"ERROR  {error}")
    for warning in warnings:
        print(f"WARN   {warning}")
    if errors:
        print(f"\n检查失败：{len(errors)} 个错误，{len(warnings)} 个警告。")
        return 1
    print(f"检查通过：0 个错误，{len(warnings)} 个警告。")
    return 0


def _handle_task_new(args: argparse.Namespace) -> int:
    task = _store(args).create(
        args.title,
        task_type=args.type,
        priority=args.priority,
        owner=args.owner,
        description=args.description,
        tags=args.tag,
    )
    print(f"已创建 {task['id']} · {task['state']} · {task['owner']}")
    print(f"工作区: {_store(args).root / task['id']}")
    return 0


def _handle_task_list(args: argparse.Namespace) -> int:
    tasks = _store(args).list()
    if args.state:
        tasks = [task for task in tasks if task["state"] == args.state]
    if args.json:
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
        return 0
    if not tasks:
        print("暂无任务。")
        return 0
    print(f"{'ID':<20} {'状态':<12} {'负责人':<16} {'优先级':<6} 标题")
    print("-" * 92)
    for task in tasks:
        print(
            f"{task['id']:<20} {task['state']:<12} {task['owner']:<16} "
            f"{task['priority']:<6} {task['title']}"
        )
    return 0


def _handle_task_show(args: argparse.Namespace) -> int:
    task = _store(args).get(args.task_id)
    if args.json:
        print(json.dumps(task, ensure_ascii=False, indent=2))
        return 0
    print(f"{task['id']} · {task['title']}")
    print(
        f"状态={task['state']}  Owner={task['owner']}  "
        f"优先级={task['priority']}  类型={task['type']}"
    )
    if task.get("blockedReason"):
        print(f"阻塞原因={task['blockedReason']}")
    print("\n最近流转:")
    for item in task.get("history", [])[-5:]:
        change = f"{item.get('from') or '-'} → {item['to']}"
        print(f"  {item['at']}  {change}  {item.get('note', '')}".rstrip())
    print(f"\n目录: {_store(args).root / task['id']}")
    return 0


def _handle_task_move(args: argparse.Namespace) -> int:
    task = _store(args).move(
        args.task_id,
        args.state,
        note=args.note,
        owner=args.owner,
        force=args.force,
    )
    print(f"{task['id']} → {task['state']} · Owner {task['owner']}")
    return 0


def _handle_task_done(args: argparse.Namespace) -> int:
    task = _store(args).move(
        args.task_id,
        "DONE",
        note=args.note,
        owner=DEFAULT_OWNER["DONE"],
        force=args.force,
    )
    print(f"{task['id']} 已完成。")
    return 0


def _handle_task_status(args: argparse.Namespace) -> int:
    summary = _store(args).summary()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    print(
        f"任务 {summary['total']} · 进行中 {summary['active']} · "
        f"阻塞 {summary['blocked']} · 完成 {summary['done']}"
    )
    for state, count in summary["byState"].items():
        if count:
            print(f"  {state:<14} {count}")
    return 0


def _handle_dashboard(args: argparse.Namespace) -> int:
    output = args.output
    if not output.is_absolute():
        output = args.root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_store(args).render_dashboard(), encoding="utf-8")
    print(f"看板已生成: {output.resolve()}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (InitError, TaskError) as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
