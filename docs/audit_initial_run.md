# 文档质量审计报告

**生成时间**: 2025-10-27 18:52:41
**审计范围**: 完整文档库
**总体状态**: ❌ FAIL
**总体得分**: 75.94%

---

## 📊 审计结果概览

| 检查项目 | 状态 | 得分 | 问题数 |
|----------|------|------|--------|
| Completeness | ✅ PASS | 100.00% | 0 |
| Link Validity | ❌ FAIL | 46.97% | 35 |
| Consistency | ❌ FAIL | 90.00% | 1 |
| Format Compliance | ✅ PASS | 100.00% | 20 |
| Code Examples | ❌ FAIL | 42.73% | 197 |

---

## 📈 指标统计

- **文档总数**: 399
- **文档总大小**: 2.93 MB
- **最近更新**: 399 文档 (7天内)
- **平均文档大小**: 0.01 KB

---

## ❌ 发现的问题

**Link Validity** (35 个问题)
- 断链: LICENSE
- 断链 docs/architecture-issue-report.md: stories/story-1.3.md
- 断链 docs/architecture-issue-report.md: stories/story-1.4.md
- 断链 docs/architecture-issue-report.md: stories/story-2.1.2.md
- 断链 docs/architecture-issue-report.md: bmm-workflow-status.md
- 断链 docs/README.md: ./bmm-workflow-status.md
- 断链 docs/README.md: ./project-progress-overview.md
- 断链 docs/README.md: ./bmm-product-brief-XLeRobot%20NPU模型转换工具-2025-10-25.md
- 断链 docs/README.md: ../bmad/bmm/workflows/workflow-status/
- 断链 docs/README.md: ../bmad/bmm/workflows/workflow-status/paths/

**Consistency** (1 个问题)
- README中的Epic 1状态与BMM工作流状态不一致

**Format Compliance** (20 个问题)
- 代码块缺少语言标识: README.md
- 表格格式可能有问题: README.md
- 代码块缺少语言标识: docs/architecture-issue-report.md
- 表格格式可能有问题: docs/architecture-issue-report.md
- 代码块缺少语言标识: docs/README.md
- 表格格式可能有问题: docs/README.md
- 代码块缺少语言标识: docs/architecture.md
- 表格格式可能有问题: docs/architecture.md
- 表格格式可能有问题: docs/update-verification-report.md
- 代码块缺少语言标识: docs/doc-quality-audit-schedule.md

**Code Examples** (197 个问题)
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: docs/architecture.md


## 💡 改进建议

- 修复断链
- 添加链接检查到CI
- 同步文档状态
- 使用自动同步脚本
- 修正格式问题
- 添加格式检查到pre-commit
- 修正无效代码示例
- 添加示例测试

---

## 📋 详细结果

### Completeness

**状态**: PASS
**得分**: 100.00%

**指标**:
- total_required: 9
- missing: 0

### Link Validity

**状态**: FAIL
**得分**: 46.97%

**指标**:
- total_links: 66
- broken_links: 35

**问题**:
- 断链: LICENSE
- 断链 docs/architecture-issue-report.md: stories/story-1.3.md
- 断链 docs/architecture-issue-report.md: stories/story-1.4.md
- 断链 docs/architecture-issue-report.md: stories/story-2.1.2.md
- 断链 docs/architecture-issue-report.md: bmm-workflow-status.md
- 断链 docs/README.md: ./bmm-workflow-status.md
- 断链 docs/README.md: ./project-progress-overview.md
- 断链 docs/README.md: ./bmm-product-brief-XLeRobot%20NPU模型转换工具-2025-10-25.md
- 断链 docs/README.md: ../bmad/bmm/workflows/workflow-status/
- 断链 docs/README.md: ../bmad/bmm/workflows/workflow-status/paths/
- 断链 docs/README.md: ../yahboom_ws/EMERGENCY_RECOVERY.md
- 断链 docs/README.md: ../yahboom_ws/docs/architecture.md
- 断链 docs/README.md: ../bmad/bmm/config.yaml
- 断链 docs/README.md: ../.claude/commands/bmad/bmm/agents/
- 断链 docs/README.md: ../bmad/bmm/workflows/1-analysis/product-brief/template.md
- 断链 docs/README.md: ../bmad/bmm/workflows/2-planning/prd/template.md
- 断链 docs/README.md: ./bmm-product-brief-XLeRobot%20NPU模型转换工具-2025-10-25.md
- 断链 docs/README.md: ./bmm-product-brief-XLeRobot%20NPU模型转换工具-2025-10-25.md
- 断链 docs/README.md: ../bmad/core/
- 断链 docs/README.md: ../bmad/bmm/workflows/
- 断链 docs/configuration-management-guide.md: architecture-story-1.4.md
- 断链 docs/configuration-management-guide.md: api-reference.md
- 断链 docs/configuration-management-guide.md: troubleshooting.md
- 断链 docs/configuration-management-guide.md: best-practices.md
- 断链 docs/PRD.md: ./epics.md
- 断链 docs/epics.md: ./PRD.md
- 断链 docs/cli-usage-guide.md: configuration-management-guide.md
- 断链 docs/cli-usage-guide.md: api-reference.md
- 断链 docs/cli-usage-guide.md: architecture-story-1.4.md
- 断链 docs/stories/story-1.5.md: story-context-1.5.xml
- 断链 docs/stories/story-1.6.md: story-context-1.6.xml
- 断链 docs/stories/story-1.2.md: story-context-1.2.xml
- 断链 docs/examples/README.md: ../configuration-management-guide.md
- 断链 docs/examples/README.md: ../api-reference.md
- 断链 docs/examples/README.md: ../architecture-story-1.4.md

### Consistency

**状态**: FAIL
**得分**: 90.00%

**指标**:
- issues_count: 1

**问题**:
- README中的Epic 1状态与BMM工作流状态不一致

### Format Compliance

**状态**: PASS
**得分**: 100.00%

**指标**:
- total_docs: 399
- compliant_docs: 399

**问题**:
- 代码块缺少语言标识: README.md
- 表格格式可能有问题: README.md
- 代码块缺少语言标识: docs/architecture-issue-report.md
- 表格格式可能有问题: docs/architecture-issue-report.md
- 代码块缺少语言标识: docs/README.md
- 表格格式可能有问题: docs/README.md
- 代码块缺少语言标识: docs/architecture.md
- 表格格式可能有问题: docs/architecture.md
- 表格格式可能有问题: docs/update-verification-report.md
- 代码块缺少语言标识: docs/doc-quality-audit-schedule.md
- 表格格式可能有问题: docs/doc-quality-audit-schedule.md
- 代码块缺少语言标识: docs/project-status-summary.md
- 表格格式可能有问题: docs/project-status-summary.md
- 代码块缺少语言标识: docs/production-deployment-guide.md
- 表格格式可能有问题: docs/production-deployment-guide.md
- 代码块缺少语言标识: docs/docker-usage.md
- 代码块缺少语言标识: docs/advanced-configuration-examples.md
- 代码块缺少语言标识: docs/api-reference.md
- 代码块缺少语言标识: docs/docs_audit_report_2025-10-27.md
- 代码块缺少语言标识: docs/docker-validation-summary.md

### Code Examples

**状态**: FAIL
**得分**: 42.73%

**指标**:
- total_examples: 344
- valid_examples: 147

**问题**:
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: README.md
- Bash示例可能有问题: docs/architecture.md
- Python示例可能有问题: docs/architecture.md
- Python示例可能有问题: docs/architecture.md
- Python示例可能有问题: docs/architecture.md
- Bash示例可能有问题: docs/doc-quality-audit-schedule.md
- Bash示例可能有问题: docs/doc-quality-audit-schedule.md
- Bash示例可能有问题: docs/doc-quality-audit-schedule.md
- Bash示例可能有问题: docs/doc-quality-audit-schedule.md
- Bash示例可能有问题: docs/doc-quality-audit-schedule.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/production-deployment-guide.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-usage.md
- Bash示例可能有问题: docs/docker-validation-summary.md
- Bash示例可能有问题: docs/docker-validation-summary.md
- Bash示例可能有问题: docs/docker-validation-summary.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/cli-usage-examples.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/coverage_monitoring.md
- Bash示例可能有问题: docs/doc-review-checklist.md
- Bash示例可能有问题: docs/doc-review-checklist.md
- Bash示例可能有问题: docs/doc-review-checklist.md
- Python示例可能有问题: docs/architecture-story-1.4.md
- Python示例可能有问题: docs/architecture-story-1.4.md
- Python示例可能有问题: docs/architecture-story-1.4.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: docs/cli-usage-guide.md
- Bash示例可能有问题: bmad/bmb/README.md
- Bash示例可能有问题: bmad/cis/readme.md
- Bash示例可能有问题: bmad/bmm/README.md
- Bash示例可能有问题: bmad/bmm/workflows/README.md
- Bash示例可能有问题: bmad/bmm/workflows/4-implementation/story-context/README.md
- Bash示例可能有问题: bmad/bmm/workflows/4-implementation/retrospective/README.md
- Bash示例可能有问题: bmad/bmm/workflows/4-implementation/create-story/README.md
- Bash示例可能有问题: bmad/bmm/workflows/4-implementation/dev-story/README.md
- Bash示例可能有问题: bmad/bmm/workflows/4-implementation/correct-course/README.md
- Bash示例可能有问题: bmad/bmm/workflows/4-implementation/epic-tech-context/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/trace/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/trace/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/trace/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/trace/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/test-review/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/test-review/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/test-review/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/ci/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/ci/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/ci/instructions.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/framework/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/framework/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/framework/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/framework/instructions.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/automate/instructions.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/automate/instructions.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/atdd/README.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/atdd/atdd-checklist-template.md
- Bash示例可能有问题: bmad/bmm/workflows/testarch/atdd/instructions.md
- Bash示例可能有问题: bmad/bmm/workflows/1-analysis/research/README.md
- Bash示例可能有问题: bmad/bmm/workflows/1-analysis/research/README.md
- Bash示例可能有问题: bmad/bmm/workflows/1-analysis/product-brief/README.md
- Bash示例可能有问题: bmad/bmm/workflows/1-analysis/document-project/templates/index-template.md
- Bash示例可能有问题: bmad/bmm/workflows/1-analysis/document-project/templates/index-template.md
- Bash示例可能有问题: bmad/bmm/workflows/1-analysis/document-project/templates/index-template.md
- Bash示例可能有问题: bmad/bmm/workflows/3-solutioning/architecture/readme.md
- Bash示例可能有问题: bmad/bmm/workflows/3-solutioning/architecture/architecture-template.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/test-priorities-matrix.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/selective-testing.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/selective-testing.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/selective-testing.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/selective-testing.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/nfr-criteria.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/playwright-config.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/playwright-config.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/ci-burn-in.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/ci-burn-in.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/ci-burn-in.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/visual-debugging.md
- Bash示例可能有问题: bmad/bmm/testarch/knowledge/visual-debugging.md
- Bash示例可能有问题: bmad/cis/workflows/README.md
- Bash示例可能有问题: bmad/cis/workflows/innovation-strategy/README.md
- Bash示例可能有问题: bmad/cis/workflows/storytelling/README.md
- Bash示例可能有问题: bmad/cis/workflows/design-thinking/README.md
- Bash示例可能有问题: bmad/cis/workflows/problem-solving/README.md
- Bash示例可能有问题: bmad/core/workflows/brainstorming/README.md
- Bash示例可能有问题: bmad/bmb/workflows/create-module/README.md
- Bash示例可能有问题: bmad/bmb/workflows/convert-legacy/README.md
- Bash示例可能有问题: bmad/bmb/workflows/convert-legacy/README.md
- Bash示例可能有问题: bmad/bmb/workflows/create-agent/README.md
- Bash示例可能有问题: bmad/bmb/workflows/create-agent/README.md
- Bash示例可能有问题: bmad/bmb/workflows/module-brief/README.md
- Bash示例可能有问题: bmad/bmb/workflows/module-brief/README.md

---

## 🔍 建议行动

### 立即行动 (今天)
- [Link Validity] 修复 35 个问题
- [Consistency] 修复 1 个问题
- [Code Examples] 修复 197 个问题

### 短期行动 (本周)
- 运行文档同步脚本
- 修复发现的链接问题
- 更新过时文档
- 添加自动化检查

### 长期行动 (本月)
- 建立文档维护流程
- 培训团队文档规范
- 优化文档结构
- 提升文档覆盖率

---

*此报告由 scripts/doc_audit.py 自动生成*
