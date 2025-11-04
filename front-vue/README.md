# Vue 3 + Vite + Django 项目

### 推荐 IDE 设置
- VS Code + Vue (Official) (并禁用 Vetur)。
- PyCharm

### 推荐浏览器设置
- 基于 Chromium 的浏览器 (Chrome, Edge, Brave 等):
  - Vue.js devtools
  - 在 Chrome DevTools 中启用自定义对象格式化程序

- Firefox:
  - Vue.js devtools
  - 在 Firefox DevTools 中启用自定义对象格式化程序

### TypeScript 对 .vue 导入的类型支持
默认情况下，TypeScript 无法处理 .vue 导入的类型信息，因此我们使用 vue-tsc 替换 tsc CLI 进行类型检查。在编辑器中，我们需要 Volar 来让 TypeScript 语言服务识别 .vue 类型。

## 项目指令

### 进入前端目录
```
cd frontend
```

### 安装依赖（必要）
```
npm install
```
### 启动（必要）
```
npm run dev
```
### 类型检查、编译和生产环境压缩
```
npm run build
```
### 使用 Vitest 运行单元测试
```
npm run test:unit
```
### 若遇到配置问题，清理并重新初始化
```
# 删除 node_modules 和 锁定文件
rm node_modules 
rm package-lock.json

# 重新安装依赖
npm install

# 验证基础配置
npm run dev
```

### 若需要运行旧框架
```
# 进入项目根目录
cd SEU-news.github.io

# 进入虚拟环境
cd .venv/Scripts/activate

# 运行启动脚本
python cmd.py
```

