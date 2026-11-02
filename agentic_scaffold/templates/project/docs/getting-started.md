# 快速开始

## 前置条件

- Python 3.10 或更高版本。
- Git。
- 一个支持读取 `AGENTS.md` 的 AI 编程工具，或愿意手动使用 `commands/` 提示词。

## 安装

在 Agentic Scaffold 源码目录运行：

```bash
python3 -m pip install -e .
agentic-scaffold --version
```

如果希望命令独立于项目虚拟环境，可以使用：

```bash
pipx install -e .
```

## 创建新项目

```bash
agentic-scaffold init ../my-project \
  --name "My Project" \
  --description "项目简介" \
  --stack "Python, PostgreSQL, React"
cd ../my-project
agentic-scaffold doctor
```

默认会初始化 `main` 分支 Git 仓库，但不会创建 commit。

## 接入现有项目

```bash
cd my-existing-project
agentic-scaffold init . \
  --name "My Existing Project" \
  --description "项目简介" \
  --stack "现有技术栈" \
  --adopt
```

`--adopt` 安全策略：

- 只创建缺失文件。
- 不覆盖已有 `README.md`、`AGENTS.md`、`.gitignore` 等文件。
- 不自动初始化 Git。
- 命令会输出已跳过文件，需人工合并。

先预览将创建的内容：

```bash
agentic-scaffold init . --name "My Project" --adopt --dry-run
```

## 第一次编辑

打开 `context/project/OVERVIEW.md`，补齐：

1. 项目面向谁、解决什么问题。
2. 系统边界、关键数据、环境和依赖。
3. 当前风险与文档索引。

然后按需补充 `context/architecture/` 与 `context/standards/`。不要一开始写满所有模板，只填与当前任务有关且已经验证的信息。

## 创建第一个任务

```bash
agentic-scaffold task new "实现一个可验收的小功能" \
  --type feature \
  --priority P1 \
  --description "描述问题和期望结果"
```

命令会输出任务 ID，例如 `TASK-20261103-001`。查看任务：

```bash
agentic-scaffold task list
agentic-scaffold task show TASK-20261103-001
```

任务目录：

```text
work/TASK-20261103-001/
├── task.json
├── brief.md
├── plan.md
└── journal.md
```

推进到需求澄清：

```bash
agentic-scaffold task move TASK-20261103-001 DISCOVERY \
  --note "开始澄清范围和验收条件"
```

在 AI 工具中输入：

```text
读取 AGENTS.md 和 commands/deliver.md，继续推进 TASK-20261103-001。
```

## 状态查询与看板

```bash
agentic-scaffold task status
agentic-scaffold dashboard
```

`dashboard` 默认写入 `work/dashboard.html`，可直接用浏览器打开。

## 常见问题

### 任务文件是否应提交到 Git

默认不提交。`work/` 是过程证据，长期知识应经过验证和提炼后写入 `context/`。

### 一个 Agent 能否扮演多个角色

可以。但每次角色切换都应重新读取对应检查清单，并明确本角色独立输出了什么证据。

### 是否必须使用所有阶段

不一定。Bug、预研和紧急修复可以缩减阶段；涉及高风险变更时不得省略设计、评审和验证。

### 如何接入内部项目管理系统

把 MCP 或其他集成写入本地未跟踪配置，并在 `.mcp.example.json` 中记录无密钥示例。同步时遵守项目权限和数据保护规则。
