# MEMORY.md - 项目记忆

> 记录项目开发过程中的重要决策、经验教训和最佳实践

---

## 🤝 多 Agent 协作规范

### 项目协作方式

**本项目由多个 AI Agent 共同协作完成：**
- **主 Agent（Clawdbot）**：负责整体规划、用户沟通、文档管理
- **Claude Code**：负责具体代码实现、bug 修复、技术细节

### 信息同步

#### 主 Agent → Claude Code
- 所有计划记录在 `TEMP_PLAN.md` 中
- Claude Code 应该定期阅读 `TEMP_PLAN.md` 了解当前工作内容
- Claude Code 可以根据计划自主实施任务

#### Claude Code → 主 Agent
- 完成工作后记录到 `TEMP_PLAN.md`
- 发现的问题、解决方案、技术决策都应记录
- 重要的 bug 修复应记录详细原因和解决方案

### 工作流程

1. **主 Agent 制定计划** → 写入 `TEMP_PLAN.md`
2. **Claude Code 阅读计划** → 理解任务目标
3. **Claude Code 实施任务** → 完成后更新 `TEMP_PLAN.md`
4. **主 Agent 检查进度** → 根据实际情况调整计划

### 注意事项

- ✅ **Claude Code 可以直接修改 `TEMP_PLAN.md`** 记录工作进度
- ✅ **重要决策和技术细节应记录到 `MEMORY.md`**
- ✅ **代码层面的信息应同步到 `CLAUDE.md`**
- ❌ **避免在对话中分散重要信息，尽量记录到文件**

---

## 🗣️ 交流方式规范

### 语言偏好
- **主要使用中文和用户交流**（全局规范）
- **适当使用英文**：技术术语、代码注释、文件名、API 端点等
- **示例**：
  - ✅ "我将创建一个新的 API 端点 `/api/auth/login/`"
  - ✅ "需要修改 `api/permissions.py` 文件中的权限检查逻辑"
  - ❌ "我将创建一个新的 API endpoint 用于登录功能"

---

## 📝 工作流程规范

### 计划编写原则（全局规范）
- ✅ **必须先列出计划，等待用户同意后再执行**（全局规范）
- ✅ **所有计划内容应该创建或修改同一个临时 md 文件**（全局规范）
- ✅ **避免分散在对话中导致遗忘**（全局规范）
- ✅ **计划文档应该包含：**
  - 目标和范围
  - 实施步骤（详细）
  - 文件清单
  - 预估工作量
  - 需要确认的问题
  - 完成标准

### 临时计划文档命名
- 使用 `TEMP_PLAN.md` 作为计划文档
- 每次更新计划都修改同一个文件
- 完成后将计划文档改名，打上 `archived` 的标签，并提醒用户检查后手动删除

---

## 🏗️ 技术架构决策

### 后端架构
- **当前状态：** Flask（模板渲染）+ Django（ORM）
- **迁移目标：** Django（ORM + REST API）
- **并行方案：** Flask(42610) + Django API(42611)

### 前端架构
- **框架：** Vue 3 + TypeScript
- **状态管理：** Pinia
- **路由：** Vue Router
- **HTTP 客户端：** Axios
- **构建工具：** Vite

### 权限系统
- **数据库模型：** `role` 字段使用位运算
  - 0 (0b00) = 普通用户
  - 1 (0b01) = 编辑
  - 2 (0b10) = 管理员
  - 3 (0b11) = 超级管理员
- **权限判断：**
  - `has_editor_perm = (role & 1) != 0`
  - `has_admin_perm = (role & 2) != 0`

---

## 📁 项目结构规范

### 路由结构
- **公开页面：** `/`, `/about`, `/contact`, `/news`, `/login`, `/register`
- **需要登录：** `/search`
- **管理页面：** `/manage/*`（Editor/Admin）
- **管理员专属：** `/manage/admin/*`（Admin only）

### API 端点结构
- **基础URL：** `http://localhost:42611/api/`
- **认证：** `/api/auth/*`
- **内容：** `/api/content/*`
- **搜索：** `/api/search/`
- **发布：** `/api/publish/`
- **导出：** `/api/v1/export/*`
- **管理：** `/api/admin/*`

---

## 🔧 开发环境

### WSL 环境
- **Python：** 3.12.3
- **Node.js：** v18.19.1
- **NPM：** 未安装（使用 /home/winnower/.nvm/versions/node/v25.6.0/bin/npm）
- **Conda：** 未配置

### Windows 环境
- **Conda 路径：** `C:\Users\HUAWEI\miniconda3`
- **环境名称：** `seu-news`
- **项目路径：** `D:\pythonProj\seu-news`

### 端口分配
- **Flask（模板）：** 42610
- **Django API：** 42611
- **Vue 开发：** 24610

---

## 💡 经验教训

### 2026-02-09

11. **Django API Review 权限修正** ✅ 已完成
**时间：** 2026-02-09
**问题：** Django API 的审核功能错误地设置为 Admin 专属，应该允许所有 Editor 审核别人的内容
**发现：** Flask 的 `ReviewView` 使用 `PermissionDecorators.editor_required`（只需要 Editor 权限）
**原因：** Django API 配置错误地使用了 `IsAdmin` 权限类
**修正：**
  - Django API：`permission_classes = [IsAuthenticated, IsAdmin]` → `[IsAuthenticated, IsEditorOrAdmin]`
  - 添加检查：不能审核自己创建或描述的内容
  - 前端路由：`/manage/review/:id` 从 Admin 专属改为 Editor+
**注意：** 任何 Editor 都可以审核别人的内容，但不能审核自己的内容

### 2026-02-15
1. **发布 API 重构（关注点分离）：**
   - 问题：职责混乱，内容查询、发布操作、文档生成混在一起
     - `POST /api/publish/pdf/` 和 `POST /api/publish/pdf_from_selection/` 功能重叠
     - `/api/publish/query/` 和 `/api/publish/ddl/` 与 `/api/content/` 查询逻辑重复
     - 未使用的 `unpublish` 功能占用代码空间
     - 文档生成不符合 RESTful 设计
   - 解决：创建独立的导出服务层 `ExportService`
     - 删除所有旧端点（9个旧端点）
     - 新增 4 个导出端点：`/api/v1/export/*`
     - 合并 PDF 生成端点（支持 date 和 content_ids 两种模式）
     - 增强 `ContentListAPIView` 支持发布相关查询参数
     - 端点数从 10 减少到 6（净减少 4 个）
     - 设计原则：内容查询、发布、导出完全分离，职责清晰
2. **前端 API 层更新：**
   - 内容查询现在使用 `ContentListAPIView` 而非专用端点
     - `queryPublishedByDateRange()` 使用 `/api/content/` + 查询参数
     - `queryDDLByDate()` 使用 `/api/content/` + `deadline_end_date` 参数
   - 导出功能统一到 `/api/v1/export/*` 端点
     - 新增 `generatePDF()`, `generateTypst()`, `generateLatex()`, `getExportData()` 函数
3. **函数命名冲突问题：**
   - 问题：组件中使用 `generatePDF` 函数名，与导入的 API 函数名冲突
   - 解决：使用导入别名 `generatePDFAPI` 避免递归调用
   - 代码：
     ```javascript
     import { generatePDF as generatePDFAPI } from '../../api/publish.js'
     // 组件中保留 generatePDF 函数名
     ```

### 2026-02-08
1. **计划管理：**
   - 问题：计划内容分散在对话中，容易遗忘
   - 解决：统一使用 `TEMP_PLAN.md` 管理所有计划

2. **工作流程规范：**
   - 问题：没有统一的工作流程规范
   - 解决：制定全局规范，先列计划，后执行
   - 问题：经常遗忘之前的上下文和计划
   - 解决：定期整理上下文，更新 TEMP_PLAN.md

3. **环境配置：**
   - 问题：WSL 无法直接访问 Windows conda 环境
   - 解决：在 Windows 本地测试，WSL 只创建代码文件

4. **后端选择：**
   - 问题：Flask 当前只返回 HTML，无法直接用于 Vue
   - 解决：使用 Django REST Framework 创建 JSON API

5. **路由重构：**
   - 问题：`/main` 名称混乱，应该叫管理页
   - 解决：重构为 `/manage/*` 结构，更清晰

6. **MCP 服务配置：**
   - 已完成：安装 mcporter，添加 github MCP
   - 待完成：context7 MCP 配置

7. **Flask → Vue 迁移：**
   - 问题：未列计划就直接开始实施
   - 解决：后续工作必须先制定详细计划

8. **Django 启动脚本：**
   - 问题：`execute_from_command_line()` 参数传递错误
     - 错误：`TypeError: execute_from_command_line() takes from 0 to 1 positional arguments but 2 were given`
   - 原因：传递了两个参数，但该函数只接受一个列表参数
   - 解决：修复为 `execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:42611'])`

9. **Django ALLOWED_HOSTS 配置：**
   - 问题：Django 启动时 `CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False`
   - 原因：DEBUG=False 时，Django 要求设置 ALLOWED_HOSTS
   - 解决：在 `config/django_config.py` 中添加：
     ```python
     DEBUG=True  # 开发环境
     ALLOWED_HOSTS=[
         '0.0.0.0',
         'localhost',
         '127.0.0.1',
     ]
     ```

10. **Django 禁用迁移检查：**
    - 需求：不使用 Django migrate 功能，生产环境不允许随意修改 MySQL 字段
    - 问题：Django 启动时提示有未应用的迁移
    - 尝试 1：使用 `--skip-checks` 参数（无效）
      ```python
      execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:42611', '--skip-checks'])
      ```
      结果：`Unknown command: '--skip-checks'`
    - 尝试 2：调整参数顺序（无效）
      ```python
      execute_from_command_line(['manage.py', '--skip-checks', 'runserver', '0.0.0.0:42611'])
      ```
      结果：仍然提示迁移警告
    - 最终解决方案：直接使用 Django 的 `run()` 函数启动服务器
      ```python
      from django.core.servers.basehttp import run
      from django.core.wsgi import get_wsgi_application
      
      wsgi_handler = get_wsgi_application()
      run(addr=(args.host, int(args.port)), wsgi_handler)
      ```
      结果：完全绕过 manage.py 命令行系统，不进行系统检查，不再提示迁移警告

---

## 📊 项目进度

### 已完成
- ✅ Django REST API 创建（20 个端点，17 个完成）
- ✅ 权限系统实现
- ✅ CORS 配置（端口 24610）
- ✅ API 测试脚本
- ✅ 文档完善
- ✅ SessionAuthentication 自定义（禁用 CSRF）
- ✅ Vue 前端页面实现（10 个核心页面）
- ✅ Vue API 层创建（6 个 API 模块）
- ✅ Admin 模块全局组件提取（2026-02-11）
  - 创建 2 个 composables (useStatusConfig, useTableSort)
  - 创建 4 个可复用组件 (LoadingSpinner, StatsCard, EmptyState, StatusBadge)
  - 创建共享样式文件 admin-components.css
  - 重构 AdminDashboard.vue (减少 ~80 行)
  - 重构 AdminEntries.vue (减少 ~100 行)
  - 重构 AdminUsers.vue (减少 ~400 行)

### 进行中
- ⏳ Django API 测试和调试
- ⏳ 前端 Pinia Store 创建
- ⏳ 前端路由重构（/main → /manage）

### 待完成
- ⏳ 发布功能实现
- ⏳ 管理功能实现
- ⏳ 前端完全对接 Django API
- ⏳ Flask 完全替代

---

## 🎯 待办事项

### 高优先级
- [ ] 测试 Django API 所有端点
- [ ] 修复登录 API 的 500 错误
- [ ] 创建 Pinia Store（认证）
- [ ] 实现路由守卫
- [ ] 重构前端路由

### 中优先级
- [ ] 实现发布功能
- [ ] 实现管理功能
- [ ] 优化 API 性能

### 低优先级
- [ ] 添加 API 文档（Swagger）
- [ ] 添加单元测试
- [ ] 优化错误处理

### 已完成
- ✅ Django REST API 创建（20 个端点）
- ✅ Django 启动脚本修复
- ✅ Django API 登录接口修复（SerializerMethodField）
- ✅ Django API CSRF 问题处理（Claude Code）
- ✅ SessionAuthentication 自定义实现（禁用 CSRF）
- ✅ CORS 和 CSRF 端口配置修正（5173 → 24610）
- ✅ Flask → Vue 迁移（部分）
- ✅ 发布 API 重构（2026-02-15）
  - 创建独立的导出服务层 `ExportService`
  - 新增 4 个导出端点：`/api/v1/export/*`
  - 删除 9 个旧端点，合并 PDF 生成
  - 增强 `ContentListAPIView` 支持发布相关查询
  - 更新前端 API 层和组件
  - 端点数从 10 减少到 6（净减少 4 个）
  - 设计原则：内容查询、发布、导出完全分离

---

## 📞 联系信息

- **用户名：** winnower / w1nn0w3r
- **公司花名：** 欧帕斯 (oupasi/ops)
- **时区：** Asia/Shanghai

---

## 💬 交流习惯

### "cc" 的含义
- 当用户说 "cc" 或 "让 cc 来做" 时，指的是 **Claude Code**
- Claude Code 可以被视为：
  - Clawdbot 的**朋友/同事**（平等的协作关系）
  - Clawdbot 的**下属/工具**（执行具体任务）
- 根据上下文灵活理解，保持友好合作的态度

### 2026-02-09

12. **路由守卫逻辑优化** ✅ 已完成
**时间：** 2026-02-09
**问题：** 已登录用户访问登录/注册页时，强制跳转到 `/manage` 不合理
**原因：**
  - 普通用户（role: 0）没有管理页权限，会看到 403
  - 用户可能只是想回到首页，不是要访问管理页
**修正：**
  - `guestOnly` 路由守卫改为跳转到 `/`（首页）而不是 `/manage`
  - 已登录用户访问 `/login` 或 `/register` → 跳转到首页
  - 首页有管理入口按钮，用户可以选择是否进入管理页
**优势：**
  - 体验更流畅（普通用户不会看到 403）
  - 逻辑更合理（已登录用户访问登录页 → 回到首页）
  - 仍然可以通过首页的"管理入口"按钮进入管理页

11. **Django API Review 权限修正** ✅ 已完成
