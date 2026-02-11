# 前端依赖安装指南

## 已安装的依赖

### 运行时依赖
- **vue** (^3.4.0) - Vue 3 框架
- **vue-router** (^4.2.0) - 路由管理
- **pinia** (^2.1.0) - 状态管理
- **axios** (^1.13.5) - HTTP 客户端 ✅ 已安装

### 开发依赖
- **vite** (^5.0.0) - 构建工具
- **@vitejs/plugin-vue** (^5.0.0) - Vue 插件
- **eslint** (^8.56.0) - 代码检查
- 等等...

## 安装新依赖

如果需要安装新的依赖，使用以下命令：

```bash
# 确保使用正确的 Node 版本
export PATH="/home/winnower/.nvm/versions/node/v25.6.0/bin:$PATH"

# 安装依赖
npm install <package-name>

# 开发依赖
npm install -D <package-name>
```

## 常用命令

```bash
# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview

# 代码检查
npm run lint

# 运行单元测试
npm run test:unit

# 运行端到端测试
npm run test:e2e
```

## 问题解决

### npm 命令找不到
```bash
export PATH="/home/winnower/.nvm/versions/node/v25.6.0/bin:$PATH"
```

### Vite 编译错误
确保所有依赖已安装：
```bash
npm install
```
