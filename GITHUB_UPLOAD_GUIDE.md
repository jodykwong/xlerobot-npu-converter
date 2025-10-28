# GitHub 上传指南

本指南将帮助您将 XLeRobot 项目上传到您的 GitHub 账户。

## 📋 准备工作

✅ 已完成：
- Git 仓库已初始化
- 所有文件已添加到 git
- `.gitignore` 文件已创建
- `README.md` 已创建
- 项目已提交 (`git commit`)

## 🚀 上传步骤

### 步骤 1: 创建 GitHub 仓库

1. 打开 [GitHub.com](https://github.com) 并登录您的账户
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `xlerobot-npu-converter` (或您喜欢的名称)
   - **Description**: `XLeRobot NPU模型转换工具 - 企业级ONNX到BPU转换解决方案`
   - **Visibility**: 选择 "Public" 或 "Private"
   - **⚠️ 不要勾选** "Add a README file" (我们已经有了)
   - **⚠️ 不要勾选** "Add .gitignore" (我们已经有了)
   - **⚠️ 不要选择** "Choose a license" (可选)
4. 点击 "Create repository"

### 步骤 2: 添加远程仓库并推送

在终端中运行以下命令：

```bash
# 1. 切换到项目目录
cd /home/sunrise/xlerobot

# 2. 添加远程仓库 (替换 YOUR_USERNAME 为您的GitHub用户名)
git remote add origin https://github.com/YOUR_USERNAME/xlerobot-npu-converter.git

# 3. 重命名主分支为 main (可选)
git branch -M main

# 4. 推送到 GitHub
git push -u origin main
```

### 步骤 3: 验证上传

1. 刷新您的 GitHub 仓库页面
2. 您应该看到所有文件已上传
3. 检查 `README.md` 是否正确显示项目信息

## 🔧 命令行工具 (如果需要)

如果您的系统没有 Git，请先安装：

### Ubuntu/Debian:
```bash
sudo apt-get install git
```

### macOS:
```bash
brew install git
```

### Windows:
下载并安装 [Git for Windows](https://git-scm.com/download/win)

## 📝 自定义仓库名称

如果您想使用不同的仓库名称，请将命令中的 `xlerrobot-npu-converter` 替换为您喜欢的名称：

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

## 🔐 身份验证

### 使用 GitHub CLI (推荐):
```bash
# 安装 GitHub CLI
# https://cli.github.com/

# 登录
gh auth login

# 推送时使用
git push -u origin main
```

### 使用 Personal Access Token:
如果使用 HTTPS URL，您需要使用 Personal Access Token 而不是密码：

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择权限: `repo` (完整仓库访问)
4. 复制生成的 token
5. 推送时，当提示输入密码时，粘贴 token

## ✅ 完成后检查清单

- [ ] GitHub 仓库已创建
- [ ] 远程仓库已添加
- [ ] 代码已推送到 GitHub
- [ ] README.md 正确显示
- [ ] 文件结构完整

## 🎉 恭喜！

您的项目已成功上传到 GitHub！现在您可以：

1. 分享仓库链接
2. 邀请协作者
3. 设置 GitHub Pages (如果需要)
4. 配置 CI/CD (GitHub Actions 已包含)

## 📞 需要帮助？

如果您在上传过程中遇到问题：

1. 检查您的 GitHub 用户名和仓库名称是否正确
2. 确保您有仓库的写入权限
3. 检查网络连接
4. 查看 GitHub 官方文档: [https://docs.github.com](https://docs.github.com)

---

**提示**: 保留此文档以备将来参考！
