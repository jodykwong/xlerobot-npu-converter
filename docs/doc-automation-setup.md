# 文档自动化工具设置指南

**创建日期**: 2025-10-27
**版本**: v1.0.0

---

## 📋 概述

本文档说明如何设置和使用XLeRobot项目的文档自动化工具，包括文档同步、审计和GitHub Actions工作流。

---

## 🛠️ 已创建的自动化工具

### 1. 文档同步脚本
- **文件**: `scripts/sync_docs.py`
- **功能**: 自动同步README与BMM工作流状态
- **使用方式**:
  ```bash
  # 检查文档同步状态
  python scripts/sync_docs.py --check-only

  # 自动同步文档
  python scripts/sync_docs.py --sync

  # 生成同步报告
  python scripts/sync_docs.py --report
  ```

### 2. 文档质量审计脚本
- **文件**: `scripts/doc_audit.py`
- **功能**: 检查文档完整性、链接有效性、一致性等
- **使用方式**:
  ```bash
  # 快速检查
  python scripts/doc_audit.py --quick --report

  # 完整审计
  python scripts/doc_audit.py --full --report

  # 保存报告
  python scripts/doc_audit.py --full --save audit_report.md
  ```

### 3. GitHub Actions工作流
- **文件**: `.github/workflows/doc-consistency-check.yml`
- **功能**: 自动检查文档一致性和质量
- **触发条件**:
  - 推送到main/master分支时
  - 创建Pull Request时
  - 每周一早上8点定时检查
  - 手动触发

### 4. Pre-commit钩子
- **文件**: `.pre-commit-config.yaml`
- **功能**: 在本地提交前自动检查文档
- **安装方式**:
  ```bash
  # 安装pre-commit (需要git仓库)
  pip install pre-commit

  # 安装钩子
  pre-commit install

  # 运行所有钩子
  pre-commit run --all-files

  # 只运行文档检查
  pre-commit run doc-sync-check --all-files
  pre-commit run doc-audit-check --all-files
  ```

---

## 🚀 快速开始

### 验证工具

1. **运行文档同步检查**
   ```bash
   python scripts/sync_docs.py --check-only
   ```

2. **运行快速审计**
   ```bash
   python scripts/doc_audit.py --quick --report
   ```

3. **生成完整报告**
   ```bash
   python scripts/doc_audit.py --full --save full_audit.md
   ```

### 设置GitHub Actions

GitHub Actions工作流文件已经创建在 `.github/workflows/doc-consistency-check.yml`。

**如何启用**:
1. 将代码推送到GitHub仓库
2. 在GitHub仓库设置中启用Actions
3. 工作流会自动在以下情况触发:
   - 推送文档相关文件时
   - 每周一自动检查
   - 手动触发

**查看工作流结果**:
- 进入GitHub仓库页面
- 点击 "Actions" 标签
- 查看最新的工作流运行记录

### 设置Pre-commit (可选)

如果需要在本地git仓库中设置pre-commit钩子:

```bash
# 确保在git仓库中
git init
git add .
git commit -m "Initial commit"

# 安装pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 运行钩子
pre-commit run --all-files
```

---

## 📊 审计结果示例

### 首次运行结果

```
🔍 开始文档质量审计...
  检查 完整性...
    ✅ PASS (得分: 100.00%)
  检查 链接有效性...
    ❌ FAIL (得分: 46.97%)
  检查 一致性...
    ❌ FAIL (得分: 90.00%)
  检查 格式规范...
    ✅ PASS (得分: 100.00%)
  检查 代码示例...
    ❌ FAIL (得分: 42.73%)

============================================================
📊 审计总结
============================================================
总体状态: ❌ 未通过
总体得分: 75.94%
检查项目: 5
发现问题: 253
```

**发现的问题类型**:
- 断链 (35个)
- 格式问题 (20个)
- 代码示例问题 (197个)
- 一致性问题 (1个)

### 常见问题修复

#### 1. 断链问题
```bash
# 检查哪些链接断了
python scripts/doc_audit.py --quick | grep "断链"

# 修复方法:
# - 更新链接路径
# - 创建缺失的文档
# - 删除无效链接
```

#### 2. 格式问题
```bash
# 检查格式问题
python scripts/doc_audit.py --full | grep "格式"

# 修复方法:
# - 添加代码块语言标识 (```bash, ```python等)
# - 修正表格格式
# - 检查Markdown语法
```

#### 3. 一致性问题
```bash
# 同步文档状态
python scripts/sync_docs.py --sync

# 验证同步
python scripts/sync_docs.py --check-only
```

---

## 📈 最佳实践

### 日常开发

1. **提交PR前**
   ```bash
   # 运行快速检查
   python scripts/doc_audit.py --quick

   # 同步文档状态
   python scripts/sync_docs.py --check-only
   ```

2. **每周审查**
   ```bash
   # 运行完整审计
   python scripts/doc_audit.py --full --report

   # 生成报告并保存
   python scripts/doc_audit.py --full --save weekly_audit_$(date +%Y%m%d).md
   ```

3. **发布前检查**
   ```bash
   # 全面检查
   python scripts/doc_audit.py --full

   # 验证所有链接
   # (需要人工检查，因为有些链接可能指向外部资源)
   ```

### 文档编写

1. **新文档创建后**
   - 更新 `REQUIRED_DOCS` 列表 (在 `scripts/doc_audit.py` 中)
   - 确保在README中有交叉引用
   - 验证链接有效

2. **更新现有文档后**
   - 检查是否需要更新README
   - 验证交叉引用
   - 运行快速审计

3. **代码变更后**
   - 更新相关文档
   - 同步文档状态
   - 运行文档同步脚本

---

## 🔧 故障排除

### 问题1: 脚本无法运行

**症状**:
```bash
python scripts/sync_docs.py
# 报错: ModuleNotFoundError: No module named 'yaml'
```

**解决方案**:
```bash
pip install PyYAML
```

### 问题2: GitHub Actions失败

**症状**:
- Actions页面显示红色❌
- 工作流运行失败

**解决方案**:
1. 点击失败的workflow查看日志
2. 常见错误:
   - 脚本路径错误 → 检查 `.github/workflows/doc-consistency-check.yml`
   - 依赖缺失 → 在工作流中添加安装步骤
   - 权限问题 → 检查仓库设置中的Actions权限

### 问题3: Pre-commit钩子失败

**症状**:
```bash
git commit -m "Update docs"
# pre-commit hook failed
```

**解决方案**:
```bash
# 跳过钩子 (不推荐)
git commit -m "Update docs" --no-verify

# 修复问题后重新提交
pre-commit run --all-files
git add .
git commit -m "Update docs"
```

### 问题4: 审计报告不准确

**症状**:
- 显示断链但链接实际存在
- 格式问题误报

**解决方案**:
- 检查脚本中的路径解析逻辑
- 验证文件权限
- 确认脚本与文件版本匹配

---

## 📝 维护计划

### 每日
- ✅ GitHub Actions自动检查

### 每周
- [ ] 运行 `python scripts/doc_audit.py --quick --report`
- [ ] 检查CI结果
- [ ] 修复发现的问题

### 每月
- [ ] 运行 `python scripts/doc_audit.py --full --report`
- [ ] 生成月度审计报告
- [ ] 更新文档维护统计

### 每季度
- [ ] 审查文档体系
- [ ] 更新自动化工具
- [ ] 优化工作流

---

## 📞 支持

### 获取帮助

1. **查看文档**
   - `docs/doc-review-checklist.md` - 文档审查清单
   - `docs/doc-quality-audit-schedule.md` - 审计机制文档

2. **查看脚本帮助**
   ```bash
   python scripts/sync_docs.py --help
   python scripts/doc_audit.py --help
   ```

3. **查看GitHub Actions日志**
   - 进入仓库Actions页面
   - 点击失败的workflow查看详情

### 问题反馈

- **GitHub Issues**: 使用 "documentation" 标签
- **邮件**: 联系文档管理员
- **Slack**: #docs-team (如果有)

---

## 📋 检查清单

### 设置完成后验证

- [ ] `python scripts/sync_docs.py --check-only` 运行成功
- [ ] `python scripts/doc_audit.py --quick` 运行成功
- [ ] `.github/workflows/doc-consistency-check.yml` 文件存在
- [ ] `.pre-commit-config.yaml` 配置正确

### 日常使用验证

- [ ] PR提交后CI自动运行文档检查
- [ ] 能够生成审计报告
- [ ] 能够修复发现的问题
- [ ] 团队成员了解如何使用工具

---

**最后更新**: 2025-10-27
**维护者**: 文档管理团队
**版本**: v1.0.0

*此文档将根据实际使用情况持续更新*
