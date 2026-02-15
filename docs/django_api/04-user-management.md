## 📋 端点列表

| 端点 | 方法 | 认证 | 权限 | 说明 |
|------|------|------|------|
| `/api/admin/users/` | GET | ✅ | 管理员 | 用户列表 |
| `/api/admin/users/<user_id>/role/` | POST | ✅ | 管理员 | 角色编辑 |
| `/api/admin/users/<user_id>/info` | PATCH | ✅ | 登录用户 | 用户信息编辑 |
| `/api/admin/dashboard/` | GET | ✅ | 管理员 | 管理面板数据 |

## 2. 用户列表

获取用户列表，支持分页、排序、搜索、权限筛选。

### 请求

**端点**: `GET /api/admin/users/`

**认证**: ✅ 需要登录

**权限**: 管理员

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|
| page | integer | ❌ | 1 | 页码 |
| page_size | integer | ❌ | 10 | 每页数量（10/20/50/100） |
| status | string | ❌ | - | 内容状态过滤（详见下方状态说明） |
| type | string | ❌ | - | 内容类型过滤（详见下方类型说明） |
| q | string | ❌ | - | 搜索关键词 |
| sort | string | ❌ | updated_at | 排序字段 |
| order | string | ❌ | desc | 排序方向（asc/desc） |

### 请求示例

```bash
# 基础分页
curl "http://localhost:42611/api/admin/users/?page=1&page_size=10" \
  --cookie "sessionid=xxx"

# 按用户状态筛选
curl "http://localhost:42611/api/admin/users/?status=draft" \
  --cookie "sessionid=xxx"

# 按搜索关键词查询
curl "http://localhost:42611/api/admin/users/?q=张三" \
  --cookie "sessionid=xxx"

# 按更新时间降序
curl "http://localhost:42611/api/admin/users/?sort=created_at&order=desc" \
  --cookie "sessionid=xxx"
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
      "username": "user1",
      "realname": "张三",
      "student_id": "123456",
      "role": 1,
      "has_editor_perm": true,
      "has_admin_perm": false,
      "created_at": "2026-01-15T10:00:00Z",
      "formatted_created_at": "01-15 10:00"
    },
    ...
  ]
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 用户 ID |
| `username` | string | 用户名 |
| `realname` | string | 真实姓名 |
| `student_id` | string | 学号 |
| `role` | integer | 角色位值 |
| `has_editor_perm` | boolean | 是否有编辑权限 |
| `has_admin_perm` | boolean | 是否有管理权限 |
| `created_at` | string | 创建时间（ISO 8601） |

## 3. 编辑用户角色

添加或删除用户的编辑权限。

### 请求

**端点**: `POST /api/admin/users/<user_id>/role/`

**认证**: ✅ 需要登录

**权限**: 管理员

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | ✅ | 操作类型：`add`（添加）或 `remove`（删除） |
| permission | string | ✅ | 权限类型：`editor`（编辑权限）或 `admin`（管理权限） |

**请求示例**:

```javascript
// 添加编辑权限
fetch('http://localhost:42611/api/admin/users/5/role/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    action: 'add',
    permission: 'editor'
  })
})
```

```javascript
// 删除编辑权限
fetch('http://localhost:42611/api/admin/users/5/role/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    action: 'remove',
    permission: 'admin'
  })
})
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "user": {
    "id": 5,
    "username": "user5",
    "realname": "张三",
    "student_id": "123456",
    "role": 3,  // 新角色值（1 | 0b01 → 3）
    "has_editor_perm": true,
    "has_admin_perm": false
  },
  "message": "角色更新成功"
}
```

### 说明

- `action`: `add` - 添加权限，`remove` - 删除权限
- `permission`: `editor` - 编辑权限（位掩码 0b01），`admin` - 管理权限（位掩码 0b10）
- 操作后角色值更新：新角色值 = 原角色值 | 权限位

## 4. 编辑用户信息

修改用户的基本信息（真实姓名、学号、密码）。

### 请求

**端点**: `PATCH /api/admin/users/<user_id>/info/`

**认证**: ✅ 需要登录

**权限**: 管理员（可以编辑任何人）、其他用户（可编辑自己的基本信息）、普通用户（只能编辑自己的密码）

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必 必填 | 说明 |
|------|------|------|------|
| realname | string | ❌ | 真实姓名 |
| student_id | string | ❌ | 学号 |
| password | string | ❌ | 新密码（最少6位） |

### 请求示例

**编辑基本信息（管理员）**:
```javascript
fetch('http://localhost:42611/api/admin/users/5/info', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    realname: "张三",
    student_id: "123456"
  })
})
```

**修改密码（管理员或本人）**:
```javascript
fetch('http://localhost:42611/api/admin/users/5/', {
  method: 'PATCH',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    password: "newpass123"
  })
})
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "user": {
    "id": 5,
    "username": "user5",
    "realname": "张三",
    "student_id": "123456",
    "role": 3,
    "has_editor_perm": true,
    "has_admin_perm": false
  },
  "message": "用户信息更新成功"
}
```

### 错误响应

- `403 Forbidden` - 无权限（非管理员且非本人）
- `404 Not Found` - 用户不存在
- `400 Bad Request` - 参数验证失败

## 5. 管理面板数据

获取管理面板的统计数据。

### 请求

**端点**: `GET /api/admin/dashboard/`

**认证**: ✅ 需要登录

**权限**: 管理员

### 请求示例

```bash
curl http://localhost:42611/api/admin/dashboard/ \
  --cookie "sessionid=xxx"
```

### 响应

**成功响应** (200 OK):

```json
{
  "success": true,
  "stats": {
    "total_users": 100,
    "total_contents": 500,
    "pending_reviews": 50,
    "published_today": 10
  }
}
```
