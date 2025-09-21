from django.db import models
import os
import json
from django.conf import settings
# Create your models here.


class User_info(models.Model):
    PERMISSION_NONE = 0b00  # 0 - 无权限
    PERMISSION_EDITOR = 0b01  # 1 - 编辑权限
    PERMISSION_ADMIN = 0b10  # 2 - 管理员权限
    PERMISSION_ALL = 0b11  # 3 - 所有权限

    PERMISSION_CHOICES = [
        (PERMISSION_NONE, '普通用户'),
        (PERMISSION_EDITOR, '编辑'),
        (PERMISSION_ADMIN, '管理员'),
        (PERMISSION_ALL, '超级管理员'),
    ]

    id = models.AutoField(primary_key=True)

    username = models.CharField(max_length=30, unique=True, verbose_name='用户名')
    password_MD5 = models.CharField(max_length=100, verbose_name='密码')
    avatar = models.CharField(max_length=100, verbose_name='头像')
    realname = models.CharField(max_length=30, verbose_name='真名')
    student_id = models.CharField(max_length=30, verbose_name='学号')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.PositiveIntegerField(verbose_name="权限位", choices=PERMISSION_CHOICES, default=0,
                                       help_text="●0(00)：一般用户 1(01)：编辑 2(10)：管理员 3(11)：兼任两者")

    class Meta:
        db_table = 'user_info'  # 数据库表名
        verbose_name = '用户'  # 单数名称
        verbose_name_plural = '用户管理'  # 复数名称
        # 按创建时间降序排列
        ordering = ['-created_at']
        # 创建数据库索引
        indexes = [
            models.Index(fields=['created_at'], name='idx_user_created_at'),
            models.Index(fields=['updated_at'], name='idx_user_updated_at'),
            models.Index(fields=['student_id'], name='idx_user_student_id'),
            models.Index(fields=['realname'], name='idx_user_realname'),
        ]

    def __str__(self):
        return self.username  # 对象显示为用户名

    def has_editor_permission(self):
        """检查是否有编辑权限"""
        return bool(self.role & self.PERMISSION_EDITOR)

    def has_admin_permission(self):
        """检查是否有管理员权限"""
        return bool(self.role & self.PERMISSION_ADMIN)

    def has_permission(self, required_permission):
        """检查是否有指定权限"""
        return bool(self.role & required_permission)


class Content(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('reviewed', '已审核'),
        ('rejected', '已拒绝'),
        ('published', '已发布'),
    )
    id = models.AutoField(primary_key=True)

    creator_id = models.IntegerField(verbose_name='创建者ID', null=False)  # 假设不允许为空
    describer_id = models.IntegerField(verbose_name='描述者ID', null=True)  # 允许为空
    reviewer_id = models.IntegerField(verbose_name='审核者ID', null=True)  # 允许为空

    title = models.CharField(max_length=200, verbose_name='标题')
    short_title = models.CharField(max_length=100, verbose_name='短标题')
    link = models.TextField(verbose_name='链接')
    content = models.TextField(verbose_name='详细内容')

    deadline = models.DateField(verbose_name="截止时间", null=True, blank=True)
    image_list = models.TextField(default='[]', verbose_name='图片列表', help_text='JSON格式的图片路径数组')
    publish_at = models.DateTimeField(verbose_name="发布时间", null=True, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    type = models.CharField(max_length=50, verbose_name='类型')
    tag = models.TextField(verbose_name='标签', default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_image(self, image_path):
        try:
            # 解析现有的JSON字符串
            if self.image_list:
                image_list_data = json.loads(self.image_list)
            else:
                image_list_data = []

            # 生成相对路径
            relative_path = f"uploads/{os.path.basename(image_path)}"

            # 添加到图片列表
            image_list_data.append(relative_path)

            # 重新保存为JSON字符串
            self.image_list = json.dumps(image_list_data)
            return True

        except Exception as e:
            print(f"添加图片失败: {str(e)}")
            return False

    @property
    def reviewer_username(self):
        try:
            user = User_info.objects.get(id=self.reviewer_id)
            return user.username
        except User_info.DoesNotExist:
            return ''

    @property
    def creator_username(self):
        try:
            user = User_info.objects.get(id=self.creator_id)
            return user.username
        except User_info.DoesNotExist:
            return ''

    @property
    def describer_username(self):
        try:
            user = User_info.objects.get(id=self.describer_id)
            return user.username
        except User_info.DoesNotExist:
            return ''

    class Meta:
        db_table = 'content_management'
        verbose_name = '文章'
        verbose_name_plural = '文章管理'
        # 按更新时间和创建时间降序排列
        ordering = ['-updated_at', '-created_at']
        # 创建数据库索引
        indexes = [
            models.Index(fields=['creator_id'], name='idx_content_creator_id'),
            models.Index(fields=['describer_id'], name='idx_content_describer_id'),
            models.Index(fields=['reviewer_id'], name='idx_content_reviewer_id'),
            models.Index(fields=['status'], name='idx_content_status'),
            models.Index(fields=['type'], name='idx_content_type'),
            models.Index(fields=['deadline'], name='idx_content_deadline'),
            models.Index(fields=['publish_at'], name='idx_content_publish_at'),
            models.Index(fields=['created_at'], name='idx_content_created_at'),
            models.Index(fields=['updated_at'], name='idx_content_updated_at'),
        ]


# 3. 评论表
class Comment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='唯一主键')
    comment = models.TextField(verbose_name='评论内容')
    creator_id = models.IntegerField(verbose_name='评论创建者ID')
    news_id = models.IntegerField(verbose_name='关联新闻ID')
    parent_comment_id = models.IntegerField(null=True, blank=True, default=None, verbose_name='回复的上级评论ID（NULL表示顶层评论）')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    class Meta:
        db_table = 'comment_management'
        verbose_name = '评论'
        verbose_name_plural = '评论管理'
        # 按创建时间降序排列
        ordering = ['-created_at']
        # 创建数据库索引
        indexes = [
            models.Index(fields=['creator_id'], name='idx_creator_id'),
            models.Index(fields=['news_id'], name='idx_news_id'),
            models.Index(fields=['parent_comment_id'], name='idx_parent_comment_id'),
            models.Index(fields=['created_at'], name='idx_created_at'),
            models.Index(fields=['updated_at'], name='idx_updated_at'),
        ]
