# 发布管理 API

提供内容发布、文档导出等功能。

---

## 📋 端点列表

| 端点 | 方法 | 认证 | 权限 | 说明 |
|------|------|------|------|------|
| 发布管理 | | | | | |
| `/api/publish/` | POST | ✅ | 编辑+ | 批量发布内容 |
| 导出功能 | | | | | |
| `/api/v1/export/pdf/` | POST | ✅ | 编辑+ | 生成 PDF（支持 date 或 content_ids） |
| `/api/v1/export/typst/` | GET | ✅ | 编辑+ | 生成 Typst 格式 |
| `/api/v1/export/latex/` | GET | ✅ | 编辑+ | 生成 LaTeX 格式 |
| `/api/v1/export/data/` | GET | ✅ | 编辑+ | 获取导出数据 |

---

## 1. 批量发布内容

将已审核的内容批量发布。

### 请求

**端点**: `POST /api/publish/`

**认证**: ✅ 需要登录

**权限**: 编辑权限

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content_ids | array | ✅ | 要发布的内容 ID 列表 |

### 请求示例

```javascript
fetch('http://localhost:42611/api/publish/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content_ids: [1, 2, 3, 4, 5]
  })
})
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "updated": 4,
  "failed": [
    {
      "id": 3,
      "reason": "状态为 draft，不能发布"
    }
  ]
}
```

### 说明

- 只有状态为 `reviewed` 的内容可以被发布
- 发布后状态变为 `published`
- 自动设置 `publish_at` 为当前时间
- 返回成功和失败的数量

---

## 2. 生成 PDF

生成 PDF 文件，支持两种模式：按日期生成或按选中内容生成。

### 请求

**端点**: `POST /api/v1/export/pdf/`

**认证**: ✅ 需要登录

**权限**: 编辑权限

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | ❌ | 日期（格式：YYYY-MM-DD） |
| content_ids | array | ❌ | 内容 ID 列表 |

**说明**: `date` 和 `content_ids` 至少提供一个

### 请求示例

**按日期生成**:
```javascript
fetch('http://localhost:42611/api/v1/export/pdf/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    date: '2026-02-15'
  })
})
```

**按选中内容生成**:
```javascript
fetch('http://localhost:42611/api/v1/export/pdf/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content_ids: [1, 2, 3]
  })
})
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "message": "PDF 生成成功",
  "pdf_url": "/static/latest.pdf",
  "pdf_path": "/path/to/latest.pdf",
  "count": 3,
  "due_contents": {
    "other": [...],
    "lecture": [...],
    "college": [...],
    "club": [...]
  }
}
```

**错误响应**:

- `400 Bad Request` - 参数验证失败
- `500 Internal Server Error` - PDF 生成失败

### 说明

- **按日期模式**: 生成指定日期已发布内容的 PDF
- **按内容模式**: 生成指定内容 ID 的 PDF
- 返回 DDL 内容分类结果（用于前端展示）
- PDF 文件保存到 `static/latest.pdf`
- 同时归档到 `archived/YYYY-MM-DD.json` 和 `static/pdfs/YYYY-MM-DD.pdf`

---

## 3. 生成 Typst 格式

生成指定日期内容的 Typst 格式数据。

### 请求

**端点**: `GET /api/v1/export/typst/`

**认证**: ✅ 需要登录

**权限**: 编辑权限

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | ✅ | 日期（格式：YYYY-MM-DD） |

### 请求示例

```bash
curl http://localhost:42611/api/v1/export/typst/?date=2026-02-15 \
  --cookie "sessionid=xxx"
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "date": "2026-02-15",
  "data": {
    "date": "2026-02-15",
    "no": 1,
    "categories": {
      "college": [...],
      "club": [...],
      "lecture": [...],
      "other": [...]
    },
    "ddl_items": [...]
  }
}
```

### 说明

- 生成指定日期已发布内容的 Typst 数据
- 按分类组织内容（college, club, lecture, other）
- 包含未到期的 DDL 内容

---

## 4. 生成 LaTeX 格式

生成指定日期内容的 LaTeX 格式数据。

### 请求

**端点**: `GET /api/v1/export/latex/`

**认证**: ✅ 需要登录

**权限**: 编辑权限

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | ✅ | 日期（格式：YYYY-MM-DD） |

### 请求示例

```bash
curl http://localhost:42611/api/v1/export/latex/?date=2026-02-15 \
  --cookie "sessionid=xxx"
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "date": "2026-02-15",
  "data": {
    "date": "2026-02-15",
    "no": 1,
    "categories": {
      "college": [...],
      "club": [...],
      "lecture": [...],
      "other": [...]
    },
    "ddl_items": [...]
  }
}
```

### 说明

- 生成指定日期已发布内容的 LaTeX 数据
- 按分类组织内容（college, club, lecture, other）
- 包含未到期的 DDL 内容

---

## 5. 获取导出数据

获取指定日期的导出数据（Flask 兼容格式）。

### 请求

**端点**: `GET /api/v1/export/data/`

**认证**: ✅ 需要登录

**权限**: 编辑权限

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | ✅ | 日期（格式：YYYY-MM-DD） |

### 请求示例

```bash
curl http://localhost:42611/api/v1/export/data/?date=2026-02-15 \
  --cookie "sessionid=xxx"
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "date": "2026-02-15",
  "data": {
    "date": "2026-02-15",
    "no": 1,
    "categories": {
      "college": [...],
      "club": [...],
      "lecture": [...],
      "other": [...]
    },
    "ddl_items": [...]
  }
}
```

### 说明

- 返回与 Typst 相同的数据结构
- 用于 Flask 兼容性

---

## 内容查询

发布相关的内容查询已集成到内容管理 API。

### 已发布内容查询

使用 `ContentListAPIView` 的增强查询参数：

```bash
# 按发布日期范围查询
curl "http://localhost:42611/api/content/?publish_start_date=2026-02-10&publish_end_date=2026-02-15&only_published=true&page_size=1000" \
  --cookie "sessionid=xxx"

# 查询 DDL 内容（截止日期之后）
curl "http://localhost:42611/api/content/?deadline_end_date=2026-02-15&only_published=true&page_size=1000" \
  --cookie "sessionid=xxx"
```

### 查询参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| publish_start_date | string | 发布日期范围开始（YYYY-MM-DD） |
| publish_end_date | string | 发布日期范围结束（YYYY-MM-DD） |
| deadline_end_date | string | DDL 结束日期（返回之后未到期的内容） |
| only_published | boolean | 只返回已发布内容（true/false） |
| page | number | 页码 |
| page_size | number | 每页大小（10, 20, 50, 100） |
| sort | string | 排序字段（id, created_at, updated_at, deadline, title, publish_at） |
| order | string | 排序方向（asc/desc） |

---

## PDF 生成流程

```
1. 查询已发布内容
   ↓
2. 选择内容或按日期
   ↓
3. 生成 PDF
   ↓
4. 下载/预览 PDF
```

---

## 📁 文件结构

生成的文件存储在以下位置：

```
static/
├── latest.pdf              # 最新 PDF（随时更新）
├── latest.json             # 最新数据（随时更新）
└── pdfs/
    └── 2026-02-15.pdf   # 归档 PDF（按日期）

archived/
└── 2026-02-15.json       # 归档数据（按日期）
```

---

## 🎨 Typst 模板

PDF 使用 Typst 编译器生成，模板位于 `static/news_template.typ`。

### 模板功能

- 自动分页显示
- 按类型分类展示
- DDL 内容独立区域
- 标题和页码

---

## ⚠️ 重要说明

### 版本控制

- 导出端点使用 `v1` 前缀，便于未来版本升级
- 后续可以创建 `v2` 版本而不影响现有功能

### 权限要求

- 所有导出和发布端点都需要编辑权限（`has_editor_perm`）
- 普通用户无法访问这些功能

### 性能考虑

- PDF 生成可能需要较长时间（10-30秒）
- 建议前端显示加载进度
- 避免重复点击生成按钮

### 旧 API 迁移

以下端点已废弃并删除：

- ~~`POST /api/publish/data/<date>/`~~ - 使用 `GET /api/v1/export/data/`
- ~~`POST /api/publish/pdf/`~~ - 使用 `POST /api/v1/export/pdf/`（参数改为 date）
- ~~`POST /api/publish/pdf_from_selection/`~~ - 使用 `POST /api/v1/export/pdf/`（参数改为 content_ids）
- ~~`GET /api/publish/query/`~~ - 使用 `GET /api/content/` + 查询参数
- ~~`GET /api/publish/query/<date>/`~~ - 使用 `GET /api/content/` + 查询参数
- ~~`GET /api/publish/ddl/`~~ - 使用 `GET /api/content/` + `deadline_end_date` 参数
- ~~`POST /api/publish/unpublish/`~~ - 已移除（前端未使用）

---

## 🔗 相关文档

- [内容管理 API](./02-content.md) - 内容 CRUD 和状态管理
- [文件工具 API](./05-file-utility.md) - 文件上传和预览
- [用户管理 API](./04-user.md) - 用户和权限管理
