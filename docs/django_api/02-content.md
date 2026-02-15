# 内容管理 API

提供内容的创建、查询、更新、删除、审核、撤回等功能。

---

## 📋 端点列表

| 端点 | 方法 | 认证 | 权限 | 说明 |
|------|------|------|------|------|
| `/api/contents/` | GET | ✅ | 登录用户 | 获取内容列表（权限动态控制） |
| `/api/content/create/` | POST | ✅ | 编辑+ | 创建内容 |
| `/api/content/<id>/` | GET | ✅ | 登录用户 | 获取内容详情 |
| `/api/content/<id>/modify/` | PATCH | ✅ | 创建者/管理员 | 更新内容 |
| `/api/content/<id>/submit/` | POST | ✅ | 编辑+ | 提交审核（纯状态转换） |
| `/api/content/<id>/review/` | POST | ✅ | 编辑+ | 审核内容 |
| `/api/content/<id>/recall/` | POST | ✅ | 创建者/管理员 | 撤回内容 |
| `/api/content/<id>/cancel/` | POST | ✅ | 创建者/管理员 | 取消内容 |
| `/api/content/<id>/admin_status/` | POST | ✅ | 管理员 | 强制修改状态（无流转限制） |

---

## 1. 获取内容列表

获取内容列表，支持分页、搜索、排序和状态过滤。

**权限动态控制**:

| 用户角色 | 可见状态 | 说明 |
|----------|----------|------|
| 管理员 | 所有状态 | 包括 `terminated`（已终止）状态 |
| 普通用户 | 活跃状态 | 仅 `draft`, `pending`, `reviewed`, `rejected`, `published` |

- 管理员可以查看所有内容，包括已终止的历史记录
- 普通用户只能查看活跃状态的内容，自动过滤已终止的内容
- 使用查询参数可进一步过滤状态

### 请求

**端点**: `GET /api/contents/`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | ❌ | 1 | 页码 |
| page_size | integer | ❌ | 10 | 每页数量（10/20/50/100） |
| status | string | ❌ | - | 内容状态过滤（详见下方状态说明） |
| type | string | ❌ | - | 内容类型过滤（详见下方类型说明） |
| q | string | ❌ | - | 搜索关键词 |
| sort | string | ❌ | updated_at | 排序字段（id, created_at, updated_at, deadline, title, publish_at） |
| order | string | ❌ | desc | 排序方向（asc/desc） |

**发布相关查询参数**:
| publish_start_date | string | ❌ | - | 发布日期范围开始（YYYY-MM-DD） |
| publish_end_date | string | ❌ | - | 发布日期范围结束（YYYY-MM-DD） |
| deadline_end_date | string | ❌ | - | DDL 查询（返回截止日期之后未到期的内容） |
| only_published | boolean | ❌ | false | 只返回已发布内容（true/false） |

**使用场景**:
```bash
# 按发布日期范围查询已发布内容
GET /api/contents/?publish_start_date=2026-02-10&publish_end_date=2026-02-15&only_published=true

# 查询 DDL 内容（截止日期之后）
GET /api/contents/?deadline_end_date=2026-02-15&only_published=true
```

**状态参数 (status) 说明**:

| 状态值 | 显示名称 | 说明 |
|--------|---------|------|
| `draft` | 草稿 | 初始创建状态，仅创建者可见 |
| `pending` | 待审核 | 已提交审核，等待审核者处理 |
| `reviewed` | 已审核 | 审核通过，等待发布 |
| `rejected` | 已拒绝 | 审核未通过，需要修改后重新提交 |
| `published` | 已发布 | 已正式发布，公开可见 |
| `terminated` | 已终止 | 已终止，不再有效 |

**类型参数 (type) 说明**:

| 类型值 | 说明 | 适用场景 |
|--------|------|----------|
| `教务` | 教务处相关通知 | 课程、考试、成绩、选课等教务信息 |
| `竞赛` | 学科竞赛信息 | 各类学科竞赛、比赛通知 |
| `活动` | 校园活动 | 校园活动、文体活动等 |
| `讲座` | 讲座信息 | 学术讲座、报告会等 |
| `其他` | 其他类型 | 不属于上述分类的其他内容 |

**多值过滤支持**:

`status` 和 `type` 参数都支持**多个值**的查询，使用逗号分隔：

```bash
# 查询多个状态
?status=draft,pending,rejected

# 查询多个类型
?type=教务,竞赛,讲座

# 组合多个过滤条件
?status=published&type=教务,竞赛
```

| 场景 | 查询参数 | 说明 |
|------|---------|------|
| 工作队列 | `?status=draft,pending,rejected` | 查看所有未完成的内容 |
| 已发布通知 | `?status=published&type=教务,竞赛` | 已发布的教务和竞赛信息 |
| 活动日历 | `?type=活动,讲座&status=published` | 显示已发布的活动和讲座 |
| 待处理项 | `?status=pending&sort=created_at&order=asc` | 按创建时间排序的待审核内容 |

**请求示例**:

```bash
# 基础分页
curl "http://localhost:42611/api/contents/?page=1&page_size=10"

# 按状态过滤 - 获取已发布的内容
curl "http://localhost:42611/api/contents/?status=published"

# 按类型过滤 - 获取教务类型的内容
curl "http://localhost:42611/api/contents/?type=教务"

# 多值过滤 - 获取多个状态的内容（草稿、待审核、被拒绝）
curl "http://localhost:42611/api/contents/?status=draft,pending,rejected"

# 多值类型过滤 - 获取教务、竞赛、讲座类型的内容
curl "http://localhost:42611/api/contents/?type=教务,竞赛,讲座"

# 组合过滤 - 获取待审核的教务和竞赛通知
curl "http://localhost:42611/api/contents/?status=pending&type=教务,竞赛"

# 搜索关键词 - 搜索包含"考试"的内容
curl "http://localhost:42611/api/contents/?q=考试"

# 排序 - 按创建时间升序排列
curl "http://localhost:42611/api/contents/?sort=created_at&order=asc"

# 复杂查询 - 搜索已发布的活动和讲座，按截止时间排序
curl "http://localhost:42611/api/contents/?status=published&type=活动,讲座&sort=deadline&order=asc"
```

```javascript
// JavaScript 使用示例
// 获取工作队列：所有未完成的内容
fetch('http://localhost:42611/api/contents/?status=draft,pending,rejected&page=1&page_size=50', {
  credentials: 'include'
})

// 获取需要处理的待审核内容
fetch('http://localhost:42611/api/contents/?status=pending&sort=created_at&order=asc', {
  credentials: 'include'
})

// 获取已发布的通知和竞赛
fetch('http://localhost:42611/api/contents/?status=published&type=教务,竞赛&sort=publish_at&order=desc', {
  credentials: 'include'
})

// 获取所有待审核的内容（跨页获取）
async function getPendingContents() {
  let page = 1
  let allResults = []

  while (true) {
    const response = await fetch(`http://localhost:42611/api/contents/?status=pending&page=${page}&page_size=50`, {
      credentials: 'include'
    })
    const data = await response.json()

    allResults.push(...data.results)

    // 如果结果少于 page_size，说明已经是最后一页
    if (data.results.length < 50) break

    page++
  }

  return allResults
}

// 获取工作台内容（草稿 + 待审核 + 被拒绝）
async function getWorkQueueContents() {
  const response = await fetch('http://localhost:42611/api/contents/?status=draft,pending,rejected&page_size=100', {
    credentials: 'include'
  })
  const data = await response.json()
  return data.results
}
```

### 响应

**成功响应** (200 OK):
```json
{
  "count": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10,
  "results": [
    {
      "id": 1,
      "title": "教务处通知",
      "short_title": "教务通知",
      "content": "具体内容...",
      "link": "http://example.com",
      "type": "教务",
      "tag_list": ["重要", "紧急"],
      "deadline": "2026-12-31T23:59:59Z",
      "status": "published",
      "status_display": "已发布",
      "creator_id": 1,
      "creator_username": "admin",
      "describer_id": 2,
      "describer_username": "editor1",
      "reviewer_id": 3,
      "reviewer_username": "admin",
      "publish_at": "2026-02-15T12:00:00Z",
      "created_at": "2026-02-15T10:00:00Z",
      "formatted_created_at": "02-15 10:00",
      "updated_at": "2026-02-15T12:00:00Z",
      "formatted_updated_at": "02-15 12:00",
      "can_delete": true
    }
  ]
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `tag_list` | array | 标签数组（JSON 数组格式），前端直接使用即可 |

**注意**: 响应中只返回 `tag_list`（数组格式），不包含原始的 `tag` 字符串字段。数据库层面只存储一个字段（tag，JSON 字符串），序列化器自动转换为数组格式返回。

**前端使用建议**:

```javascript
// ✅ 直接使用 tag_list（已解析的数组）
content.tag_list.forEach(tag => {
  console.log(tag)
})

// 标签展示
function renderTags(content) {
  return content.tag_list.map(tag =>
    `<span class="tag">${tag}</span>`
  ).join('')
}

// 标签编辑（发送时使用数组格式）
async function updateTags(contentId, newTags) {
  await fetch(`/api/content/${contentId}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tag: newTags  // 直接发送数组: ["标签1", "标签2"]
    })
  })
}
```

---

## 2. 获取内容详情

获取单个内容的详细信息。

### 请求

**端点**: `GET /api/content/<id>/`

**认证**: ✅ 需要登录
**权限**: 所有登录用户

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | ✅ | 内容 ID |

**请求示例**:

```bash
# 获取 ID 为 1 的内容详情
curl "http://localhost:42611/api/content/1/"
```

```javascript
// JavaScript 使用示例
fetch('http://localhost:42611/api/content/1/', {
  credentials: 'include'
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "id": 1,
  "title": "教务处通知",
  "short_title": "教务通知",
  "content": "具体内容...",
  "link": "http://example.com",
  "type": "教务",
  "tag_list": ["重要", "紧急"],
  "deadline": "2026-12-31T23:59:59Z",
  "status": "published",
  "status_display": "已发布",
  "creator_id": 1,
  "creator_username": "admin",
  "describer_id": 2,
  "describer_username": "editor1",
  "reviewer_id": 3,
  "reviewer_username": "admin",
  "publish_at": "2026-02-15T12:00:00Z",
  "created_at": "2026-02-15T10:00:00Z",
  "formatted_created_at": "02-15 10:00",
  "updated_at": "2026-02-15T12:00:00Z",
  "formatted_updated_at": "02-15 12:00",
  "can_delete": true
}
```

---

## 3. 创建内容

创建新内容。

### 请求

**端点**: `POST /api/content/create/`

**认证**: ✅ 需要登录
**权限**: 编辑权限（role & 0b01 != 0）

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | ✅ | 内容标题（最多200字符） |
| short_title | string | ❌ | 短标题（用于展示，最多100字符） |
| content | string | ✅ | 详细内容 |
| link | string | ✅ | 内容链接地址 |
| type | string | ✅ | 内容类型（见下方类型说明） |
| tag | string/array | ❌ | 内容标签（支持字符串或数组，详见下方） |
| deadline | string | ❌ | 截止时间（ISO 8601 格式） |
| image_list | string | ❌ | 图片列表（JSON 数组字符串） |

**标签 (tag) 参数说明**:

`tag` 字段支持两种格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| **字符串（逗号分隔）** | `"重要,紧急,教务"` | 多个标签用逗号分隔，会自动转换为数组 |
| **JSON 数组** | `["重要", "紧急", "教务"]` | 直接发送数组格式 |
| **空值** | `""` 或 `[]` | 无标签 |

**请求示例**：

```javascript
// 方式 1：字符串格式
{
  "title": "教务通知",
  "content": "具体内容...",
  "type": "教务",
  "tag": "重要,紧急"  // 逗号分隔的字符串
}

// 方式 2：数组格式（推荐）
{
  "title": "教务通知",
  "content": "具体内容...",
  "type": "教务",
  "tag": ["重要", "紧急"]  // JSON 数组
}

// 方式 3：无标签
{
  "title": "教务通知",
  "content": "具体内容...",
  "type": "教务"
  // tag 字段可选，不填表示无标签
}
```

**内容类型 (type) 可选值**:

| 类型值 | 说明 | 典型示例 |
|--------|------|----------|
| `教务` | 教务处相关通知 | 课程调整、考试安排、选课通知 |
| `竞赛` | 学科竞赛信息 | 数学竞赛、编程比赛、学科竞赛 |
| `活动` | 校园活动 | 文体活动、社团招新、校园庆典 |
| `讲座` | 讲座信息 | 学术讲座、名家论坛、报告会 |
| `其他` | 其他类型 | 不属于上述分类的其他内容 |

**请求示例**:

```javascript
// 示例 1：单个标签（字符串）
fetch('http://localhost:42611/api/content/create/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: "教务处重要通知",
    short_title: "教务通知",
    content: "关于下学期选课的通知...",
    link: "http://jwc.seu.edu.cn/notice",
    type: "教务",
    tag: "重要",
    deadline: "2026-12-31T23:59:59Z"
  })
})

// 示例 2：多个标签（数组格式，推荐）
fetch('http://localhost:42611/api/content/create/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: "竞赛报名通知",
    content: "全国大学生数学建模竞赛报名...",
    link: "https://example.com",
    type: "竞赛",
    tag: ["数学", "重要", "报名中"],
    deadline: "2026-03-15T23:59:59Z"
  })
})

// 示例 3：多个标签（逗号分隔字符串）
fetch('http://localhost:42611/api/content/create/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: "学术讲座通知",
    content: "人工智能前沿技术讲座...",
    link: "https://example.com",
    type: "讲座",
    tag: "AI,机器学习,学术讲座",  // 逗号分隔
    deadline: "2026-02-20T18:00:00Z"
  })
})
```

### 响应

**成功响应** (201 Created):
```json
{
  "id": 10,
  "title": "教务处重要通知",
  "short_title": "教务通知",
  "content": "关于下学期选课的通知...",
  "link": "http://jwc.seu.edu.cn/notice",
  "type": "教务",
  "tag_list": ["重要", "紧急"],
  "deadline": "2026-12-31T23:59:59Z",
  "status": "draft",
  "creator_id": 1,
  "describer_id": 1,
  "created_at": "2026-02-15T13:00:00Z"
}
```

**内容状态**:
- `draft` - 草稿
- `pending` - 待审核
- `reviewed` - 已审核
- `rejected` - 已拒绝
- `published` - 已发布
- `terminated` - 已终止

---

## 4. 更新内容

更新已有内容的字段。

### 请求

**端点**: `PATCH /api/content/<id>/modify/`

**认证**: ✅ 需要登录
**权限**: 内容创建者或管理员

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | ❌ | 内容标题（最多200字符） |
| short_title | string | ❌ | 短标题（用于展示，最多100字符） |
| content | string | ❌ | 详细内容 |
| link | string | ❌ | 内容链接地址 |
| type | string | ❌ | 内容类型（见下方类型说明） |
| tag | string/array | ❌ | 内容标签（支持字符串或数组） |
| deadline | string | ❌ | 截止时间（ISO 8601 格式） |
| image_list | string | ❌ | 图片列表（JSON 数组字符串） |

**允许更新的字段**:

只能更新以下字段，其他字段（如 id, creator_id, status 等）将被忽略：
- `title`
- `short_title`
- `content`
- `link`
- `type`
- `tag`
- `deadline`
- `image_list`

**状态限制**:

只能更新以下状态的内容：
- `draft` - 草稿状态
- `rejected` - 已拒绝状态

其他状态（pending, reviewed, published, terminated）的内容不允许更新。

**标签 (tag) 参数说明**:

`tag` 字段支持两种格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| **字符串（逗号分隔）** | `"重要,紧急,教务"` | 多个标签用逗号分隔，会自动转换为数组 |
| **JSON 数组** | `["重要", "紧急", "教务"]` | 直接发送数组格式 |
| **空值** | `""` 或 `[]` | 清除标签 |

**权限说明**:

| 用户角色 | 可更新内容 |
|----------|----------|
| 创建者 | ✅ 仅自己创建的内容 |
| 管理员 | ✅ 任何内容 |
| 其他编辑者 | ❌ 无权限（除非是管理员） |

**请求示例**:

```javascript
// 示例 1：更新单个字段（标题）
fetch('http://localhost:42611/api/content/1/0', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: "更新后的标题"
  })
})
```

```javascript
// 示例 2：更新多个字段
fetch('http://localhost:42611/api/content/1/0', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: "教务处通知",
    short_title: "教务通知",
    content: "关于下学期选课的通知...",
    link: "http://jwc.seu.edu.cn/notice"
  })
})
```

```javascript
// 示例 3：更新标签（数组格式，推荐）
fetch('http://localhost:42611/api/content/1/0', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tag: ["重要", "紧急", "教务"]  // JSON 数组
  })
})
```

```javascript
// 示例 4：更新标签（逗号分隔字符串）
fetch('http://localhost:42611/api/content/1/0', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tag: "重要,紧急,教务"  // 逗号分隔
  })
})
```

```javascript
// 示例 5：清空标签
fetch('http://localhost:42611/api/content/1/0', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tag: []  // 或 tag: ""
  })
})
```

```javascript
// 示例 6：更新内容类型和截止时间
fetch('http://localhost:42611/api/content/1/0', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    type: "竞赛",
    deadline: "2026-12-31T23:59:59Z"
  })
})
```

### 响应

**成功响应** (200 OK): 返回更新后的内容对象

```json
{
  "id": 10,
  "title": "更新后的标题",
  "short_title": "短标题",
  "content": "详细内容...",
  "link": "http://example.com",
  "type": "教务",
  "tag_list": ["重要", "紧急"],
  "deadline": "2026-12-31T23:59:59Z",
  "status": "draft",
  "status_display": "草稿",
  "creator_id": 1,
  "describer_id": 1,
  "creator_username": "admin",
  "describer_username": "admin",
  "reviewer_id": null,
  "reviewer_username": "",
  "publish_at": null,
  "created_at": "2026-02-15T10:00:00Z",
  "formatted_created_at": "02-15 10:00",
  "updated_at": "2026-02-15T12:00:00Z",
  "formatted_updated_at": "02-15 12:00"
}
```

**字段更新说明**:

响应中的 `tag_list` 字段会自动根据输入的 `tag` 参数转换：
- 输入字符串 `"重要,紧急"` → 输出数组 `["重要", "紧急"]`
- 输入数组 `["重要", "紧急"]` → 输出数组 `["重要", "紧急"]`
- 输入空值 `""` 或 `[]` → 输出空数组 `[]`

**错误响应**:

```json
{
  "success": false,
  "message": "只有内容创建者或管理员可以修改"
}
```

**错误码说明**:

| HTTP 状态 | 错误类型 | 说明 |
|----------|---------|------|
| 403 Forbidden | 无权限 | 非创建者且非管理员 |
| 404 Not Found | 内容不存在 | 指定的 id 不存在 |
| 400 Bad Request | 状态不允许 | 当前状态不允许修改（非 draft 或 rejected） |

### 注意事项

1. **PUT vs PATCH**
   - `PUT`: 替换整个资源（需要所有字段）
   - `PATCH`: 部分更新（只需修改的字段）
   - 推荐使用 `PATCH` 进行部分更新

2. **状态限制**
   - 只能更新 `draft` 和 `rejected` 状态的内容
   - 已发布或待审核的内容需要先撤回才能修改
   - 尝试更新其他状态会返回 400 错误

3. **权限检查**
   - 创建者只能更新自己的内容
   - 管理员可以更新任何内容
   - 其他编辑者无权限更新（除非是管理员）

4. **标签处理**
   - 前端发送时可以使用字符串或数组格式
   - 后端自动转换为 JSON 数组存储
   - 响应统一返回 `tag_list` 数组格式
   - 不需要前端手动解析 JSON

5. **字段验证**
   - `title`: 最多200字符
   - `short_title`: 最多100字符
   - `type`: 必须是有效类型（教务/竞赛/活动/讲座/其他）
   - `deadline`: 必须是有效的 ISO 8601 日期时间格式

6. **并发更新**
   - 多个用户同时更新同一内容时，最后提交的更新生效
   - 前端建议使用乐观锁或版本控制

7. **自动字段**
   - `updated_at` 字段会自动更新为当前时间
   - `status` 不会自动改变（保持在 draft/rejected）

### 使用场景

**场景 1：编辑草稿并保存**

```javascript
// 用户编辑内容后自动保存
await autoSave(contentId, {
  title: newTitle,
  content: newContent
})
```

**场景 2：修改被拒绝的内容**

```javascript
// 审核拒绝后，根据反馈修改
await fixRejectedContent(contentId, {
  content: fixedContent,
  tag: ["已修改", "重新提交"]
})
```

**场景 3：批量更新多个字段**

```javascript
// 一次性更新标题、标签、截止时间
await updateContentMetadata(contentId, {
  short_title: "简称",
  tag: ["重要", "竞赛"],
  deadline: "2026-12-31T23:59:59Z"
})
```

**场景 4：清空标签**

```javascript
// 删除所有标签
await clearTags(contentId, {
  tag: []
})
```

---

## 5. 提交审核（纯状态转换）

将草稿内容提交审核，仅改变状态，不修改内容字段。

### 请求

**端点**: `POST /api/content/<id>/submit/`

**认证**: ✅ 需要登录
**权限**: 编辑权限（role & 0b01 != 0）

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| (无) | - | ❌ | 请求体为空 |

**说明**:
- 内容状态从 `draft` 变为 `pending`
- **不修改 describer_id**（提交者 ≠ 描述者）
- **不修改内容字段**（title, content, type 等）
- 纯状态转换操作，职责清晰

**请求示例**:

```javascript
// 提交审核（无需传递内容数据）
fetch('http://localhost:42611/api/content/1/0submit/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({})  // 空请求体
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "提交审核成功"
}
```

**错误响应**:
- `403 Forbidden` - 无编辑权限
- `404 Not Found` - 内容不存在
- `400 Bad Request` - 当前状态不允许提交（非 draft 状态）

### 设计理念

**submitter（提交者） vs describer（描述者）**

| 角色 | 说明 |
|------|------|
| submitter | 执行"提交审核"操作的人（点击提交按钮的用户） |
| describer | 实际描述/编辑内容详情的人 |
| creator | 创建内容的原始作者 |

**关键差异**:

| 端点 | describer_id 操作 | 状态转换 | 响应内容 |
|------|-----------------|-----------|---------|
| `POST /content/<id>/submit/` | **不修改** | draft → pending | 仅返回 success + message |
| `POST /content/<id>/modify/` | **设为调用者** | draft → pending | 返回完整内容对象 |

**使用场景**:

```javascript
// ✅ 场景 1：纯提交（推荐用于职责分离）
await fetch(`/api/content/${id}/submit/`, { method: 'POST' })
// 适用场景：别人编辑了内容，我来提交审核

// ✅ 场景 2：描述并提交（原方式，已废弃）
await fetch(`/api/content/${id}/modify/`, {
  method: 'POST',
  body: JSON.stringify({ title: '新标题', content: '新内容' })
})
// 适用场景：我编辑了内容并提交审核
```

---

## 6. 审核内容

审核内容（通过或拒绝）。

### 请求

**端点**: `POST /api/content/<id>/review/`

**认证**: ✅ 需要登录
**权限**: 编辑权限，不能审核自己的内容

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| approved | boolean | ✅ | true=通过，false=拒绝 |
| comment | string | ❌ | 审核意见 |

**请求示例**:

```javascript
fetch('http://localhost:42611/api/content/1/0review/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    approved: true,
    comment: "内容完整，可以发布"
  })
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "审核完成"
}
```

**内容状态变化**:
- 通过：`pending` → `reviewed`
- 拒绝：`pending` → `rejected`

---

## 7. 撤回内容

将已发布/已审核的内容撤回到草稿状态。

### 请求

**端点**: `POST /api/content/<id>/recall/`

**认证**: ✅ 需要登录
**权限**: 内容创建者或管理员

**说明**:
- 适用状态：`published`, `reviewed`, `pending`
- 撤回后状态变为 `draft`
- 清除 `reviewer_id`

---

## 8. 取消内容

取消内容（终止流程）。

### 请求

**端点**: `POST /api/content/<id>/cancel/`

**认证**: ✅ 需要登录
**权限**: 内容创建者或管理员

**说明**:
- 适用状态：除 `published` 和 `terminated` 外的所有状态
- 取消后状态变为 `terminated`

---

## 9. 管理员强制修改状态

超级管理员强制修改内容状态为任意有效值，不受常规状态流转规则限制。

### 请求

**端点**: `POST /api/content/<id>/admin_status/`

**认证**: ✅ 需要登录
**权限**: 管理员（role >= 2）

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | ✅ | 新状态值（见下方状态说明） |
| reason | string | ❌ | 状态变更原因（用于审计） |

**有效状态值**:

| 状态值 | 说明 |
|--------|------|
| `draft` | 草稿 |
| `pending` | 待审核 |
| `reviewed` | 已审核 |
| `rejected` | 已拒绝 |
| `published` | 已发布 |
| `terminated` | 已终止 |

**设计说明**:
- 此端点不受常规状态流转规则限制，可任意设置状态
- 仅管理员（role >= 2）可使用
- 所有操作会被记录审计日志
- 用于应急处理和特殊情况

**请求示例**:

```javascript
// 示例 1：直接将草稿发布
fetch('http://localhost:42611/api/content/1/admin_status/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    status: "published",
    reason: "紧急发布，跳过审核流程"
  })
})
```

```javascript
// 示例 2：将已发布内容撤回并标记为草稿
fetch('http://localhost:42611/api/content/1/admin_status/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    status: "draft",
    reason: "内容需要重新编辑"
  })
})
```

```javascript
// 示例 3：强制终止错误发布的内容
fetch('http://localhost:42611/api/content/1/admin_status/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    status: "terminated",
    reason: "发现严重错误，立即终止"
  })
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "状态已强制更新",
  "data": {
    "id": 1,
    "title": "教务处通知",
    "short_title": "教务通知",
    "content": "具体内容...",
    "link": "http://example.com",
    "type": "教务",
    "tag_list": ["重要", "紧急"],
    "deadline": "2026-12-31T23:59:59Z",
    "status": "published",
    "status_display": "已发布",
    "creator_id": 1,
    "creator_username": "admin",
    "describer_id": 2,
    "describer_username": "editor1",
    "reviewer_id": null,
    "reviewer_username": "",
    "publish_at": "2026-02-15T12:00:00Z",
    "created_at": "2026-02-15T10:00:00Z",
    "formatted_created_at": "02-15 10:00",
    "updated_at": "2026-02-15T12:00:00Z",
    "formatted_updated_at": "02-15 12:00",
    "can_delete": true
  }
}
```

**错误响应**:

```json
{
  "success": false,
  "message": "只有超级管理员可以强制修改内容状态"
}
```

```json
{
  "success": false,
  "message": "缺少必需参数: status"
}
```

```json
{
  "success": false,
  "message": "无效的状态值，必须是: draft, pending, reviewed, rejected, published, terminated"
}
```

**错误码说明**:

| HTTP 状态 | 错误类型 | 说明 |
|----------|---------|------|
| 403 Forbidden | 无权限 | 非管理员（role < 2） |
| 404 Not Found | 内容不存在 | 指定的 id 不存在 |
| 400 Bad Request | 参数错误 | 缺少 status 参数或状态值无效 |

### 使用场景

**场景 1：紧急发布**

当内容需要立即发布，来不及走正常审核流程时：

```javascript
await emergencyPublish(contentId, {
  status: "published",
  reason: "紧急通知，需要立即发布"
})
```

**场景 2：撤回已发布内容**

当已发布的内容需要撤回修改，但普通撤回流程有问题时：

```javascript
await forceRecall(contentId, {
  status: "draft",
  reason: "内容有误，需要重新编辑"
})
```

**场景 3：终止错误内容**

当发现已发布的内容有严重错误，需要立即终止：

```javascript
await forceTerminate(contentId, {
  status: "terminated",
  reason: "发现严重错误，立即终止"
})
```

**场景 4：状态修复**

当内容状态出现异常，无法通过正常流程修正时：

```javascript
await fixStatus(contentId, {
  status: "reviewed",
  reason: "修复状态异常"
})
```

### 注意事项

1. **权限严格限制**
   - 仅管理员（role >= 2）可使用
   - 所有操作都会被记录审计日志

2. **审计追踪**
   - 记录操作者用户名
   - 记录旧状态和新状态
   - 记录状态变更原因
   - 日志级别为 INFO

3. **状态验证**
   - 严格验证状态值是否在有效范围内
   - 防止无效状态写入数据库
   - 提供 clear 的错误提示

4. **向后兼容**
   - 不影响现有端点和状态流转逻辑
   - 仅作为紧急情况下的备用方案
   - 常规操作仍应使用标准流程

5. **审计日志示例**

```
INFO - 超级管理员强制修改状态: content_id=1, old_status=pending, new_status=published, admin=winnower, reason=紧急发布，跳过审核流程
INFO - 超级管理员强制修改状态: content_id=2, old_status=published, new_status=terminated, admin=winnower, reason=发现严重错误，立即终止
INFO - 超级管理员强制修改状态: content_id=3, old_status=rejected, new_status=draft, admin=winnower, reason=修复状态异常
```

---

```
创建 → draft
  ↓ 提交审核（纯状态转换）
待审核 → pending
  ↓ 审核通过
已审核 → reviewed
  ↓ 发布
已发布 → published

任何阶段都可以撤回到 draft（创建者/管理员）

⚠️ 管理员可以通过 /admin_status/ 端点强制修改为任意状态
```

---

### 关键操作对比

| 操作 | 端点 | describer_id 操作 | 状态转换 | 响应类型 | 用途 |
|------|------|-----------------|-----------|---------|------|
| 更新内容 | `PATCH /content/<id>/` | 不变 | 不变 | 完整对象 | 修改内容数据 |
| 提交审核 | `POST /content/<id>/submit/` | **不变** | draft → pending | success + message | 纯状态转换 |
| 描述内容 | `POST /content/<id>/modify/` | **设为调用者** | draft → pending | 完整对象 | 描述并提交 |
| 审核内容 | `POST /content/<id>/review/` | 不变 | pending → reviewed/rejected | success + message | 审核通过/拒绝 |
| 撤回内容 | `POST /content/<id>/recall/` | 不变 | 任意状态 → draft | 完整对象 | 撤回到草稿 |
| 取消内容 | `POST /content/<id>/cancel/` | 不变 | 任意状态 → terminated | success + message | 终止内容 |
| **强制修改状态** | `POST /content/<id>/admin_status/` | 不变 | **任意状态 → 任意状态** | success + data + message | 管理员强制修改 |

### 设计原则

**职责分离**: 内容更新和状态提交完全分离
- 如需"修改并提交"，前端应分两步调用：先 PATCH 更新内容，再 POST /submit/ 提交审核
- 不提供原子操作端点（一个请求同时修改和提交）

---

## 📊 查询和过滤

### 状态过滤

```bash
# 只看草稿
GET /api/content/?status=draft

# 只看已发布
GET /api/content/?status=published

# 只看待审核
GET /api/content/?status=pending
```

### 类型过滤

```bash
# 只看教务
GET /api/content/?type=教务

# 只看竞赛
GET /api/content/?type=竞赛

# 只看讲座
GET /api/content/?type=讲座
```

### 组合查询

```bash
# 获取待审核的教务通知
GET /api/content/?status=pending&type=教务

# 获取已发布的讲座信息，按时间排序
GET /api/content/?status=published&type=讲座&sort=deadline&order=asc

# 搜索包含"考试"的教务内容
GET /api/content/?type=教务&q=考试

# 获取所有草稿状态的竞赛信息
GET /api/content/?status=draft&type=竞赛&page_size=50

# 🔥 多状态组合 - 获取所有未完成的内容
GET /api/content/?status=draft,pending,rejected

# 🔥 多类型组合 - 获取所有通知类内容
GET /api/content/?type=教务,竞赛&status=published

# 🔥 复杂组合 - 获取待处理的活动和讲座
GET /api/content/?status=pending&type=活动,讲座&sort=created_at&order=asc

# 🔥 工作台视图 - 获取需要用户处理的所有内容
GET /api/content/?status=draft,pending,rejected&page_size=100
```

### 搜索

```bash
# 搜索标题或内容
GET /api/content/?q=通知

# 搜索特定类型的内容
GET /api/content/?type=讲座&q=人工智能

# 搜索待审核的内容
GET /api/content/?status=pending&q=紧急
```

### 排序

```bash
# 按更新时间降序（最新优先）
GET /api/content/?sort=updated_at&order=desc

# 按创建时间升序（最早优先）
GET /api/content/?sort=created_at&order=asc

# 按截止时间升序（最紧急优先）
GET /api/content/?sort=deadline&order=asc

# 按标题字母排序
GET /api/content/?sort=title&order=asc
```

---

## 📖 过滤参数使用指南

### 状态 (status) 使用场景

| 使用场景 | 推荐状态值 | 说明 |
|---------|-----------|------|
| 编辑查看自己的草稿 | `draft` | 查看未完成的内容 |
| 审核者处理待审核内容 | `pending` | 需要审核的内容队列 |
| 管理员发布内容 | `reviewed` | 审核通过待发布的内容 |
| 前台展示 | `published` | 已正式发布的公开内容 |
| 重新编辑被拒绝内容 | `rejected` | 审核未通过需修改的内容 |
| 归档查询 | `terminated` | 已终止的历史内容 |
| **🔥 工作台视图** | `draft,pending,rejected` | 所有需要处理的内容 |
| **🔥 审核队列** | `pending,rejected` | 待审核和被拒绝的内容 |

### 类型 (type) 使用场景

| 页面/场景 | 推荐类型过滤 | 说明 |
|----------|-------------|------|
| 教务通知页面 | `type=教务` | 仅显示教务相关通知 |
| 竞赛信息页面 | `type=竞赛` | 仅显示竞赛相关信息 |
| 讲座日历页面 | `type=讲座&status=published` | 显示已发布的讲座 |
| 活动预告页面 | `type=活动&sort=deadline&order=asc` | 按截止时间排序的活动 |
| 全部内容页面 | 不指定 type | 显示所有类型内容 |
| **🔥 通知中心** | `type=教务,竞赛,讲座` | 所有通知类内容 |
| **🔥 活动日历** | `type=活动,讲座&status=published` | 显示活动和讲座 |

### 实用查询示例

#### 场景 1：内容管理者的工作台（使用多值过滤）

```javascript
// ✅ 推荐：使用多值过滤一次获取所有工作项
const workQueue = await fetch('/api/contents/?status=draft,pending,rejected&page_size=100')

// ❌ 不推荐：多次请求
const pendingReviews = await fetch('/api/contents/?status=pending')
const rejectedItems = await fetch('/api/contents/?status=rejected')
const draftItems = await fetch('/api/contents/?status=draft')
```

#### 场景 2：教务通知专员

```javascript
// 查看所有教务相关的待审核内容
const教务Pending = await fetch('/api/contents/?type=教务&status=pending')

// 查看已发布的教务通知
const教务Published = await fetch('/api/contents/?type=教务&status=published&sort=publish_at&order=desc')
```

#### 场景 3：竞赛信息管理员

```javascript
// 查看所有竞赛信息，按截止时间排序（紧急优先）
const竞赛ByDeadline = await fetch('/api/contents/?type=竞赛&sort=deadline&order=asc')

// 查找即将截止的竞赛（7天内）
const today = new Date()
const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
const upcoming = await fetch(`/api/content/?type=竞赛&status=published&deadline_gte=${today.toISOString()}&deadline_lte=${nextWeek.toISOString()}`)
```

#### 场景 4：前台公开内容展示

```javascript
// 获取最新的已发布内容
const latestPublished = await fetch('/api/contents/?status=published&sort=updated_at&order=desc&page_size=10')

// 获取不同类型的已发布内容
const getPublishedByType = async (type) => {
  return await fetch(`/api/content/?status=published&type=${type}&sort=publish_at&order=desc`)
}

// 使用示例
const 教务通知 = await getPublishedByType('教务')
const 竞赛信息 = await getPublishedByType('竞赛')
const 讲座信息 = await getPublishedByType('讲座')
```

---

## ⚠️ 注意事项

1. **并发编辑保护**
   - `locker_id` 和 `locked_at` 字段用于防止并发编辑
   - 编辑时建议使用乐观锁

2. **三人协作机制**
   - `creator_id`: 内容创建者
   - `describer_id`: 内容描述者（补充详情）
   - `reviewer_id`: 内容审核者（批准/拒绝）

3. **状态转换规则**
   - 只能修改 `draft` 和 `rejected` 状态的内容
   - 已发布的内容可以撤回但不能直接修改

4. **软删除**
   - 删除操作是永久性的，无法恢复
   - 如需"删除"但不真正删除，使用 `cancel` 操作

5. **端点废弃说明**
   - `/content/<id>/modify/` 已废弃，建议使用 `/content/<id>/submit/`
   - `modify/` 同时修改 describer_id 和状态，职责不清晰
   - `submit/` 只改变状态，不修改 describer_id 和内容字段
   - 前端调用 `modifyEntry()` 时会收到 deprecation 警告

---

## 🏷️ 标签 (tag) 使用指南

### 标签格式支持

`tag` 字段支持灵活的输入格式，系统会自动统一处理：

| 输入格式 | 示例 | 存储格式 | 返回的 tag_list |
|---------|------|---------|----------------|
| 空值 | `""` 或 `null` 或不传 | `"[]"` | `[]` |
| 单个字符串 | `"重要"` | `"[\"重要\"]"` | `["重要"]` |
| 逗号分隔字符串 | `"重要,紧急"` | `"[\"重要\",\"紧急\"]"` | `["重要", "紧急"]` |
| JSON 数组 | `["标签1", "标签2"]` | `"[\"标签1\",\"标签2\"]"` | `["标签1", "标签2"]` |

### 前端使用建议

**推荐做法**：
```javascript
// ✅ 创建时使用数组格式
const createContent = async () => {
  await fetch('/api/content/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: '标题',
      content: '内容',
      type: '教务',
      tag: ['重要', '紧急']  // 推荐使用数组
    })
  })
}

// ✅ 展示时使用 tag_list（已解析）
const renderTags = (content) => {
  return content.tag_list.map(tag =>
    `<span class="tag">${tag}</span>`
  ).join('')
}

// ✅ 更新时也使用数组
const updateTags = async (contentId, newTags) => {
  await fetch(`/api/content/${contentId}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tag: newTags  // 直接传数组
    })
  })
}
```

**不推荐的做法**：
```javascript
// ❌ 不要手动拼接字符串（发送时直接传数组即可）
const tagString = tags.join(',')  // 不推荐，直接传数组
```

### 标签管理场景

#### 场景 1：标签输入组件

```javascript
// 使用标签输入框（支持添加/删除标签）
<template>
  <div class="tag-input">
    <span v-for="tag in tags" :key="tag" class="tag">
      {{ tag }}
      <button @click="removeTag(tag)">×</button>
    </span>
    <input
      v-model="newTag"
      @keyup.enter="addTag"
      placeholder="输入标签后按回车"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const tags = ref([])
const newTag = ref('')

const addTag = () => {
  if (newTag.value && !tags.value.includes(newTag.value)) {
    tags.value.push(newTag.value)
    newTag.value = ''
  }
}

const removeTag = (tag) => {
  tags.value = tags.value.filter(t => t !== tag)
}

// 保存时直接发送数组
const saveContent = async () => {
  await fetch('/api/content/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: '标题',
      content: '内容',
      type: '教务',
      tag: tags.value  // 直接发送数组
    })
  })
}
</script>
```

#### 场景 2：标签筛选

```javascript
// 前端根据标签筛选内容
const filterByTag = async (tagName) => {
  const response = await fetch('/api/content/')
  const data = await response.json()

  // 筛选包含特定标签的内容
  const filtered = data.results.filter(content =>
    content.tag_list.includes(tagName)
  )

  return filtered
}

// 获取所有使用过的标签（去重）
const getAllTags = async () => {
  const response = await fetch('/api/contents/?page_size=100')
  const data = await response.json()

  const allTags = new Set()
  data.results.forEach(content => {
    content.tag_list.forEach(tag => allTags.add(tag))
  })

  return Array.from(allTags)
}
```

#### 场景 3：标签统计

```javascript
// 统计每个标签的使用次数
const getTagStats = async () => {
  const response = await fetch('/api/contents/?page_size=100')
  const data = await response.json()

  const stats = {}
  data.results.forEach(content => {
    content.tag_list.forEach(tag => {
      stats[tag] = (stats[tag] || 0) + 1
    })
  })

  return stats
  // 结果: { "重要": 15, "紧急": 8, "教务": 20 }
}

// 标签云展示
const renderTagCloud = () => {
  const stats = await getTagStats()

  return Object.entries(stats)
    .sort((a, b) => b[1] - a[1])  // 按使用次数排序
    .map(([tag, count]) =>
      `<span class="tag-cloud-item" style="font-size: ${12 + count}px">${tag} (${count})</span>`
    )
    .join('')
}
```

### 标签最佳实践

1. **标签数量**
   - 建议每个内容添加 1-5 个标签
   - 过多标签会影响展示效果

2. **标签命名**
   - 使用简洁明了的词语
   - 避免特殊字符和空格
   - 推荐使用：重要、紧急、教务、竞赛、报名中等

3. **标签分类**
   - 优先级：重要、紧急、一般
   - 状态：报名中、已截止、进行中
   - 类型：课程、考试、活动、讲座

4. **性能考虑**
   - 前端使用 `tag_list` 而不是解析 `tag`
   - 标签筛选在前端进行（小数据量）
   - 大数据量时考虑后端实现标签过滤 API
