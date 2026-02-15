# 错误码说明

API 返回的 HTTP 状态码和业务错误码的完整说明。

---

## 📋 HTTP 状态码

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功（无返回内容） |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未登录或登录过期 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如用户名已存在） |
| 500 | Internal Server Error | 服务器内部错误 |

---

## 🔐 认证错误 (401)

### 未登录

**状态码**: `401 Unauthorized`

**场景**: 用户未登录访问受保护的资源

**响应示例**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**常见原因**:
- 未调用登录接口
- Session 已过期
- Cookie 未正确发送

**解决方案**:
```javascript
// 1. 调用登录接口
await authAPI.login('username', 'password')

// 2. 确保 axios 配置了 withCredentials
axios.defaults.withCredentials = true

// 3. 检查响应拦截器是否正确处理 401
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 跳转到登录页
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

---

## 🚫 权限错误 (403)

### 无编辑权限

**状态码**: `403 Forbidden`

**场景**: 普通用户尝试创建/编辑内容

**响应示例**:
```json
{
  "success": false,
  "message": "需要编辑权限",
  "code": "permission_denied"
}
```

**权限要求对照表**:

| 操作 | 需要的权限 | 权限检查 |
|------|-----------|----------|
| 创建内容 | 编辑权限 | `user.role & 0b01 != 0` |
| 审核内容 | 编辑权限 | `user.role & 0b01 != 0` |
| 发布内容 | 编辑权限 | `user.role & 0b01 != 0` |
| 管理用户 | 管理员权限 | `user.role & 0b10 != 0` |
| 编辑角色 | 管理员权限 | `user.role & 0b10 != 0` |

### 不能审核自己的内容

**状态码**: `403 Forbidden`

**场景**: 用户尝试审核自己创建的内容

**响应示例**:
```json
{
  "success": false,
  "message": "不能审核自己的内容",
  "code": "permission_denied"
}
```

### 不能修改自己的角色

**状态码**: `403 Forbidden`

**场景**: 管理员尝试修改自己的角色

**响应示例**:
```json
{
  "success": false,
  "message": "不能修改自己的角色",
  "code": "permission_denied"
}
```

---

## 📝 请求参数错误 (400)

### 缺少必填参数

**状态码**: `400 Bad Request`

**场景**: 请求缺少必填字段

**响应示例**:
```json
{
  "success": false,
  "message": "缺少必填参数：title",
  "code": "validation_error"
}
```

**常见缺失参数**:

| 端点 | 必填参数 | 示例 |
|------|---------|------|
| POST /api/auth/register/ | username, password, realname, student_id | 注册 |
| POST /api/auth/login/ | username, password | 登录 |
| POST /api/content/ | title, content, link, type | 创建内容 |
| POST /api/publish/ | content_ids | 批量发布 |
| POST /api/upload/ | upload_type | 文件上传 |

### 参数格式错误

**状态码**: `400 Bad Request`

**场景**: 参数类型或格式不正确

**响应示例**:
```json
{
  "success": false,
  "message": "密码长度不能少于6位",
  "code": "validation_error"
}
```

**常见格式错误**:

| 参数 | 错误格式 | 正确格式 |
|------|---------|---------|
| password | 5位 | 至少6位 |
| deadline | 2026/02/15 | 2026-02-15T23:59:59Z |
| content_ids | "1,2,3" | [1, 2, 3] |
| role | "0b01" | 1 |
| date | 02-15 | 2026-02-15 |

### 密码验证错误

**状态码**: `400 Bad Request`

**场景**: 原密码错误

**响应示例**:
```json
{
  "success": false,
  "message": "原密码错误",
  "code": "validation_error"
}
```

**解决方案**:
- 确认输入的原密码正确
- 检查密码是否正确加密（MD5）

### 内容状态错误

**状态码**: `400 Bad Request`

**场景**: 内容状态不允许该操作

**响应示例**:
```json
{
  "success": false,
  "message": "状态为 draft，不能发布",
  "code": "validation_error"
}
```

**状态转换规则**:

| 操作 | 允许的起始状态 | 目标状态 |
|------|--------------|---------|
| 发布 | reviewed | published |
| 取消发布 | published | reviewed |
| 审核 | pending | reviewed/rejected |
| 撤回 | published/reviewed/pending | draft |
| 取消 | draft/rejected/pending | terminated |

---

## 🔍 资源不存在 (404)

### 内容不存在

**状态码**: `404 Not Found`

**场景**: 访问不存在的内容 ID

**响应示例**:
```json
{
  "success": false,
  "message": "内容不存在",
  "code": "not_found"
}
```

### 用户不存在

**状态码**: `404 Not Found`

**场景**: 访问不存在的用户 ID

**响应示例**:
```json
{
  "success": false,
  "message": "用户不存在",
  "code": "not_found"
}
```

---

## ⚔️ 资源冲突 (409)

### 用户名已存在

**状态码**: `409 Conflict`

**场景**: 注册时用户名重复

**响应示例**:
```json
{
  "success": false,
  "message": "用户名已存在",
  "code": "conflict"
}
```

**解决方案**:
- 更换用户名
- 前端预先检查用户名是否存在

---

## 💥 服务器错误 (500)

### 数据库错误

**状态码**: `500 Internal Server Error`

**场景**: 数据库连接失败或查询错误

**响应示例**:
```json
{
  "success": false,
  "message": "数据库错误",
  "code": "server_error"
}
```

**常见原因**:
- 数据库服务未启动
- 数据库配置错误
- SQL 语法错误
- 表结构不匹配

### 文件操作错误

**状态码**: `500 Internal Server Error`

**场景**: 文件上传或 PDF 生成失败

**响应示例**:
```json
{
  "success": false,
  "message": "PDF 生成失败",
  "code": "server_error"
}
```

**常见原因**:
- Typst 编译器未安装
- 字体文件缺失
- 磁盘空间不足
- 文件权限问题

---

## 📊 业务错误码

除了 HTTP 状态码，API 还返回业务错误码 (`code` 字段):

| 错误码 | 说明 |
|--------|------|
| `validation_error` | 参数验证失败 |
| `permission_denied` | 权限不足 |
| `not_found` | 资源不存在 |
| `conflict` | 资源冲突 |
| `business_logic_error` | 业务逻辑错误 |
| `server_error` | 服务器内部错误 |

### 业务逻辑错误示例

**状态码**: `400 Bad Request`

**响应示例**:
```json
{
  "success": false,
  "message": "不能修改自己的角色",
  "code": "business_logic_error"
}
```

---

## 🔧 错误处理最佳实践

### 前端统一错误处理

```javascript
// axios 响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    const { status, data } = error.response || {}

    switch (status) {
      case 401:
        // 未登录 - 跳转到登录页
        router.push('/login')
        break

      case 403:
        // 无权限 - 显示提示
        ElMessage.error(data.message || '无权限访问')
        break

      case 404:
        // 资源不存在
        ElMessage.error(data.message || '资源不存在')
        break

      case 400:
        // 参数错误
        ElMessage.error(data.message || '请求参数错误')
        break

      case 500:
        // 服务器错误
        ElMessage.error('服务器错误，请稍后重试')
        break

      default:
        ElMessage.error('网络错误')
    }

    return Promise.reject(error)
  }
)
```

### 后端统一错误处理

```python
# api/core/exceptions.py
class APIException(Exception):
    def __init__(self, message: str, code: str = 'error', status: int = 400):
        self.message = message
        self.code = code
        self.status = status

# 视图中使用
try:
    result = service.do_something()
except APIException as e:
    return Response(
        {'success': False, 'message': e.message, 'code': e.code},
        status=e.status
    )
```

---

## 📝 常见错误排查

### 问题：登录后立即 401

**可能原因**:
1. Cookie 未正确设置
2. CORS 配置错误
3. Session 配置问题

**排查步骤**:
```javascript
// 1. 检查响应头
console.log(response.headers)

// 2. 检查 Cookie
console.log(document.cookie)

// 3. 检查 axios 配置
axios.defaults.withCredentials = true
```

### 问题：403 权限错误

**可能原因**:
1. 用户权限不足
2. Token/Session 过期
3. 权限检查逻辑错误

**排查步骤**:
```python
# 1. 检查用户权限
print(user.role)  # 应该是 1, 2, 或 3
print(user.has_editor_perm)  # 编辑权限
print(user.has_admin_perm)  # 管理员权限

# 2. 检查权限类
permission_classes = [IsAuthenticated, IsEditorOrAdmin]
```

### 问题：400 参数错误

**可能原因**:
1. 参数类型错误
2. 必填参数缺失
3. 参数格式不正确

**排查步骤**:
```python
# 1. 打印请求数据
print(request.data)

# 2. 验证参数
serializer = MySerializer(data=request.data)
if not serializer.is_valid():
    print(serializer.errors)
```

---

## 🔗 相关文档

- [数据模型 - 权限系统](./07-data-models.md#权限系统)
- [认证 API - 登录](./01-auth.md#登录)
- [用户管理 - 权限说明](./04-user-management.md#权限系统详解)
