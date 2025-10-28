#!/bin/bash
# 快速上传到GitHub脚本

echo "=============================================="
echo "XLeRobot 项目快速上传到 GitHub"
echo "=============================================="
echo

# 检查是否已配置远程仓库
if ! git remote get-url origin &> /dev/null; then
    echo "⚠️  未检测到远程仓库配置"
    echo
    echo "请在GitHub上创建新仓库，然后运行以下命令:"
    echo
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
    echo "  git push -u origin main"
    echo
    echo "或编辑此脚本，在GITHUB_USER和REPO_NAME变量中填入您的信息，然后重新运行。"
    echo

    # 读取用户输入
    read -p "请输入您的GitHub用户名: " GITHUB_USER
    read -p "请输入仓库名称 (默认: xlerobot-npu-converter): " REPO_NAME

    # 设置默认值
    REPO_NAME=${REPO_NAME:-xlerobot-npu-converter}

    # 添加远程仓库
    git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git
    echo "✅ 远程仓库已添加: https://github.com/$GITHUB_USER/$REPO_NAME.git"
else
    echo "✅ 检测到远程仓库: $(git remote get-url origin)"
fi

echo
echo "正在推送到 GitHub..."
echo

# 推送到 GitHub
git push -u origin main

if [ $? -eq 0 ]; then
    echo
    echo "=============================================="
    echo "✅ 上传成功！"
    echo "=============================================="
    echo
    echo "您的项目已上传到:"
    echo "  $(git remote get-url origin)"
    echo
    echo "下一步:"
    echo "  1. 在浏览器中打开您的仓库"
    echo "  2. 验证文件已正确上传"
    echo "  3. 开始转换模型!"
    echo
else
    echo
    echo "❌ 上传失败，请检查错误信息并重试"
    echo
    echo "常见问题:"
    echo "  - 确保您已登录GitHub"
    echo "  - 检查网络连接"
    echo "  - 验证远程仓库URL是否正确"
    echo
fi
