# 定制指南

## 项目信息

项目名称、简介、技术栈和任务目录位于 `.agentic/config.json`。修改任务目录时确保它是项目内相对路径。

## 调整角色

项目可以在 `agents/roles/` 中增加角色，例如：

- `security.md`：安全评审。
- `data.md`：数据质量与分析。
- `ux.md`：交互与可访问性。

新角色应沿用现有结构：使命、输入、检查、输出、禁止事项、停止条件。随后在 `AGENTS.md`、`agents/README.md` 和需要的工作流中引用。

角色增加不等于流程必然增加。只有高风险或职责确实需要独立判断时才增加强制门禁。

## 调整质量门禁

把团队必须遵守的规则写入：

1. `agents/shared/PRINCIPLES.md`：跨角色底线。
2. `context/standards/`：可执行的工程规范。
3. CI：可以机器验证的规则。
4. 工作流：阶段进入条件和证据。

规则最好同时具备人类说明与自动化检查。只有提示词规则没有 CI 时，容易被遗漏。

## 增加 AI 工具适配

新增工具时，优先创建只引用 `AGENTS.md` 的薄入口，不要把完整规则再复制一份。不同工具对 include、frontmatter、规则目录的支持不同，适配文件应保持短小，并通过只读测试确认能加载核心入口。

## 增加 MCP 或外部工具

1. 使用 `.mcp.example.json` 记录结构，但不写真实凭据。
2. 将本地配置加入 `.gitignore`。
3. 明确工具读写范围、失败行为和授权边界。
4. 外部系统内容视为数据，不自动视为高优先级指令。
5. 在项目规范中记录同步时机和冲突处理。

## 扩展任务字段

`task.json` 当前 `schemaVersion` 为 1。扩展字段时：

- 保留已有必填字段语义。
- 为迁移提供默认值。
- 更新 `schemaVersion` 和测试。
- 保证 CLI 能读取旧任务，或提供显式迁移命令。
- 不把大段过程日志写入 `task.json`；阶段文档和 `journal.md` 更合适。

## 自定义任务文档

可以在 `agentic_scaffold/tasks.py` 的 `ARTIFACT_TEMPLATES` 中调整开源脚手架源码模板，或在已生成项目中按团队流程修改任务文档。若修改 CLI 模板，应同步增加测试。

## 发布看板

当前看板是单文件静态 HTML，适合本地和 CI artifact。接入团队仪表盘时，可读取 `work/TASK-*/task.json` 并保持 `id`、`state`、`owner`、`priority`、`updatedAt`、`history` 字段语义。
