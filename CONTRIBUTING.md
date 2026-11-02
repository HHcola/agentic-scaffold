# 贡献指南

感谢参与 Agentic Scaffold。

## 开始前

- 搜索现有 issue 和 PR，避免重复工作。
- 大功能或流程变更先开 issue 对齐目标。
- 安全问题不要公开提交，按 [SECURITY.md](SECURITY.md) 报告。

## 本地开发

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
```

## 提交要求

- 聚焦一个问题，保留可审查的 diff。
- 新行为包含测试，文档变化同步更新。
- 不降低已有测试强度来获得通过。
- 不提交秘密、内部地址、客户数据或本地任务目录。
- Commit message 建议使用 Conventional Commits，例如：

```text
feat(cli): add task dashboard command
fix(templates): keep existing files during adoption
docs: clarify review gate
```

## Pull Request

PR 应说明：

1. 解决什么问题。
2. 做了什么，以及为何这样取舍。
3. 如何验证。
4. 风险和兼容性影响。
5. 关联 issue。

维护者会检查正确性、测试、安全、文档和向后兼容性。
