# GitHub 身份验证设置指南

## 问题
推送时提示身份验证失败，需要配置GitHub访问凭证。

## 解决方案 1: 使用 Personal Access Token (推荐)

### 步骤 1: 生成 Personal Access Token

1. 打开浏览器，访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写信息:
   - Note: "XLeRobot Upload Token"
   - Expiration: 选择您希望的期限
   - Scopes: ✅ 勾选 "repo" (完整仓库访问权限)
4. 点击 "Generate token"
5. **⚠️ 重要**: 复制生成的token (格式类似: ghp_xxxxxxxxxxxxxxxxxxxx)

### 步骤 2: 配置 Git 使用 Token

在终端中执行:

```bash
# 设置远程仓库URL (如果还没有)
git remote set-url origin https://github.com/jodykwong/xlerobot-npu-converter.git

# 推送时使用token作为密码
git push -u origin main
```

当提示输入用户名时: 输入 `jodykwong`
当提示输入密码时: 粘贴刚才生成的Personal Access Token

### 步骤 3: 保存凭证 (可选)

为避免每次都输入，可以保存凭证:

```bash
git config --global credential.helper store
```

下次推送时会记住您的token。

## 解决方案 2: 使用 SSH (备选)

如果您想使用SSH方式:

1. **生成 SSH 密钥**:
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```

2. **添加 SSH 密钥到 GitHub**:
   - 访问: https://github.com/settings/ssh/new
   - 粘贴您的公钥 (~/.ssh/id_ed25519.pub)

3. **更改远程仓库为 SSH**:
   ```bash
   git remote set-url origin git@github.com:jodykwong/xlerobot-npu-converter.git
   ```

4. **推送**:
   ```bash
   git push -u origin main
   ```

## 验证推送

推送成功后，检查:
- [ ] 浏览器打开 https://github.com/jodykwong/xlerobot-npu-converter
- [ ] 所有文件已显示
- [ ] README.md 正确渲染
- [ ] 提交历史正确

## 🎉 恭喜!

您的 XLeRobot 项目现已上传到 GitHub！

项目地址: https://github.com/jodykwong/xlerobot-npu-converter
