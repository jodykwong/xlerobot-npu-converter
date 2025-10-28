# API Error解决方案工具包

## 🚨 问题
当使用BMM工作流程更新文件时，可能遇到错误：
```
API Error: Cannot read properties of undefined (reading 'map')
```

## ⚠️ 重启后会复发吗？

**是的** - BMM工作流程引擎本身有bug，重启后问题仍会出现。

## ✅ 永久解决方案

我们在项目中创建了3个工具来永久解决这个问题：

### 1. 快速修复脚本（推荐）

```bash
# 交互式模式
bash scripts/quick_fix_api_error.sh

# 更新特定故事
bash scripts/quick_fix_api_error.sh --update story-3.1

# 备份文件
bash scripts/quick_fix_api_error.sh --backup docs/stories/story-3.1.md
```

### 2. 安全文件处理器

```bash
# 直接运行
python3 scripts/safe_bmm_file_handler.py
```

### 3. 详细FAQ指南

```bash
# 查看完整指南
cat scripts/API_ERROR_FAQ.md
```

## 🎯 最佳实践

### 当BMM工作流程要求更新文件时：

#### ❌ 不要直接使用BMM的文件更新功能

#### ✅ 应该这样做：

1. **使用快速修复脚本**
   ```bash
   bash scripts/quick_fix_api_error.sh
   # 选择 "更新故事状态"
   ```

2. **或手动编辑文件**
   ```bash
   vim docs/stories/story-3.1.md
   # 手动找到并修改要更新的内容
   ```

3. **或使用安全工具**
   ```bash
   python3 scripts/safe_bmm_file_handler.py
   # 按照提示操作
   ```

### 预防措施：

1. **提前备份**
   ```bash
   bash scripts/quick_fix_api_error.sh --backup docs/stories/story-3.1.md
   ```

2. **设置别名**
   ```bash
   # 添加到 ~/.bashrc
   alias safe-update='cd /home/sunrise/xlerobot && bash scripts/quick_fix_api_error.sh'
   ```

3. **使用前检查**
   ```bash
   bash scripts/quick_fix_api_error.sh --check
   ```

## 📋 工具对比

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| quick_fix_api_error.sh | 交互式、用户友好 | 日常使用 |
| safe_bmm_file_handler.py | 程序化、灵活 | 脚本集成 |
| API_ERROR_FAQ.md | 文档、详细说明 | 学习和参考 |

## 🔧 工具位置

所有工具都在 `/home/sunrise/xlerobot/scripts/` 目录中：

```
scripts/
├── quick_fix_api_error.sh      # 快速修复脚本（可执行）
├── safe_bmm_file_handler.py    # 安全文件处理器
└── API_ERROR_FAQ.md           # 详细FAQ文档
```

## 💡 关键要点

1. **问题根源**: BMM工作流程引擎的bug
2. **重启后会复发**: 引擎bug未修复
3. **解决方案**: 使用永久的工具绕过引擎
4. **最佳实践**: 始终使用安全工具更新文件
5. **预防措施**: 提前备份，设置别名

## 🆘 需要帮助？

```bash
# 查看完整FAQ
cat scripts/API_ERROR_FAQ.md

# 查看快速修复脚本帮助
bash scripts/quick_fix_api_error.sh --help

# 运行交互式模式
bash scripts/quick_fix_api_error.sh
```

---

**记住**: 这些工具是永久的，保存在项目目录中，重启Claude Code后仍可用！
