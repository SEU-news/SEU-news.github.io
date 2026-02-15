# 阶段 2: django_models/ 基础重构计划

> **目标**: 添加 Manager 和 QuerySet，简化模型层
> **时间**: 1 小时
> **依赖**: 阶段 0（测试基准）

---

## 🎯 重构目标

- [ ] **优先**: 修复数据库字段不一致问题
  - Content 模型添加 `locker_id` 和 `locked_at` 字段
  - Comment 模型修复 `created`/`updated` 字段名
- [ ] 添加自定义 Manager（ContentManager, UserManager, CommentManager）
- [ ] 添加自定义 QuerySet（ContentQuerySet）
- [ ] 保持向后兼容（@property 兼容层）

---

## 📋 任务清单

### 任务 0: 修复数据库字段不一致问题

⚠️ **重要**: 在开始重构前，先修复 models.py 与数据库不一致的问题

#### 修复 Content 模型

**修改**: `django_models/models.py` 的 `Content` 类

在 `tag` 字段后添加：

```python
# 锁定字段（用于并发编辑控制）
locker_id = models.IntegerField(
    verbose_name='当前锁定者用户ID',
    null=True,
    blank=True,
    help_text='正在编辑此内容的用户ID，为空表示未被锁定'
)
locked_at = models.DateTimeField(
    verbose_name='锁定时间',
    null=True,
    blank=True,
    help_text='内容被锁定的时间戳'
)
```

**说明**:
- 这两个字段在数据库中已存在，但 models.py 中缺失
- 添加它们不会破坏现有功能（都是 nullable 字段）
- 可用于未来实现内容锁定功能，防止并发编辑冲突

#### 修复 Comment 模型字段名

**修改**: `django_models/models.py` 的 `Comment` 类

将：
```python
created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
updated_at = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
```

改为：
```python
created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='created')
updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间', db_column='updated')
```

**说明**:
- 数据库字段名是 `created` 和 `updated`
- 使用 `db_column` 参数保持 Python 属性名不变（`created_at`/`updated_at`）
- 这样无需修改所有引用这些字段的代码

**或者（更彻底的方案）**：
直接修改字段名与数据库一致：
```python
created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
```

然后搜索并替换所有引用：
- `created_at` → `created`
- `updated_at` → `updated`

#### 验证步骤
- [ ] 修改 `Content` 模型，添加 `locker_id` 和 `locked_at` 字段
- [ ] 修改 `Comment` 模型，修复 `created`/`updated` 字段名
- [ ] 运行 `python test_api.py` 确保所有测试通过
- [ ] 验证可以正常查询 Comment 的 `created`/`updated` 字段

---

### 任务 1: 创建 django_models/managers.py

**新建文件**: `django_models/managers.py`

```python
"""
Django 自定义 Manager
封装常用查询逻辑
"""

from django.db import models


class ContentManager(models.Manager):
    """内容管理器 - 封装常用查询"""

    def get_queryset(self):
        """自定义 QuerySet"""
        return ContentQuerySet(self.model, using=self._db)

    # ===== 状态查询 =====
    def drafts(self):
        """草稿"""
        return self.filter(status='draft')

    def pending(self):
        """待审核"""
        return self.filter(status='pending')

    def reviewed(self):
        """已审核"""
        return self.filter(status='reviewed')

    def rejected(self):
        """已拒绝"""
        return self.filter(status='rejected')

    def published(self):
        """已发布"""
        return self.filter(status='published')

    def terminated(self):
        """已终止"""
        return self.filter(status='terminated')

    def active(self):
        """活跃状态（草稿、待审核、已审核、已发布）"""
        return self.filter(status__in=['draft', 'pending', 'reviewed', 'published'])

    # ===== 用户相关查询 =====
    def by_creator(self, user_id):
        """指定创建者的内容"""
        return self.filter(creator_id=user_id)

    def by_describer(self, user_id):
        """指定描述者的内容"""
        return self.filter(describer_id=user_id)

    def by_reviewer(self, user_id):
        """指定审核者的内容"""
        return self.filter(reviewer_id=user_id)

    # ===== DDL 查询 =====
    def with_deadline(self):
        """有截止日期的内容"""
        return self.filter(deadline__isnull=False)

    def upcoming_deadlines(self):
        """未到期的DDL"""
        from django.utils import timezone
        return self.filter(deadline__gt=timezone.now())

    # ===== 搜索 =====
    def search(self, query):
        """搜索标题和内容"""
        from django.db.models import Q
        if not query:
            return self.none()
        return self.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )


class ContentQuerySet(models.QuerySet):
    """自定义 QuerySet - 支持链式调用"""

    def active(self):
        """活跃状态"""
        return self.filter(status__in=['draft', 'pending', 'reviewed', 'published'])

    def by_type(self, content_type):
        """按类型筛选"""
        return self.filter(type=content_type)

    def with_tag(self, tag):
        """按标签筛选"""
        return self.filter(tag__icontains=tag)


class UserManager(models.Manager):
    """用户管理器"""

    def editors(self):
        """所有编辑"""
        return self.filter(role__gte=1)

    def admins(self):
        """所有管理员"""
        return self.filter(role__gte=2)

    def regular_users(self):
        """普通用户"""
        return self.filter(role=0)

    def by_student_id(self, student_id):
        """按学号查询"""
        return self.filter(student_id=student_id)


class CommentManager(models.Manager):
    """评论管理器"""

    def top_level(self):
        """顶层评论（无父评论）"""
        return self.filter(parent_comment_id__isnull=True)

    def by_news(self, news_id):
        """指定新闻的评论"""
        return self.filter(news_id=news_id)

    def by_creator(self, user_id):
        """指定用户的评论"""
        return self.filter(creator_id=user_id)
```

### 任务 2: 更新 django_models/models.py

**原则**:
- ✅ 任务 0 已修复字段不一致问题
- ✅ 本任务只添加 Manager，不再修改字段定义
- ✅ 保持所有字段完全不变
- ✅ 添加 @property 兼容层

**修改**: `django_models/models.py`

在 `User_info` 类中添加：

```python
# ===== Manager（新增） =====
objects = models.Manager()  # 默认 Manager - 保持兼容
users = UserManager()  # 自定义 Manager - 提供新功能
```

在 `Content` 类中添加：

```python
# ===== Manager（新增） =====
objects = models.Manager()  # 默认 Manager - 保持兼容
contents = ContentManager()  # 自定义 Manager - 提供新功能
```

在 `Comment` 类中添加：

```python
# ===== Manager（新增） =====
objects = models.Manager()  # 默认 Manager - 保持兼容
comments = CommentManager()  # 自定义 Manager - 提供新功能
```

---

## ✅ 验证标准

- [ ] **任务 0**: 数据库字段修复完成
  - [ ] `Content` 模型添加 `locker_id` 和 `locked_at` 字段
  - [ ] `Comment` 模型修复 `created`/`updated` 字段名
  - [ ] 验证字段与数据库 100% 一致
- [ ] **任务 1**: `managers.py` 创建完成
- [ ] **任务 2**: `models.py` 添加 Manager
- [ ] 运行 `python test_api.py` 全部通过
- [ ] 旧代码仍然可用：
  - `User_info.objects.filter()` ✅
  - `Content.objects.filter()` ✅
  - `user.has_editor_perm` ✅ (通过@property)

---

## 📝 执行步骤

1. **任务 0**: 修复数据库字段不一致
2. **创建 managers.py**
2. **更新 models.py**（只添加 Manager）
3. **运行测试验证**
4. **更新文档记录**

---

*阶段 1 计划由 Claude Code 生成*
*最后更新: 2026-02-15*
