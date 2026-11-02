# AI 研发协作入口

本文件是所有 AI 编程工具进入本项目的统一入口。执行任何非平凡任务前，按顺序读取：

1. 本文件。
2. [`agents/shared/PRINCIPLES.md`](agents/shared/PRINCIPLES.md)。
3. [`agents/ORCHESTRATION.md`](agents/ORCHESTRATION.md)。
4. [`context/project/OVERVIEW.md`](context/project/OVERVIEW.md)。
5. 与任务相关的 `context/architecture/`、`context/standards/`、`context/decisions/`。
6. 任务对应的角色手册 `agents/roles/{role}.md`。

不要一次性加载整个 `context/`。先根据任务边界选择最少但充分的资料。

## 默认工作方式

1. 先确认问题、目标、非目标、约束和验收条件。
2. 创建或选择一个 `TASK-*`，通过 CLI 流转状态，不手工改写 `task.json`。
3. 在每阶段开始时读取对应交付模板，在结束前写入事实、证据和未决风险。
4. 代码修改后执行最接近变更风险的自动化验证。
5. Reviewer 与 QA 各自独立判断，不用开发者自评替代评审与验证。
6. 发布前确认回滚方案和观测项。
7. 只把经过验证、可复用的经验沉淀到 `context/`。

## 不可违反的规则

- 结论必须建立在已读取的代码、文档或可复现实验之上；未知信息标记为“待确认”。
- 不虚构测试结果、命令输出、性能数据、外部事实或用户需求。
- 不把密钥、Token、Cookie、个人路径、客户数据写入受 Git 管理的文件。
- 不绕过会导致代码或数据难以恢复的破坏性操作；执行前确认精确目标。
- 已有用户修改必须保留；不要为了“整洁”撤销无关变更。
- 状态流转表示事实已发生。没有实际评审或验证，就不能把任务移动到对应阶段。
- 紧急流程可以缩减阶段，但必须在任务日志记录为什么缩减、风险是什么、谁批准。

## 常用命令

```bash
agentic-scaffold doctor
agentic-scaffold task new "任务标题" --priority P1
agentic-scaffold task list
agentic-scaffold task show TASK-YYYYMMDD-NNN
agentic-scaffold task move TASK-YYYYMMDD-NNN DISCOVERY --note "开始澄清"
agentic-scaffold task status
agentic-scaffold dashboard
```

## 阶段与 Owner

| 状态 | Owner | 交付物 |
| --- | --- | --- |
| `INTAKE` | orchestrator | `brief.md` 初始问题 |
| `DISCOVERY` | product | 需求、范围、验收、未知项 |
| `DESIGN` | architect | 方案、权衡、风险、测试策略 |
| `IMPLEMENTATION` | developer | 代码、测试、自测记录 |
| `REVIEW` | reviewer | 独立代码与风险评审 |
| `VERIFICATION` | qa | 自动化、人工验证与缺陷记录 |
| `RELEASE` | release | 发布、回滚、观测计划 |
| `DONE` | orchestrator | 最终交付摘要 |

任务工作流详见 [`workflows/delivery.md`](workflows/delivery.md)。
