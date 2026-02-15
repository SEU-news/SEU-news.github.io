# 文件和工具 API

提供文件上传、内容搜索、预览等功能。

---

## 📋 端点列表

| 端点 | 方法 | 认证 | 权限 | 说明 |
|------|------|------|------|------|
| `/api/upload/` | POST | ✅ | 编辑+ | 统一上传接口（文本/URL/图片） |
| `/api/search/` | POST | ✅ | 所有用户 | 内容搜索 |
| `/api/preview/` | POST | ✅ | 编辑+ | 预览编辑 |

---

## 1. 统一上传接口

统一的上传接口，支持三种上传类型：纯文本消息、URL 粘贴、图片上传。

### 请求

**端点**: `POST /api/upload/`

**认证**: ✅ 需要登录
**权限**: 编辑权限

**Content-Type**: `multipart/form-data`（图片上传）或 `application/json`（文本/URL）

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| upload_type | string | ✅ | 上传类型：`text`/`url`/`image` |

**不同类型的参数**:

#### 1.1 纯文本上传 (upload_type=text)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | ✅ | 内容标题（最多200字符） |
| short_title | string | ❌ | 短标题（最多100字符） |
| content | string | ✅ | 详细内容 |
| link | string | ✅ | 内容链接 |
| type | string | ✅ | 内容类型（教务/竞赛/活动/讲座/其他） |
| tag | string | ❌ | 标签 |
| deadline | string | ❌ | 截止时间（ISO 8601 格式） |
| image_list | string | ❌ | 图片列表（JSON 数组） |

#### 1.2 URL 粘贴 (upload_type=url)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | ✅ | 要粘贴的 URL |

#### 1.3 图片上传 (upload_type=image)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| images | file | ✅ | 图片文件（支持多张） |

**请求示例**:

```javascript
// 1. 纯文本上传
const formData = new FormData()
formData.append('upload_type', 'text')
formData.append('title', '教务处通知')
formData.append('content', '关于选课的通知...')
formData.append('link', 'http://example.com')
formData.append('type', '教务')

fetch('http://localhost:42611/api/upload/', {
  method: 'POST',
  credentials: 'include',
  body: formData
})

// 2. URL 粘贴
fetch('http://localhost:42611/api/upload/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    upload_type: 'url',
    url: 'http://jwc.seu.edu.cn/notice'
  })
})

// 3. 图片上传（多图）
const formData = new FormData()
formData.append('upload_type', 'image')
formData.append('images', file1)  // File 对象
formData.append('images', file2)  // File 对象

fetch('http://localhost:42611/api/upload/', {
  method: 'POST',
  credentials: 'include',
  body: formData
})
```

### 响应

**成功响应** (201 Created):

```json
{
  "id": 10,
  "title": "教务处通知",
  "short_title": "",
  "content": "关于选课的通知...",
  "link": "http://example.com",
  "type": "教务",
  "tag": "",
  "deadline": null,
  "status": "draft",
  "status_display": "草稿",
  "creator_id": 1,
  "creator_username": "admin",
  "describer_id": 1,
  "describer_username": "admin",
  "reviewer_id": null,
  "reviewer_username": "",
  "publish_at": null,
  "created_at": "2026-02-15T12:00:00Z",
  "formatted_created_at": "02-15 12:00",
  "updated_at": "2026-02-15T12:00:00Z",
  "formatted_updated_at": "02-15 12:00",
  "can_delete": true
}
```

**URL 粘贴响应**:

```json
{
  "id": 11,
  "title": "东南大学教务处",
  "short_title": "",
  "content": "",
  "link": "http://jwc.seu.edu.cn/notice",
  "type": "教务",
  "tag": "",
  "deadline": null,
  "status": "draft",
  "status_display": "草稿",
  "creator_id": 1,
  "creator_username": "admin",
  "describer_id": null,
  "describer_username": "",
  "reviewer_id": null,
  "reviewer_username": "",
  "publish_at": null,
  "created_at": "2026-02-15T12:00:00Z",
  "formatted_created_at": "02-15 12:00",
  "updated_at": "2026-02-15T12:00:00Z",
  "formatted_updated_at": "02-15 12:00",
  "can_delete": true
}
```

**图片上传响应**:

```json
{
  "id": 12,
  "title": "图片",
  "short_title": "",
  "content": "",
  "link": "",
  "type": "其他",
  "tag": "",
  "deadline": null,
  "status": "draft",
  "status_display": "草稿",
  "image_list": "[\"uploads/image1.jpg\",\"uploads/image2.jpg\"]",
  "creator_id": 1,
  "creator_username": "admin",
  "describer_id": null,
  "describer_username": "",
  "reviewer_id": null,
  "reviewer_username": "",
  "publish_at": null,
  "created_at": "2026-02-15T12:00:00Z",
  "formatted_created_at": "02-15 12:00",
  "updated_at": "2026-02-15T12:00:00Z",
  "formatted_updated_at": "02-15 12:00",
  "can_delete": true
}
```

**错误响应**:
- `400 Bad Request` - 无效的上传类型或参数错误
  ```json
  {
    "success": false,
    "message": "无效的上传类型"
  }
  ```

**说明**:
- 所有上传类型都会创建新的 Content 记录
- 图片上传支持一次上传多张图片
- URL 粘贴会自动提取网页标题作为内容标题
- 上传的图片保存在 `uploads/` 目录

---

## 2. 内容搜索

搜索内容标题、正文或链接。

### 请求

**端点**: `POST /api/search/`

**认证**: ✅ 需要登录
**权限**: 所有登录用户

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | ❌ | 搜索关键词（为空返回空结果） |

**请求示例**:

```javascript
fetch('http://localhost:42611/api/search/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    q: '教务'
  })
})
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "count": 5,
  "results": [
    {
      "id": 1,
      "title": "教务处通知",
      "short_title": "教务通知",
      "content": "关于选课的通知...",
      "link": "http://jwc.seu.edu.cn/notice",
      "type": "教务",
      "status": "published",
      "status_display": "已发布",
      "creator_id": 1,
      "creator_username": "admin",
      "created_at": "2026-02-15T12:00:00Z",
      "updated_at": "2026-02-15T12:00:00Z"
    }
  ]
}
```

**搜索范围**:
- 标题 (`title`)
- 详细内容 (`content`)
- 链接 (`link`)

**搜索方式**: 不区分大小写的模糊匹配

---

## 3. 预览编辑

预览选中内容的编辑效果（Typst 格式）。

### 请求

**端点**: `POST /api/preview/`

**认证**: ✅ 需要登录
**权限**: 编辑权限

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content_ids | array | ✅ | 内容 ID 列表 |

**请求示例**:

```javascript
fetch('http://localhost:42611/api/preview/', {
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
  "preview": "#title(\"简报\")\n\n= 教务\n\n..."
}
```

**说明**:
- 返回 Typst 格式的文本预览
- 内容按类型分组显示
- 用于生成 PDF 前的预览查看

**错误响应**:
- `400 Bad Request` - 内容不存在或格式错误
  ```json
  {
    "success": false,
    "message": "无法生成预览"
  }
  ```

---

## 📁 文件上传规范

### 支持的文件类型

| 类型 | 格式 | 说明 |
|------|------|------|
| 图片 | jpg, jpeg, png, gif | 常见图片格式 |
| 文本 | - | 通过表单字段提交 |
| URL | http/https | 自动提取标题 |

### 文件存储

**上传目录**: `uploads/`

**文件命名**: `{随机UUID}.{原扩展名}`

**路径格式**: `uploads/{filename}`

**示例**:
```
uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg
```

### 文件大小限制

- 默认：2.5MB（Django 默认）
- 可在 `config/django_config.py` 中配置 `FILE_UPLOAD_MAX_MEMORY_SIZE`

---

## 🔍 搜索功能详解

### 搜索字段

搜索查询会在以下字段中查找匹配：

| 字段 | 说明 | 示例 |
|------|------|------|
| title | 内容标题 | "教务处通知" |
| content | 详细内容 | "关于选课..." |
| link | 外部链接 | "http://jwc.seu.edu.cn" |

### 搜索匹配

- **不区分大小写**: `教务` = `教务` = `JIAOWU`
- **模糊匹配**: `教务` 可以匹配 "教务处通知"
- **部分匹配**: `选课` 可以匹配 "关于选课的通知"

### 搜索示例

```javascript
// 搜索关键词
await searchAPI('教务')  // 搜索包含"教务"的内容

// 空关键词（返回空结果）
await searchAPI('')  // count: 0

// URL 搜索
await searchAPI('jwc.seu.edu.cn')  // 搜索包含此 URL 的内容
```

---

## ⚠️ 注意事项

1. **文件上传安全**
   - 验证文件类型（MIME type）
   - 限制文件大小
   - 使用 UUID 防止文件名冲突
   - 不允许上传可执行文件

2. **图片处理**
   - 支持多图上传（`request.FILES.getlist('images')`）
   - 图片路径保存为 JSON 数组
   - 路径格式：`["uploads/file1.jpg", "uploads/file2.jpg"]`

3. **URL 粘贴**
   - 自动提取网页标题
   - 创建草稿状态的内容
   - 需要后续补充详细信息

4. **搜索性能**
   - 当前使用 `Q()` 对象进行模糊匹配
   - 对于大量数据，建议使用全文搜索引擎（如 Elasticsearch）
   - 可考虑添加数据库索引优化

5. **预览功能**
   - 返回 Typst 源码
   - 不实际编译 PDF
   - 用于快速查看内容格式

---

## 🔗 相关端点

- [内容管理 - 创建内容](./02-content.md#创建内容)
- [内容管理 - 获取内容列表](./02-content.md#获取内容列表)
- [发布管理 - 生成 Typst](./03-publish.md#生成-typst-格式)
