# 标准功能交付

## 适用场景

新功能、明确行为变更、跨模块改动。

## 1. Intake

创建任务，写清问题、目标和初始约束。

**证据**：任务已创建；`brief.md` 有初始描述。

## 2. Discovery

Product 补全用户场景、范围、非目标、验收条件和待确认项。

**门禁**：验收条件可观察；关键业务规则没有未确认的占位假设。

```bash
agentic-scaffold task move TASK-YYYYMMDD-NNN DISCOVERY --note "开始需求澄清"
```

## 3. Design

Architect 阅读真实代码和架构，记录方案、备选方案、权衡、风险、测试策略与回滚边界。

**门禁**：实现路径和风险可被独立评审；重要决策有记录。

## 4. Implementation

Developer 实现代码与测试，运行相关检查，把命令、结果和残余风险写入 `implementation.md`。

**门禁**：变更范围明确；相关自动化检查有真实结果。

## 5. Review

Reviewer 基于实际 diff 独立检查正确性、安全、可维护性和证据。发现问题则回流实现。

**门禁**：无未解决阻断项。

## 6. Verification

QA 在明确环境中检查验收条件、边界、回归和权限。记录可复现证据。

**门禁**：验收项逐条通过；无阻断/严重缺陷；残余风险被接收。

## 7. Release

Release 执行或记录发布、健康检查、观测和回滚方案。

**门禁**：发布与回滚可执行；关键指标可观测。

## 8. Done

Orchestrator 汇总交付、证据、残余风险、后续项，并提炼长期知识。

```bash
agentic-scaffold task done TASK-YYYYMMDD-NNN --note "验收和发布完成"
```
