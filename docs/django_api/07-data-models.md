# 数据模型

数据库表结构和字段说明。

---

## 📋 数据库表概览

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| user_info | 用户信息 | id, username, password_MD5, role |
| content_management | 内容管理 | id, title, content, status, type |
| comment_management | 评论管理 | id, comment, creator_id, news_id |
| django_session | Django 会话 | session_key, session_data, expire_date |

---

## 1. 用户表 (user_info)

存储用户账号和权限信息。

### 表结构

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PRIMARY KEY | 用户唯一标识 |
| username | CharField(30) | UNIQUE, NOT NULL | 登录用户名 |
| password_MD5 | CharField(100) | NOT NULL | MD5 哈希密码 |
| realname | CharField(30) | NOT NULL | 真实姓名 |
| student_id | CharField(30) | NOT NULL | 学号 |
| avatar | CharField(100) | | 头像图片文件名 |
| role | PositiveIntegerField | DEFAULT 0 | 权限位（位掩码） |
| created_at | DateTimeField | AUTO_NOW_ADD | 账号创建时间 |
| updated_at | DateTimeField | AUTO_NOW | 最后更新时间 |
| last_login | DateTimeField | NULLABLE | 最后登录时间 |

### 索引

| 索引名 | 字段 | 类型 |
|--------|------|------|
| idx_user_created_at | created_at | 索引 |
| idx_user_updated_at | updated_at | 索引 |
| idx_user_student_id | student_id | 索引 |
| idx_user_realname | realname | 索引 |
| ( UNIQUE 约束 ) | username | 唯一索引 |

### 权限系统

**权限位定义**:

| 权限值 | 二进制 | 名称 | has_editor_perm | has_admin_perm |
|--------|--------|------|-----------------|----------------|
| 0 | `0b00` | 普通用户 | false | false |
| 1 | `0b01` | 编辑 | true | false |
| 2 | `0b10` | 管理员 | false | true |
| 3 | `0b11` | 超级管理员 | true | true |

**权限检查**:

```python
# 编辑权限检查
user.has_editor_permission()  # 等同于: user.role & 0b01 != 0

# 管理员权限检查
user.has_admin_permission()  # 等同于: user.role & 0b10 != 0

# 属性访问
user.has_editor_perm  # True/False
user.has_admin_perm   # True/False
```

**权限组合示例**:

```python
# 添加编辑权限
new_role = user.role | 0b01  # 位或操作

# 移除管理员权限
new_role = user.role & ~0b10  # 位与非操作

# 检查是否有编辑权限
has_editor = (user.role & 0b01) != 0
```

### Model 方法

```python
class User_info(models.Model):
    @property
    def is_active(self):
        """用户是否激活（所有用户都激活）"""
        return True

    @property
    def is_staff(self):
        """是否可以访问 admin（管理员可以）"""
        return self.has_admin_permission()

    @property
    def is_authenticated(self):
        """是否已认证（用于 Django 认证系统）"""
        return True

    def has_editor_permission(self):
        """检查是否有编辑权限"""
        return bool(self.role & self.PERMISSION_EDITOR)

    def has_admin_permission(self):
        """检查是否有管理员权限"""
        return bool(self.role & self.PERMISSION_ADMIN)

    def has_permission(self, required_permission):
        """检查是否有指定权限"""
        return bool(self.role & required_permission)
```

### 示例数据

```sql
INSERT INTO user_info (username, password_MD5, realname, student_id, role) VALUES
('admin', MD5('admin'), '管理员', 'admin001', 3),
('editor1', MD5('123456'), '编辑一', '2021001', 1),
('user1', MD5('123456'), '用户一', '2021002', 0);
```

---

## 2. 内容表 (content_management)

存储新闻、通知、公告等内容。

### 表结构

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PRIMARY KEY | 内容唯一标识 |
| creator_id | IntegerField | NOT NULL | 创建者用户 ID |
| describer_id | IntegerField | NULLABLE | 描述者用户 ID |
| reviewer_id | IntegerField | NULLABLE | 审核者用户 ID |
| title | CharField(200) | NOT NULL | 内容标题 |
| short_title | CharField(100) | NULLABLE | 短标题（展示用） |
| content | TextField | NOT NULL | 详细内容 |
| link | TextField | NOT NULL | 外部链接 |
| type | CharField(50) | NOT NULL | 内容类型 |
| tag | TextField | DEFAULT '' | 内容标签 |
| deadline | DateTimeField | NULLABLE | 截止时间 |
| image_list | TextField | DEFAULT '[]' | 图片列表（JSON） |
| status | CharField(50) | DEFAULT 'draft' | 内容状态 |
| publish_at | DateTimeField | NULLABLE | 发布时间 |
| locker_id | IntegerField | NULLABLE | 锁定者用户 ID |
| locked_at | DateTimeField | NULLABLE | 锁定时间 |
| created_at | DateTimeField | AUTO_NOW_ADD | 创建时间 |
| updated_at | DateTimeField | AUTO_NOW | 更新时间 |

### 索引

| 索引名 | 字段 | 类型 |
|--------|------|------|
| idx_content_creator_id | creator_id | 索引 |
| idx_content_describer_id | describer_id | 索引 |
| idx_content_reviewer_id | reviewer_id | 索引 |
| idx_content_status | status | 索引 |
| idx_content_type | type | 索引 |
| idx_content_deadline | deadline | 索引 |
| idx_content_publish_at | publish_at | 索引 |
| idx_content_created_at | created_at | 索引 |
| idx_content_updated_at | updated_at | 索引 |

### 内容状态

| 状态值 | 说明 | 可执行操作 |
|--------|------|-----------|
| draft | 草稿 | 修改、描述、删除 |
| pending | 待审核 | 审核、撤回、取消 |
| reviewed | 已审核 | 发布、撤回 |
| rejected | 已拒绝 | 修改、撤回、取消 |
| published | 已发布 | 取消发布 |
| terminated | 已终止 | 无 |

### 内容类型

| 类型值 | 说明 |
|--------|------|
| 教务 | 教务处相关通知 |
| 竞赛 | 学科竞赛信息 |
| 活动 | 校园活动 |
| 讲座 | 讲座信息 |
| 其他 | 其他类型 |

### 三人协作机制

每条内容涉及三个用户角色：

| 角色 | 字段 | 说明 |
|------|------|------|
| 创建者 | creator_id | 内容的创建人 |
| 描述者 | describer_id | 补充详细信息的人 |
| 审核者 | reviewer_id | 审核/批准的人 |

**工作流**:
1. 创建者创建内容（status=draft）
2. 描述者补充详情（status=pending）
3. 审核者审核（status=reviewed/rejected）
4. 管理员发布（status=published）

### 图片列表格式

**字段**: `image_list` (TextField)

**格式**: JSON 数组字符串

```json
["uploads/image1.jpg", "uploads/image2.jpg"]
```

**示例**:

```python
# 添加图片
content = Content.objects.get(id=1)
content.add_image('uploads/photo.jpg')

# 读取图片
import json
images = json.loads(content.image_list)
# ['uploads/image1.jpg', 'uploads/image2.jpg']
```

### 并发锁定机制

**锁定字段**:
- `locker_id`: 正在编辑的用户 ID
- `locked_at`: 锁定时间

**用途**: 防止多个用户同时编辑同一条内容

**使用示例**:

```python
# 检查是否被锁定
if content.locker_id and content.locker_id != current_user.id:
    raise Exception("内容正在被其他用户编辑")

# 锁定内容
content.locker_id = current_user.id
content.locked_at = datetime.now()
content.save()

# 解锁内容
content.locker_id = None
content.locked_at = None
content.save()
```

### Model 属性

```python
class Content(models.Model):
    @property
    def creator_username(self):
        """创建者用户名"""
        try:
            user = User_info.objects.get(id=self.creator_id)
            return user.username
        except User_info.DoesNotExist:
            return ''

    @property
    def describer_username(self):
        """描述者用户名"""
        try:
            user = User_info.objects.get(id=self.describer_id)
            return user.username
        except User_info.DoesNotExist:
            return ''

    @property
    def reviewer_username(self):
        """审核者用户名"""
        try:
            user = User_info.objects.get(id=self.reviewer_id)
            return user.username
        except User_info.DoesNotExist:
            return ''
```

---

## 3. 评论表 (comment_management)

存储用户对内容的评论。

### 表结构

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PRIMARY KEY | 评论唯一标识 |
| comment | TextField | NOT NULL | 评论内容 |
| creator_id | IntegerField | NOT NULL | 评论创建者 ID |
| news_id | IntegerField | NOT NULL | 关联的内容 ID |
| parent_comment_id | IntegerField | NULLABLE | 父评论 ID（NULL=顶层评论） |
| created | DateTimeField | AUTO_NOW_ADD | 创建时间 |
| updated | DateTimeField | AUTO_NOW | 更新时间 |

### 索引

| 索引名 | 字段 | 类型 |
|--------|------|------|
| idx_creator_id | creator_id | 索引 |
| idx_news_id | news_id | 索引 |
| idx_parent_comment_id | parent_comment_id | 索引 |
| idx_created | created | 索引 |
| idx_updated | updated | 索引 |

### 评论层级结构

**支持回复功能**（通过 `parent_comment_id`）:

```
顶层评论 (parent_comment_id=NULL)
  ├─ 子评论 1 (parent_comment_id=1)
  ├─ 子评论 2 (parent_comment_id=2)
  │   └─ 孙评论 (parent_comment_id=3)
  └─ 子评论 3 (parent_comment_id=4)
```

**查询示例**:

```python
# 查询某内容的所有顶层评论
top_level = Comment.objects.filter(news_id=10, parent_comment_id=None)

# 查询某评论的所有子评论
replies = Comment.objects.filter(parent_comment_id=5)

# 查询某用户的所有评论
user_comments = Comment.objects.filter(creator_id=1)
```

---

## 4. Django 会话表 (django_session)

Django 框架自带的会话表。

### 表结构

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| session_key | CharField(40) | PRIMARY KEY | Session ID |
| session_data | TextField | NOT NULL | Session 数据（base64 编码） |
| expire_date | DateTimeField | NOT NULL | 过期时间 |

### Session 数据格式

**编码**: Base64 + Pickle

**数据结构**:
```python
{
    '_auth_user_id': '1',  # 用户 ID
    '_auth_user_backend': 'django.contrib.auth.backends.ModelBackend',
    '_auth_user_hash': 'abc123...'
}
```

**过期时间**: 默认 2 周（可在配置中修改）

---

## 🔗 表关系

### ER 图

```
user_info (用户表)
    ↓ 1:N
content_management (内容表)
    ↑ 1:N
    │
comment_management (评论表)

django_session (会话表)
    ↓ N:1
user_info
```

### 外键关系（逻辑）

虽然数据库中没有物理外键约束，但通过逻辑关联：

| 表 | 字段 | 关联表 | 说明 |
|----|------|--------|------|
| content_management | creator_id | user_info.id | 创建者 |
| content_management | describer_id | user_info.id | 描述者 |
| content_management | reviewer_id | user_info.id | 审核者 |
| comment_management | creator_id | user_info.id | 评论者 |
| comment_management | news_id | content_management.id | 关联内容 |
| comment_management | parent_comment_id | comment_management.id | 父评论 |

---

## 📊 数据库统计

### 表大小估算

| 表名 | 单条记录估算 | 1000 条记录 |
|------|-------------|-------------|
| user_info | ~500 bytes | ~500 KB |
| content_management | ~2 KB | ~2 MB |
| comment_management | ~500 bytes | ~500 KB |
| django_session | ~1 KB | ~1 MB |

### 索引建议

**高查询频率字段**:
- `content.status` - 用于过滤不同状态的内容
- `content.type` - 用于按类型查询
- `content.created_at` - 用于时间排序
- `user.role` - 用于权限过滤

**复合索引示例**:
```sql
CREATE INDEX idx_content_status_created ON content_management(status, created_at DESC);
CREATE INDEX idx_content_type_status ON content_management(type, status);
```

---

## ⚠️ 数据库注意事项

### 1. 密码安全

**当前**: MD5 哈希（不安全）

**建议升级**:
```python
# 使用 bcrypt 或 Argon2
import bcrypt

password = "user_password".encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
```

### 2. 字符编码

**字符集**: `utf8mb4`

**排序规则**: `utf8mb4_unicode_ci`

**原因**: 支持emoji和特殊字符

### 3. 时间字段

**时区**: 使用 UTC 时间

**格式**: ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)

**示例**:
```python
from django.utils import timezone
now = timezone.now()  # 当前 UTC 时间
```

### 4. 软删除建议

**当前**: 不支持软删除

**建议**: 添加 `is_deleted` 字段

```python
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True
```

---

## 🔗 相关文档

- [认证 API - 用户注册](./01-auth.md#用户注册)
- [内容管理 API - 创建内容](./02-content.md#创建内容)
- [用户管理 API - 权限系统](./04-user-management.md#权限系统详解)
- [错误码 - 权限错误](./06-error-codes.md#权限错误-403)
