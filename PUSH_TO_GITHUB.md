# 推送代码到 GitHub 指南

## 📦 待推送的提交

```bash
77ce5c4 docs: 添加 AI 模板系统优化建议文档
98ba681 feat: 实现 AI 模板生成系统
```

---

## 方法 1：使用 Personal Access Token (推荐)

### 步骤 1：创建 GitHub Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选权限：
   - ✅ repo (所有子选项)
   - ✅ workflow
4. 点击 "Generate token"
5. **复制生成的 token**（只显示一次！）

### 步骤 2：推送代码

```bash
# 在项目目录下运行
cd /home/candy/project/yueen-Technical-Document-Start

# 推送到 GitHub（会要求输入用户名和密码）
git push origin main
# Username: coco830
# Password: [粘贴你的 Personal Access Token]
```

### 步骤 3：保存凭据（可选）

```bash
# 保存凭据，下次不用再输入
git config credential.helper store
git push origin main
```

---

## 方法 2：使用 SSH Key

### 步骤 1：生成 SSH Key

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按回车使用默认路径
# 可以设置密码或直接回车

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

### 步骤 2：添加 SSH Key 到 GitHub

1. 复制公钥内容
2. 访问：https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥，点击 "Add SSH key"

### 步骤 3：修改远程仓库 URL

```bash
# 将 HTTPS URL 改为 SSH URL
git remote set-url origin git@github.com:coco830/Technical-Document-Start.git

# 推送
git push origin main
```

---

## 方法 3：从 Windows 推送（最简单）

如果在 Windows 上安装了 Git：

```bash
# 在 Windows PowerShell 或 CMD 中
cd C:\path\to\yueen-Technical-Document-Start
git push origin main
```

Windows 的 Git Credential Manager 会自动处理认证。

---

## 验证推送成功

推送成功后，访问：
https://github.com/coco830/Technical-Document-Start/commits/main

应该能看到最新的两个提交。

---

## 常见问题

### Q1: "fatal: could not read Username"
**解决**：使用方法 1 或方法 2 设置认证

### Q2: "Authentication failed"
**解决**：确保 Personal Access Token 有正确的权限

### Q3: "Permission denied (publickey)"
**解决**：检查 SSH Key 是否正确添加到 GitHub

---

## 快速推送（如果已配置认证）

```bash
cd /home/candy/project/yueen-Technical-Document-Start
git push origin main
```

---

## 需要帮助？

如果遇到问题，请查看详细错误信息：
```bash
GIT_TRACE=1 git push origin main
```
