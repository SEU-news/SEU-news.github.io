"""
Django 自定义 Manager
封装常用查询逻辑，简化视图层代码
"""

from django.db import models
from django.db.models import Q


class ContentQuerySet(models.QuerySet):
    """自定义 QuerySet - 支持链式调用"""

    def active(self):
        """活跃状态（草稿、待审核、已审核、已发布）"""
        return self.filter(status__in=['draft', 'pending', 'reviewed', 'published'])

    def by_type(self, content_type):
        """按类型筛选"""
        return self.filter(type=content_type)

    def with_tag(self, tag):
        """按标签筛选"""
        return self.filter(tag__icontains=tag)

    def with_deadline(self):
        """有截止日期的内容"""
        return self.filter(deadline__isnull=False)

    def upcoming_deadlines(self):
        """未到期的DDL"""
        from django.utils import timezone
        return self.filter(deadline__gt=timezone.now())

    def search(self, query):
        """搜索标题和内容"""
        if not query:
            return self.none()
        return self.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )


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
        if not query:
            return self.none()
        return self.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )


class UserManager(models.Manager):
    """用户管理器"""

    def editors(self):
        """所有编辑（包括管理员和超管）"""
        return self.filter(role__gte=1)

    def admins(self):
        """所有管理员（包括超管）"""
        return self.filter(role__gte=2)

    def regular_users(self):
        """普通用户（无权限）"""
        return self.filter(role=0)

    def by_student_id(self, student_id):
        """按学号查询"""
        return self.filter(student_id=student_id)

    def by_realname(self, realname):
        """按真实姓名查询"""
        return self.filter(realname=realname)


class CommentManager(models.Manager):
    """评论管理器"""

    def top_level(self):
        """顶层评论（无父评论）"""
        return self.filter(parent_comment_id__isnull=True)

    def replies(self):
        """回复评论（有父评论）"""
        return self.filter(parent_comment_id__isnull=False)

    def by_news(self, news_id):
        """指定新闻的评论"""
        return self.filter(news_id=news_id)

    def by_creator(self, user_id):
        """指定用户的评论"""
        return self.filter(creator_id=user_id)
