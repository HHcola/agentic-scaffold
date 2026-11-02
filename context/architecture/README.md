# 架构知识

本目录保存项目的稳定架构事实，而不是任务流水。

建议按系统或主题拆分：

```text
context/architecture/
├── README.md
├── system-context.md
├── backend.md
├── frontend.md
├── data.md
└── observability.md
```

每份文档至少包含：

- 范围与读者。
- 关键组件和职责。
- 数据流与调用关系。
- 外部依赖和失败边界。
- 关键约束、容量与安全考虑。
- 权威代码位置和最后确认时间。

架构变化时，更新事实文档；重要选择另写 ADR 到 `context/decisions/`。
