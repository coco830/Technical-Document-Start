# Next.js 配置修复 - 执行步骤

## 📋 立即执行以下命令

```bash
# 1. 进入前端目录
cd frontend

# 2. 备份原配置（可选）
cp next.config.js next.config.js.backup

# 3. 应用修复后的配置
cp next.config.fixed.js next.config.js

# 4. 停止所有Node进程
taskkill /IM node.exe /F

# 5. 清理缓存
rm -rf .next node_modules

# 6. 重新安装依赖（确保无冲突）
npm install --legacy-peer-deps

# 7. 启动开发服务器
npm run dev
```

## ✅ 验证修复

启动后应看到：
- ✓ 无 "Invalid next.config.js options" 警告
- ✓ 无 "exports is not defined" 错误
- ✓ 页面正常加载
- ✓ 热更新正常工作（修改代码后自动刷新）
- ✓ 控制台无模块加载错误

## 📊 预期结果

修复后：
- Next.js使用内置chunk拆分逻辑
- App Router正常工作
- 静态资源正确加载
- 开发体验优化

## 🎯 关键变化

| 原配置 | 修复后 |
|--------|--------|
| reactRefresh: false | 删除此行 |
| 自定义splitChunks | 使用内置优化 |
| 复杂webpack配置 | 简化配置 |

