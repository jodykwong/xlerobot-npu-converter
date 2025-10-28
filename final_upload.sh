#!/bin/bash
# 最终上传脚本 - 需要用户提供GitHub用户名

echo "=============================================="
echo "  XLeRobot 项目最终上传脚本"
echo "=============================================="
echo

# 读取GitHub用户名
if [ -z "$1" ]; then
    echo "请在命令后提供您的GitHub用户名:"
    echo "  例如: ./final_upload.sh YOUR_USERNAME"
    echo
    exit 1
fi

GITHUB_USER=$1
REPO_NAME="xlerobot-npu-converter"

echo "GitHub用户名: $GITHUB_USER"
echo "仓库名称: $REPO_NAME"
echo "仓库URL: https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo

# 确认操作
read -p "确认上传到上述仓库? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "上传已取消"
    exit 1
fi

echo
echo "正在配置远程仓库..."
git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git
if [ $? -eq 0 ]; then
    echo "✅ 远程仓库已添加"
else
    echo "❌ 远程仓库添加失败 (可能已存在)"
fi

echo
echo "正在重命名分支为 main..."
git branch -M main
echo "✅ 分支已重命名"

echo
echo "正在推送到 GitHub..."
echo "⚠️  注意: 如果提示身份验证，请输入您的 GitHub Personal Access Token"
echo
git push -u origin main

if [ $? -eq 0 ]; then
    echo
    echo "=============================================="
    echo "✅ 上传成功！"
    echo "=============================================="
    echo
    echo "您的项目已上传到:"
    echo "  https://github.com/$GITHUB_USER/$REPO_NAME"
    echo
    echo "下一步:"
    echo "  1. 在浏览器中打开您的仓库"
    echo "  2. 验证文件已正确上传"
    echo "  3. 开始转换模型!"
    echo
else
    echo
    echo "❌ 上传失败"
    echo
    echo "常见问题:"
    echo "  - 确保仓库URL正确"
    echo "  - 确保您有仓库的写入权限"
    echo "  - 检查网络连接"
    echo "  - 如果使用HTTPS，需要使用Personal Access Token作为密码"
    echo
fi
