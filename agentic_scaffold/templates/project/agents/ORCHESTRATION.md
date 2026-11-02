# 编排协议

编排器负责把模糊输入变成可执行、可验证、可追踪的任务，并确保每个角色只在职责边界内作判断。

## 1. 任务分级

| 类型 | 适用场景 | 默认路径 |
| --- | --- | --- |
| `feature` | 新能力、行为变更 | DISCOVERY → DESIGN → IMPLEMENTATION → REVIEW → VERIFICATION → RELEASE |
| `bug` | 已存在行为与预期不符 | DISCOVERY → IMPLEMENTATION → REVIEW → VERIFICATION → RELEASE |
| `spike` | 技术可行性、方案验证 | DISCOVERY → DESIGN → DONE |
| `chore` | 构建、文档、依赖、清理 | DESIGN（如需要）→ IMPLEMENTATION → REVIEW → VERIFICATION |

路径是最小建议，不替代风险判断。涉及权限、数据迁移、支付、隐私、核心链路或不可逆操作时，不能省略 DESIGN、REVIEW 或 VERIFICATION。

## 2. 接收任务时

先回答以下问题，能基于代码和文档确认的直接确认，不能确认的列成不超过 3 个关键问题：

1. 谁遇到什么问题，期望的可观察结果是什么？
2. 哪些范围明确不做？
3. 哪些系统、数据、权限或外部依赖会受影响？
4. 失败时最坏会发生什么，是否可恢复？
5. 用什么证据证明完成？

任务可以开始时立即创建：

```bash
agentic-scaffold task new "任务标题" \
  --type feature \
  --priority P1 \
  --description "问题、目标和非目标"
```

## 3. 角色交接契约

每次交接都包含五部分：

```text
目标：这次交接要让下游完成什么
事实：已验证的上下文与引用
决策：已做出的选择及理由
约束：不能做什么、必须兼容什么
期望：下游应产出什么证据
```

交接前更新任务状态：

```bash
agentic-scaffold task move TASK-YYYYMMDD-NNN REVIEW \
  --note "实现与自测完成；变更范围见 implementation.md"
```

不要只把结论放在聊天消息里。任务目录中的阶段文档是可审计交付面。

## 4. 独立判断

- Product 不能替用户虚构业务规则。
- Architect 不能把未验证的假设写成系统事实。
- Developer 不能用“代码已写完”替代测试。
- Reviewer 不能只复述开发者摘要，必须检查实际差异。
- QA 不能引用未实际执行的命令结果。
- Release 不能在缺少回滚路径时宣布可发布。

角色可以由同一个 Agent 依次扮演，但每次切换时必须重新读取该角色的检查清单，并把前一角色的假设作为“待验证”输入。

## 5. 返工与阻塞

- Review 发现阻断问题时进入 `IMPLEMENTATION`。
- QA 发现行为不符合时进入 `IMPLEMENTATION`。
- 发布异常退回 `VERIFICATION`，必要时回滚并创建修复任务。
- 缺少外部权限、关键决策或不可用环境时进入 `BLOCKED`，在 `--note` 中写清解除条件和责任人。

```bash
agentic-scaffold task move TASK-YYYYMMDD-NNN BLOCKED \
  --note "等待安全团队确认日志脱敏范围；Owner: @security-lead"
```

## 6. 完成标准

任务进入 `DONE` 前必须满足：

- [ ] 验收条件逐条有证据。
- [ ] 必须执行的自动化检查通过，或明确记录不可执行原因和残余风险。
- [ ] Reviewer 无未解决阻断项。
- [ ] QA 的验证范围与环境可追溯。
- [ ] 发布步骤、回滚步骤和关键观测项已记录。
- [ ] 影响项目长期认知的结论已提炼到 `context/`。
- [ ] 没有把敏感信息或本地运行产物加入 Git。

## 7. 多 Agent 协作

可以并行时，优先按**无共享写目标**拆分；并行角色之间必须交换输入和输出路径。多个角色共享工作区时：

1. 明确每个角色的文件所有权。
2. 不互相格式化或重写对方文件。
3. 集成前重新读取最新文件。
4. 由编排器负责最终冲突检测与状态推进。

并行提升速度，但不能牺牲独立评审。实现者和评审者同时开始、共享同一假设时，应增加一次交叉检查或等待实现基线稳定。
