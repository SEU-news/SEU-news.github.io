# SEU News 项目设计规范

## 概述

本文档定义 SEU News 整个项目的设计规范，包括：

- **公开页面** (Home, News, About, Contact, Search)
- **认证页面** (Login, Register)
- **管理页面** (Manage, Upload, Edit, Review, Publish, Preview)
- **管理后台** (Dashboard, Users, Deadlines, Entries)
- **组件和工具**

本文档旨在确保所有前端页面保持统一的视觉风格、交互模式和代码规范。

---

## 设计原则

### 1. 整体架构

#### 页面类型分类与布局模式

**公开页面** (无需认证 - 顶部导航栏布局):

- Home.vue - 首页
- News.vue - 新闻列表
- About.vue - 关于
- Contact.vue - 联系我们
- Search.vue - 搜索结果

**布局模式:** Navbar + Main Content

```html
<Navbar />
<main>
  <!-- 页面内容 -->
</main>
```

**认证页面** (仅未登录可访问 - 居中卡片布局):

- Login.vue - 登录
- Register.vue - 注册

**布局模式:** Centered Card

```html
<div class="auth-container">
  <div class="auth-card">
    <!-- 表单内容 -->
  </div>
</div>
```

**管理页面** (需要 Editor+ 权限 - 侧边栏布局):

- Manage.vue - 管理首页
- Upload.vue - 上传内容
- Describe.vue - 描述内容
- Edit.vue - 编辑内容
- Review.vue - 审核内容
- Publish.vue - 发布内容
- Preview.vue - 预览编辑

**布局模式:** Sidebar + Main Content

```html
<ManageLayout />
<!-- 子路由在 ManageLayout 的 router-view 中渲染 -->
```

**管理后台** (需要 Admin 权限 - 深色侧边栏布局):

- AdminDashboard.vue - 仪表板
- AdminUsers.vue - 用户管理
- AdminDeadlines.vue - 截止日期管理
- AdminEntries.vue - 条目管理

**布局模式:** Dark Sidebar + Main Content

```html
<AdminLayout />
<!-- 子路由在 AdminLayout 的 router-view 中渲染 -->
```

### 2. 统一的样式系统

- 使用 Bootstrap 5 基础类名
- 自定义样式定义在 `admin.css` 中
- 颜色系统统一使用 Tailwind 调色板参考色值

### 3. 一致的交互模式

- 操作按钮：主操作用 `btn-primary`，危险操作用 `btn-danger`
- 模态框：统一的 backdrop 和 content 结构
- 表单：使用 `.form-group` 包裹 label 和 input
- 空状态：统一的 `.empty-state` 样式
- 加载状态：统一的 `.loading-spinner` 样式

---

## 组件规范

### 侧边栏导航

```html
<nav class="admin-sidebar-nav">
  <router-link to="/path" class="admin-nav-item" active-class="router-link-active">
    <i>📊</i>
    <span>标题</span>
  </router-link>
</nav>
```

**关键点:**

- 必须添加 `active-class="router-link-active"` 属性
- 图标使用 emoji 或 SVG
- 激活状态有左边框高亮

### 管理侧边栏 (Manage 页面)

```html
<aside class="manage-sidebar">
  <nav class="manage-nav">
    <router-link to="/manage" class="nav-item" active-class="active">
      <i>📋</i>
      <span>管理首页</span>
    </router-link>
    <router-link to="/manage/upload" class="nav-item" active-class="active">
      <i>📤</i>
      <span>上传</span>
    </router-link>
    <!-- 更多导航项 -->
  </nav>
</aside>
```

**关键点:**

- 浅色侧边栏背景 (#f8f9fa)
- 激活项高亮颜色 (#3498db)

### 页面头部 (所有页面通用)

```html
<div class="admin-header">
  <h2>页面标题</h2>
  <p>页面描述</p>
</div>
```

### 统计卡片

```html
<div class="stat-card primary">
  <div class="stat-label">标签</div>
  <div class="stat-value">{{ value }}</div>
  <div class="stat-icon">📊</div>
</div>
```

**颜色变体:**

- `primary` - 蓝色渐变
- `success` - 绿色渐变
- `warning` - 粉红渐变
- `info` - 青色渐变

### 表格工具栏

```html
<div class="users-toolbar">
  <input type="text" class="form-control" placeholder="搜索..." />
  <select class="form-select">
    <option value="">全部</option>
    <option value="value">选项</option>
  </select>
</div>
```

### 内容卡片 (公开页面)

```html
<div class="content-card">
  <div class="card-image">
    <img :src="entry.image" :alt="entry.title" />
  </div>
  <div class="card-body">
    <h3 class="card-title">{{ entry.title }}</h3>
    <p class="card-meta">
      <span class="badge">{{ entry.type }}</span>
      <span class="date">{{ formatDate(entry.created_at) }}</span>
    </p>
    <p class="card-desc">{{ shortText(entry.content) }}</p>
    <a :href="entry.link" target="_blank" class="btn btn-primary">查看详情</a>
  </div>
</div>
```

**样式:**

```css
.content-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
}

.content-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-image img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.card-body {
  padding: 20px;
}

.card-title {
  margin: 0 0 10px 0;
  color: #2c3e50;
}
```

### 认证表单 (Login/Register)

```html
<div class="auth-container">
  <div class="auth-card">
    <h2 class="auth-title">登录</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>用户名</label>
        <input v-model="form.username" type="text" class="form-control" required />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="form.password" type="password" class="form-control" required />
      </div>
      <button type="submit" class="btn btn-primary w-100">登录</button>
    </form>
    <div class="auth-footer">
      <router-link to="/register">没有账号？注册</router-link>
    </div>
  </div>
</div>
```

**样式:**

```css
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.auth-title {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
}
```

### 顶部导航栏 (公开页面)

```html
<nav class="navbar navbar-expand-lg">
  <div class="container">
    <router-link to="/" class="navbar-brand">
      SEU News
    </router-link>
    <div class="navbar-nav">
      <router-link to="/news" class="nav-link" active-class="active">
        新闻
      </router-link>
      <router-link to="/about" class="nav-link" active-class="active">
        关于
      </router-link>
      <router-link to="/contact" class="nav-link" active-class="active">
        联系
      </router-link>
    </div>
    <div class="auth-buttons">
      <router-link v-if="!isLoggedIn" to="/login" class="btn btn-outline-primary">
        登录
      </router-link>
      <router-link v-else to="/manage" class="btn btn-primary">
        管理后台
      </router-link>
    </div>
  </div>
</nav>
```

### 数据表格

```html
<div class="table-container">
  <table class="users-table">
    <thead>...</thead>
    <tbody>
      <tr v-for="item in items">
        <td>{{ item.field }}</td>
      </tr>
    </tbody>
  </table>
</div>
```

### 分页控件

```html
<div class="pagination d-flex justify-content-center mt-3">
  <button class="btn btn-outline-primary me-2" :disabled="page === 1" @click="page--">
    上一页
  </button>
  <span>第 {{ page }} / {{ totalPages }} 页</span>
  <button class="btn btn-outline-primary ms-2" :disabled="page === totalPages" @click="page++">
    下一页
  </button>
</div>
```

### 模态框

```html
<div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
  <div class="modal-content">
    <div class="modal-header">
      <h3>标题</h3>
      <button class="close-btn" @click="closeModal">&times;</button>
    </div>
    <div class="modal-body">
      <!-- 表单内容 -->
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" @click="closeModal">取消</button>
      <button class="btn btn-primary" @click="save">保存</button>
    </div>
  </div>
</div>
```

**关键点:**

- backdrop 使用 `@click.self` 关闭（点击内容区不关闭）
- 统一的 header/footer 结构
- 按钮顺序：取消在前，保存在后

## 颜色系统

### 主色调

- 主色: #3498db
- 成功: #2ecc71
- 警告: #f39c12
- 危险: #e74c3c
- 信息: #1abc9c

### 渐变色

```css
.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
.warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.info { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
```

## 权限徽章

```css
.badge-editor { background-color: #3498db; }
.badge-admin { background-color: #e74c3c; }
.badge-super { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
```

## 响应式设计

### 移动端断点

```css
@media (max-width: 768px) {
  .admin-sidebar { width: 100%; position: relative; }
  .admin-main { margin-left: 0; padding: 20px 15px; }
  .dashboard-stats { grid-template-columns: 1fr; }
  .deadline-form .form-row { grid-template-columns: 1fr; }
}
```

## 常用代码片段

### 格式化日期

```javascript
function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}
```

### 确认对话框

```javascript
if (confirm('确定执行此操作？')) {
  await apiCall()
}
```

### 加载状态管理

```javascript
const loading = ref(true)
async function fetchData() {
  try {
    loading.value = true
    const data = await apiCall()
    // 处理数据
  } catch (error) {
    console.error(error)
    alert('操作失败')
  } finally {
    loading.value = false
  }
}
```

## API 调用规范

### 所有 API 调用

- 使用 `front-vue/src/api/` 下的模块
- 统一使用 async/await
- try-catch 包裹错误处理
- 操作成功后显示 alert 提示

### API 文件结构

- `auth.js` - 认证相关
- `content.js` - 内容 CRUD
- `publish.js` - 发布功能
- `review.js` - 审核流程
- `user.js` - 用户管理

## 路由守卫与权限

### 公开页面路由

```typescript
{
  path: '/',
  name: 'Home',
  component: () => import('../views/Home.vue')
  // 无 meta 字段，所有人可访问
}
```

### 认证页面路由 (仅未登录)

```typescript
{
  path: '/login',
  name: 'Login',
  component: () => import('../views/Login.vue'),
  meta: { guestOnly: true }  // 已登录用户重定向到首页
}
```

### 管理页面路由 (需要 Editor+)

```typescript
{
  path: '/manage/upload',
  name: 'Upload',
  component: () => import('../views/Upload.vue'),
  meta: {
    requiresAuth: true,
    requiresEditor: true
  }
}
```

### 管理后台路由 (需要 Admin)

```typescript
{
  path: '/manage/admin/users',
  name: 'AdminUsers',
  component: () => import('../views/admin/AdminUsers.vue'),
  meta: {
    requiresAuth: true,
    requiresAdmin: true
  }
}
```

### 路由守卫逻辑

```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 恢复登录状态
  authStore.restoreState()

  const { requiresAuth, requiresEditor, requiresAdmin, guestOnly } = to.meta

  // 未登录且需要认证
  if (requiresAuth && !authStore.isLoggedIn) {
    return next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }

  // 仅未登录可访问
  if (guestOnly && authStore.isLoggedIn) {
    return next('/')
  }

  // 需要 Editor 权限
  if (requiresEditor && !authStore.hasEditorPerm) {
    return next('/403')
  }

  // 需要 Admin 权限
  if (requiresAdmin && !authStore.hasAdminPerm) {
    return next('/403')
  }

  next()
})
```

## 表单组件规范

### 内容上传表单

```html
<div class="upload-form">
  <div class="form-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      @click="activeTab = tab.id"
      :class="['tab-button', { active: activeTab === tab.id }]"
    >
      {{ tab.label }}
    </button>
  </div>

  <!-- 文本上传 -->
  <div v-if="activeTab === 'text'" class="tab-content">
    <div class="form-group">
      <label>标题 *</label>
      <input v-model="form.title" type="text" class="form-control" required />
    </div>
    <div class="form-group">
      <label>短标题</label>
      <input v-model="form.short_title" type="text" class="form-control" />
    </div>
    <div class="form-group">
      <label>内容 *</label>
      <textarea v-model="form.content" class="form-control" rows="10" required />
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>链接</label>
        <input v-model="form.link" type="url" class="form-control" />
      </div>
      <div class="form-group">
        <label>刊载版块</label>
        <select v-model="form.type" class="form-select" required>
          <option value="教务">教务</option>
          <option value="校园">校园</option>
          <option value="学术">学术</option>
          <option value="活动">活动</option>
        </select>
      </div>
    </div>
  </div>

  <!-- URL 粘贴 -->
  <div v-if="activeTab === 'url'" class="tab-content">
    <div class="form-group">
      <label>URL 链接</label>
      <input v-model="form.pasteUrl" type="url" class="form-control" placeholder="https://..." />
    </div>
    <button class="btn btn-primary" @click="pasteUrl">解析内容</button>
  </div>

  <!-- 图片上传 -->
  <div v-if="activeTab === 'image'" class="tab-content">
    <div class="upload-zone" @click="triggerFileInput">
      <i>📤</i>
      <p>点击或拖拽图片到此处</p>
      <input ref="fileInput" type="file" accept="image/*" @change="handleFileUpload" hidden />
    </div>
  </div>

  <button class="btn btn-primary btn-lg" @click="submit">上传内容</button>
</div>
```

**样式:**

```css
.upload-form {
  background: white;
  border-radius: 12px;
  padding: 30px;
}

.form-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #dee2e6;
}

.tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  color: #6c757d;
  font-size: 1rem;
  position: relative;
  cursor: pointer;
}

.tab-button.active {
  color: #3498db;
  font-weight: 600;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -32px;
  left: 0;
  right: 0;
  height: 3px;
  background: #3498db;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.upload-zone {
  border: 2px dashed #dee2e6;
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-zone:hover {
  border-color: #3498db;
  background: #f8f9fa;
}
```

### 富文本编辑器

```html
<div class="editor-container">
  <div class="editor-toolbar">
    <button @click="format('bold')" class="toolbar-btn" title="加粗">
      <strong>B</strong>
    </button>
    <button @click="format('italic')" class="toolbar-btn" title="斜体">
      <em>I</em>
    </button>
    <button @click="format('underline')" class="toolbar-btn" title="下划线">
      <u>U</u>
    </button>
    <div class="toolbar-separator"></div>
    <button @click="insertHeading" class="toolbar-btn" title="标题">
      H
    </button>
    <button @click="insertList" class="toolbar-btn" title="列表">
      ☰
    </button>
    <div class="toolbar-separator"></div>
    <button @click="insertLink" class="toolbar-btn" title="插入链接">
      🔗
    </button>
  </div>
  <div
    class="editor-content"
    contenteditable="true"
    v-html="form.content"
    @input="updateContent"
  ></div>
</div>
```

**样式:**

```css
.editor-container {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  gap: 5px;
}

.toolbar-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.toolbar-btn:hover {
  background: #e9ecef;
}

.toolbar-separator {
  width: 1px;
  height: 24px;
  background: #dee2e6;
  margin: 0 5px;
}

.editor-content {
  min-height: 300px;
  padding: 20px;
  line-height: 1.6;
}

.editor-content:focus {
  outline: none;
}
```

## 提示与通知系统

### Toast 通知组件

```html
<div class="toast-container">
  <div
    v-for="toast in toasts"
    :key="toast.id"
    :class="['toast', toast.type]"
    @click="removeToast(toast.id)"
  >
    <div class="toast-icon">{{ toast.icon }}</div>
    <div class="toast-content">
      <h4 class="toast-title">{{ toast.title }}</h4>
      <p class="toast-message">{{ toast.message }}</p>
    </div>
    <button class="toast-close">&times;</button>
  </div>
</div>
```

**类型与样式:**

```css
.toast {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #d4edda;
  border-left: 4px solid #2ecc71;
}

.toast.error {
  background: #f8d7da;
  border-left: 4px solid #e74c3c;
}

.toast.warning {
  background: #fff3cd;
  border-left: 4px solid #f39c12;
}

.toast.info {
  background: #d1ecf1;
  border-left: 4px solid #3498db;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

**使用示例:**

```javascript
import { useToast } from '@/composables/toast'

const { showToast } = useToast()

// 成功提示
showToast({
  type: 'success',
  title: '操作成功',
  message: '用户信息已更新'
})

// 错误提示
showToast({
  type: 'error',
  title: '操作失败',
  message: '网络连接错误，请重试'
})
```

## 最佳实践

### 1. 命名规范

- **组件文件**: PascalCase (AdminUsers.vue)
- **状态变量**: camelCase (users, loading)
- **CSS 类**: kebab-case (users-table, admin-header)

### 2. 响应式数据

- 优先使用 `computed` 处理衍生数据
- `watch` 监听分页等状态变化
- `onMounted` 初始化数据加载

### 3. 错误处理

- 所有 async 函数使用 try-catch
- 控制台输出错误详情
- 用户友好的错误提示（alert）

### 4. 用户体验

- 长列表添加分页
- 提供搜索和筛选功能
- 危险操作需要二次确认
- 加载中显示 loading 动画
- 空数据状态友好提示

### 5. 代码复用

- 相似功能提取为组件
- 通用样式定义在 admin.css
- API 调用统一使用 api 模块

## 已知问题

### AdminUsers.vue 中的拼写错误

- 代码中存在 `editingUser.value.id` (正确写法)，需注意保持一致性

### 导航高亮问题

- AdminLayout.vue 的 router-link 需要添加 `active-class` 属性（已在优化计划中修复）

---

*最后更新: 2026-02-10*
