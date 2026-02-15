# 认证相关 API

提供用户登录、注册、登出、用户信息获取和密码管理功能。

---

## 📋 端点列表

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/auth/register/` | POST | ❌ | 用户注册 |
| `/api/auth/login/` | POST | ❌ | 用户登录 |
| `/api/auth/logout/` | POST | ✅ | 用户登出 |
| `/api/auth/user/` | GET | ✅ | 获取当前用户信息 |
| `/api/auth/password/` | POST | ✅ | 修改密码 |

---

## 1. 用户注册

创建新用户账号。

### 请求

**端点**: `POST /api/auth/register/`

**Content-Type**: `application/x-www-form-urlencoded` 或 `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ✅ | 用户名（唯一，最多30字符） |
| password | string | ✅ | 密码（最少6位） |
| realname | string | ✅ | 真实姓名 |
| student_id | string | ✅ | 学号 |

**请求示例**:

```bash
curl -X POST http://localhost:42611/api/auth/register/ \
  -d "username=testuser&password=123456&realname=张三&student_id=123456"
```

```javascript
// 使用 fetch
fetch('http://localhost:42611/api/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // 携带 cookie
  body: JSON.stringify({
    username: 'testuser',
    password: '123456',
    realname: '张三',
    student_id: '123456'
  })
})
```

### 响应

**成功响应** (201 Created):
```json
{
  "id": 1,
  "username": "testuser",
  "realname": "张三",
  "student_id": "123456",
  "avatar": "",
  "has_editor_perm": false,
  "has_admin_perm": false,
  "created_at": "2026-02-15T12:00:00Z"
}
```

**错误响应**:
- `400 Bad Request` - 参数验证失败
  ```json
  {
    "success": false,
    "message": "用户名已存在"
  }
  ```
- `409 Conflict` - 用户名已存在（正确的 RESTful 行为）

---

## 2. 用户登录

使用用户名和密码登录系统。

### 请求

**端点**: `POST /api/auth/login/`

**Content-Type**: `application/x-www-form-urlencoded` 或 `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ✅ | 用户名 |
| password | string | ✅ | 密码 |

**请求示例**:

```bash
curl -X POST http://localhost:42611/api/auth/login/ \
  -d "username=admin&password=admin"
```

```javascript
fetch('http://localhost:42611/api/auth/login/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin'
  })
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "realname": "管理员",
    "student_id": "admin001",
    "avatar": "",
    "has_editor_perm": true,
    "has_admin_perm": true
  }
}
```

**错误响应**:
- `400 Bad Request` - 参数缺失或验证失败
  ```json
  {
    "success": false,
    "message": "用户名或密码错误"
  }
  ```

**说明**:
- 登录成功后，服务器会设置 `sessionid` cookie
- 后续请求会自动携带此 cookie
- Cookie 会自动包含在后续请求中（使用 `credentials: 'include'`）

---

## 3. 获取当前用户信息

获取当前登录用户的详细信息。

### 请求

**端点**: `GET /api/auth/user/`

**认证**: ✅ 需要登录

**请求示例**:

```bash
curl http://localhost:42611/api/auth/user/ \
  --cookie "sessionid=xxx"
```

```javascript
fetch('http://localhost:42611/api/auth/user/', {
  credentials: 'include'  // 自动携带 cookie
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "realname": "管理员",
  "student_id": "admin001",
  "avatar": "",
  "has_editor_perm": true,
  "has_admin_perm": true,
  "created_at": "2026-02-01T00:00:00Z",
  "updated_at": "2026-02-15T12:00:00Z",
  "last_login": "2026-02-15T12:30:00Z"
}
```

**错误响应**:
- `401 Unauthorized` - 未登录
  ```json
  {
    "detail": "Authentication credentials were not provided."
  }
  ```

---

## 4. 修改密码

修改当前用户的密码。

### 请求

**端点**: `POST /api/auth/password/`

**认证**: ✅ 需要登录

**Content-Type**: `application/json`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | ✅ | 原密码 |
| new_password | string | ✅ | 新密码（最少6位） |

**请求示例**:

```javascript
fetch('http://localhost:42611/api/auth/password/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    old_password: 'admin',
    new_password: 'newpass123'
  })
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

**错误响应**:
- `400 Bad Request` - 原密码错误或新密码不符合要求
  ```json
  {
    "success": false,
    "message": "原密码错误"
  }
  ```

---

## 5. 用户登出

登出当前用户并清除 session。

### 请求

**端点**: `POST /api/auth/logout/`

**认证**: ✅ 需要登录

**请求示例**:

```javascript
fetch('http://localhost:42611/api/auth/logout/', {
  method: 'POST',
  credentials: 'include'
})
```

### 响应

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "登出成功"
}
```

---

## 🔐 权限说明

认证 API 的权限要求：

| 端点 | 登录前 | 登录后 |
|------|--------|--------|
| 注册 | ✅ 允许 | ✅ 允许 |
| 登录 | ✅ 允许 | ✅ 允许（重新登录） |
| 登出 | ❌ 拒绝 | ✅ 允许 |
| 获取用户信息 | ❌ 拒绝 | ✅ 允许 |
| 修改密码 | ❌ 拒绝 | ✅ 允许 |

---

## 📝 注意事项

1. **Session 管理**
   - 使用 Django session-based 认证
   - Session 默认有效期为 2 周
   - 前端需要使用 `credentials: 'include'` 自动携带 cookie

2. **密码安全**
   - 密码使用 MD5 哈希存储（生产环境建议使用 bcrypt 或 Argon2）
   - 密码长度最少 6 位
   - 原密码验证确保安全性

3. **用户名限制**
   - 长度：1-30 字符
   - 必须唯一
   - 只能包含字母、数字、下划线

4. **权限系统**
   - API 返回布尔值权限字段，便于前端直接使用
   - `has_editor_perm`: 是否具有编辑权限
   - `has_admin_perm`: 是否具有管理员权限
   - 后端使用位掩码存储（0-3），但前端无需关心内部实现

---

## 🔄 工作流程

### 注册 → 登录流程

```
1. POST /api/auth/register/
   ↓ 创建新用户（默认 role=0）

2. POST /api/auth/login/
   ↓ 验证用户名密码
   ↓ 设置 session cookie

3. GET /api/auth/user/
   ↓ 获取用户信息和权限

4. 使用其他 API
   ↓ 自动携带 session cookie

5. POST /api/auth/logout/
   ↓ 清除 session
```

---

## ⚠️ 错误处理

所有错误响应遵循统一格式：

```json
{
  "success": false,
  "message": "具体错误信息"
}
```

常见错误码：
- `400` - 参数错误
- `401` - 未登录
- `409` - 资源冲突（如用户名已存在）
- `500` - 服务器内部错误
