# Agentic Scaffold

> AI 研发数字化基础设施：让 AI 在明确角色、统一上下文、可追踪流程和可验证门禁中参与软件交付。

## 项目定位

- **主要用户**：希望把 AI 安全、稳定地引入研发流程的软件团队。
- **核心问题**：AI 协作中的上下文断层、角色混淆、过程不可见和结果不可验证。
- **主要技术栈**：Python 3.10+（核心 CLI 零第三方运行时依赖）。
- **当前阶段**：`0.1.0` Alpha，适合内部试点和团队基线定制。

## 系统边界

| 能力 | 所在模块 | 对外接口 | Owner |
| --- | --- | --- | --- |
| 角色协作协议 | `agents/`、`AGENTS.md` | Markdown 上下文 | Maintainers |
| 项目接入 | `agentic_scaffold/project.py`、`templates/` | `agentic-scaffold init`、`doctor` | Maintainers |
| 任务生命周期 | `agentic_scaffold/tasks.py` | `agentic-scaffold task` | Maintainers |
| 交付可视化 | `TaskStore.render_dashboard()` | `agentic-scaffold dashboard` | Maintainers |
| 多工具适配 | `CLAUDE.md`、`.cursor/`、`.github/` | 薄入口文件 | Maintainers |

## 关键数据

只记录数据类别、权威来源和生命周期，不在本文件复制敏感数据。

| 数据 | 权威来源 | 使用方 | 保留策略 |
| --- | --- | --- | --- |
| 项目配置 | `.agentic/config.json` | CLI、AI 工具 | 随项目版本管理 |
| 任务状态 | `work/TASK-*/task.json` | CLI、看板 | 默认仅本地保留 |
| 阶段证据 | `work/TASK-*/[brief/design/...].md` | 协作角色、审计 | 按团队策略归档 |
| 长期知识 | `context/` | 所有角色 | Git 版本管理 |
| 开源基线 | `agentic_scaffold/templates/project/` | `init` 命令 | 随发布版本管理 |

## 运行与部署

- 本地运行：`python3 -m agentic_scaffold --help` 或安装后执行 `agentic-scaffold --help`。
- 测试：`python3 -m unittest discover -s tests -v`。
- 发版环境：通过 `pyproject.toml` 构建 Python 包。
- CI：GitHub Actions 覆盖 Python 3.10、3.11、3.12。
- 关键依赖：运行期仅使用 Python 标准库；构建依赖为 setuptools。

## 当前风险

- `0.1` 阶段接口可能变化，需要保持任务 schema 与配置的向后兼容。
- 任务过程数据包含本地环境信息，接入项目必须遵守默认的忽略策略。
- 角色门禁是流程约束，仍需要 CI 与人工评审验证真实质量。

## 文档索引

- 架构：`context/architecture/README.md`
- 工程规范：`context/standards/README.md`
- 架构决策：`context/decisions/README.md`
- 术语表：`context/project/GLOSSARY.md`
