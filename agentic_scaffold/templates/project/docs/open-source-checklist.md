# 开源发布检查清单

## 敏感信息

- [ ] 搜索并移除 Token、Cookie、密码、私钥和内部 API。
- [ ] 检查 Git 历史，而不只是当前工作树。
- [ ] 检查示例数据、截图、日志和测试 fixture。
- [ ] 确认作者邮箱、内部主机名和本地绝对路径是否可以公开。
- [ ] 真实环境配置只保留占位符；`.mcp.json`、`.env*` 已被忽略。

可用基础检查：

```bash
git grep -nEI '(token|secret|password|cookie|authorization)[[:space:]]*[:=]' || true
git grep -nE '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|https?://[^ ]+\.internal)' || true
```

这些规则不能保证发现所有问题，人工复核仍是必要步骤。

## 法律与治理

- [ ] 确认 LICENSE 符合组织要求，并更新版权主体。
- [ ] 审查第三方代码、字体、图片、数据集和依赖许可证。
- [ ] 提供 `CONTRIBUTING.md`、`CODE_OF_CONDUCT.md` 和 `SECURITY.md`。
- [ ] 明确项目支持范围、版本策略和维护者责任。
- [ ] 删除客户名称、内部业务规则和未获授权的参考实现。

## 仓库质量

- [ ] `README.md` 能让新用户完成首次运行。
- [ ] 安装、初始化、升级和验证命令都已实际执行。
- [ ] 测试在干净环境通过。
- [ ] CI 在目标 Python 版本运行。
- [ ] Issue、PR 模板可用。
- [ ] CHANGELOG 与版本号一致。
- [ ] GitHub 仓库 URL、维护者和联系渠道已替换占位符。

## 发布后

- [ ] 启用分支保护、Secret scanning 和依赖提醒。
- [ ] 创建首个 Release 和版本标签。
- [ ] 检查 GitHub Actions 权限遵循最小权限。
- [ ] 建立安全问题私下报告渠道。
- [ ] 制定 issue 分流和 PR 评审责任。
