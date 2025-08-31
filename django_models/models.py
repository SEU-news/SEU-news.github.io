from django.db import models
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
    username = models.CharField(max_length=30, unique=True, verbose_name='用户名')
    password_MD5 = models.CharField(max_length=100, verbose_name='密码')
    avatar = models.CharField(max_length=100, verbose_name='头像')
    real_name = models.CharField(max_length=30, verbose_name='真名')
    students_id = models.CharField(max_length=30, verbose_name='学号')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.PositiveIntegerField(verbose_name="权限位", choices=PERMISSION_CHOICES, default=0, help_text="●0(00)：一般用户 1(01)：编辑 2(10)：管理员 3(11)：兼任两者")

    class Meta:
        db_table = 'user_info'  # 数据库表名
        verbose_name = '用户'  # 单数名称
        verbose_name_plural = '用户管理'  # 复数名称
        ordering = [
            models.Index(fields=['created_at'], name='idx_created_at'),
            models.Index(fields=['updated_at'], name='idx_updated_at'),
            models.Index(fields=['students_id'], name='idx_students_id'),
            models.Index(fields=['real_name'], name='idx_real_name'),
        ]  # 默认按创建时间降序排列

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
    creator = models.ForeignKey(User_info, on_delete=models.SET_NULL, null=True, related_name='created_content')
    describer = models.ForeignKey(User_info, on_delete=models.SET_NULL, null=True, related_name='described_content')
    reviewer = models.ForeignKey(User_info, on_delete=models.SET_NULL, null=True, related_name='reviewed_content')

    title = models.CharField(max_length=200, verbose_name='标题')
    short_title = models.CharField(max_length=100, verbose_name='短标题')
    link = models.TextField(verbose_name='链接')
    content = models.TextField(verbose_name='详细内容')

    deadline = models.DateTimeField(verbose_name="截止时间")
    image_list = models.TextField(verbose_name='图片list', default=0)
    published_time = models.DateTimeField(verbose_name="发布时间")

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    type = models.CharField(max_length=50, verbose_name='类型')
    tag = models.TextField(verbose_name='标签', default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_management'
        verbose_name = '文章'
        verbose_name_plural = '文章管理'
        indexes = [
            models.Index(fields=['creator'], name='idx_creator_id'),
            models.Index(fields=['describer'], name='idx_describer_id'),
            models.Index(fields=['reviewer'], name='idx_reviewer_id'),
            models.Index(fields=['status'], name='idx_status'),
            models.Index(fields=['type'], name='idx_type'),
            models.Index(fields=['deadline'], name='idx_deadline'),
            models.Index(fields=['published_time'], name='idx_publish_at'),
            models.Index(fields=['created_at'], name='idx_created_at'),
            models.Index(fields=['updated_at'], name='idx_updated_at'),
        ]


# 3. 评论表
class Comment(models.Model):
    news_id = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    creator = models.ForeignKey(User_info, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    parent_comment_id = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', verbose_name="父级评论")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comment'
        verbose_name = '评论'
        verbose_name_plural = '评论管理'
        ordering = [
            models.Index(fields=['creator'], name='idx_creator_id'),
            models.Index(fields=['news_id'], name='idx_news_id'),
            models.Index(fields=['created_at'], name='idx_created'),
            models.Index(fields=['parent_comment_id'], name='idx_parent_comment_id'),
            models.Index(fields=['updated_at'], name='idx_updated_at'),
        ]
