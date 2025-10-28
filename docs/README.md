# XLeRobot 项目文档中心

**项目**: XLeRobot NPU模型转换工具
**最后更新**: 2025-10-25
**文档状态**: 活跃开发中

---

## 🎯 项目概述

XLeRobot NPU模型转换工具是一个专用的AI模型NPU格式转换工具，旨在将SenseVoice ASR、Piper VITS TTS等AI模型转换为RDK X5 NPU硬件可执行格式，实现2-5倍的性能提升。

**技术栈**: Ubuntu 20.04 + Python 3.10 + Docker + RDK X5 BPU
**当前阶段**: Phase 2 - Planning (PRD开发中)
**总体进度**: 15% 完成

---

## 📚 文档结构

### 🚀 项目管理文档

#### 核心状态文档
- **[工作流程状态](./bmm-workflow-status.md)** - BMad工作流程状态跟踪
- **[项目进度概览](./project-progress-overview.md)** - 详细的项目进度和指标
- **[产品Brief](./bmm-product-brief-XLeRobot%20NPU模型转换工具-2025-10-25.md)** - 完整的产品需求分析

#### BMad工作流程文档
- **[工作流程配置](../bmad/bmm/workflows/workflow-status/)** - 工作流程配置文件
- **[路径配置](../bmad/bmm/workflows/workflow-status/paths/)** - 项目类型路径定义

### 🛠️ 技术实施文档

#### 核心SOP文档
- **[项目重构SOP](../xlerobot-project-reconstruction-sop.md)** - 完整的系统重构方案
- **[模型转换SOP](../SenseVoice_Horizon_X5_转换问题排查SOP.md)** - NPU模型转换技术细节

#### 技术参考文档
- **[紧急恢复指南](../yahboom_ws/EMERGENCY_RECOVERY.md)** - (存在时) 系统应急恢复流程
- **[架构文档](../yahboom_ws/docs/architecture.md)** - (存在时) 系统架构设计

### 📊 配置和模板文档

#### BMad配置
- **[BMad配置](../bmad/bmm/config.yaml)** - 核心配置文件
- **[代理配置](../.claude/commands/bmad/bmm/agents/)** - 各种代理的配置

#### 模板和标准
- **[产品Brief模板](../bmad/bmm/workflows/1-analysis/product-brief/template.md)** - 产品Brief模板
- **[PRD模板](../bmad/bmm/workflows/2-planning/prd/template.md)** - PRD模板 (待使用)

---

## 🎯 当前项目状态

### 📈 进度概览
```
Phase 1 - Analysis:     ✅ 100% COMPLETE
Phase 2 - Planning:     🔄 0%  IN PROGRESS
Phase 3 - Solutioning:  ⏳ 0%  PENDING
Phase 4 - Implementation: ⏳ 0%  PENDING

总体进度: 15%
```

### 🔄 当前工作流程
- **当前阶段**: Phase 2 - Planning
- **当前工作流**: PRD (产品需求文档)
- **负责代理**: Product Manager
- **下一步**: 执行 `*prd` 命令开始PRD开发

### 📋 最近完成
- ✅ 产品Brief完成 (2025-10-25)
- ✅ 项目范围明确定义
- ✅ 技术约束确定 (Ubuntu 20.04 + Python 3.10)
- ✅ 可扩展架构设计

---

## 🚀 快速开始

### 对于项目成员

1. **查看项目状态**
   ```bash
   cat docs/bmm-workflow-status.md
   ```

2. **了解进度详情**
   ```bash
   cat docs/project-progress-overview.md
   ```

3. **查看产品需求**
   ```bash
   cat docs/bmm-product-brief-XLeRobot\ NPU模型转换工具-2025-10-25.md
   ```

### 对于开发者

1. **理解技术要求**
   - 查看 [项目重构SOP](../xlerobot-project-reconstruction-sop.md)
   - 查看 [模型转换SOP](../SenseVoice_Horizon_X5_转换问题排查SOP.md)

2. **准备开发环境**
   - Ubuntu 20.04 系统
   - Python 3.10 环境
   - Docker 容器支持
   - RDK X5 硬件平台

### 对于项目经理

1. **开始PRD开发**
   ```bash
   # 启动产品经理代理
   /bmad:bmm:agents:pm

   # 执行PRD工作流
   *prd
   ```

2. **参考产品Brief**
   - 基于 [产品Brief](./bmm-product-brief-XLeRobot%20NPU模型转换工具-2025-10-25.md) 开发详细PRD

---

## 📊 质量门禁

| 门禁 | 状态 | 文档链接 |
|------|------|----------|
| **Analysis Gate** | ✅ PASS | [产品Brief](./bmm-product-brief-XLeRobot%20NPU模型转换工具-2025-10-25.md) |
| **Planning Gate** | 🔄 IN PROGRESS | [PRD文档](./) (待创建) |
| **Solutioning Gate** | ⏳ PENDING | [架构文档](./) (待创建) |
| **Implementation Gate** | ⏳ PENDING | [技术规格](./) (待创建) |

---

## 🔗 相关资源

### BMad工作流程系统
- **BMad核心文档**: [../bmad/core/](../bmad/core/)
- **工作流程配置**: [../bmad/bmm/workflows/](../bmad/bmm/workflows/)
- **代理配置**: [../.claude/commands/](../.claude/commands/)

### 外部资源
- **Horizon X5文档**: [D-Robotics官方文档](https://developer.d-robotics.cc/)
- **Docker文档**: [Docker官方文档](https://docs.docker.com/)
- **ONNX文档**: [ONNX官方文档](https://onnx.ai/)

---

## 📞 联系和支持

### 项目角色
- **项目负责人**: Jody
- **当前分析师**: Mary (Business Analyst)
- **下一步负责**: Product Manager (待指定)

### 文档维护
- **更新频率**: 重大里程碑后，或至少每3天
- **维护责任人**: 项目负责人
- **版本控制**: Git版本控制，所有变更都有历史记录

---

## 📝 文档更新日志

### 2025-10-25
- ✅ 创建项目文档中心
- ✅ 系统性更新项目状态
- ✅ 建立文档结构和索引
- ✅ 完成Phase 1 Analysis阶段文档

### 未来计划
- 📋 PRD开发完成后更新文档
- 📋 架构设计完成后添加技术文档
- 📋 实施开始后添加开发指南

---

*本文档作为XLeRobot项目的中心文档索引，所有相关文档的最新版本和链接都可以在这里找到。*

**最后更新**: 2025-10-25 14:30
**维护者**: Jody
**版本**: 1.0