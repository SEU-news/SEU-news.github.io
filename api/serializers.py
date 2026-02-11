"""
API 序列化器

定义所有 API 端点的数据序列化逻辑
"""

from rest_framework import serializers
from django_models.models import User_info, Content, Comment


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息序列化器
    """
    has_editor_perm = serializers.SerializerMethodField()
    has_admin_perm = serializers.SerializerMethodField()

    class Meta:
        model = User_info
        fields = [
            'id',
            'username',
            'realname',
            'student_id',
            'avatar',
            'has_editor_perm',
            'has_admin_perm',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_has_editor_perm(self, obj):
        """序列化 has_editor_perm 属性"""
        return obj.has_editor_perm

    def get_has_admin_perm(self, obj):
        """序列化 has_admin_perm 属性"""
        return obj.has_admin_perm


class ContentSerializer(serializers.ModelSerializer):
    """
    内容序列化器
    """
    creator_username = serializers.SerializerMethodField()
    describer_username = serializers.SerializerMethodField()
    reviewer_username = serializers.SerializerMethodField()

    formatted_created_at = serializers.SerializerMethodField()
    formatted_updated_at = serializers.SerializerMethodField()
    formatted_deadline = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = [
            'id',
            'creator_id',
            'describer_id',
            'reviewer_id',
            'title',
            'short_title',
            'link',
            'content',
            'type',
            'status',
            'status_display',
            'tag',
            'deadline',
            'image_list',
            'publish_at',
            'created_at',
            'updated_at',
            'formatted_created_at',
            'formatted_updated_at',
            'formatted_deadline',
            'creator_username',
            'describer_username',
            'reviewer_username',
            'can_delete',
        ]

    def get_creator_username(self, obj):
        """获取创建者用户名"""
        if obj is None or not hasattr(obj, 'creator_username'):
            return ''
        return obj.creator_username or ''

    def get_describer_username(self, obj):
        """获取描述者用户名"""
        if obj is None or not hasattr(obj, 'describer_username'):
            return ''
        return obj.describer_username or ''

    def get_reviewer_username(self, obj):
        """获取审核者用户名"""
        if obj is None or not hasattr(obj, 'reviewer_username'):
            return ''
        return obj.reviewer_username or ''

    def get_can_delete(self, obj):
        """检查是否可以删除（创建者或管理员）"""
        if obj is None:
            return False
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.creator_id == request.user.id or request.user.has_admin_perm
        return False

    def get_formatted_created_at(self, obj):
        if obj is None or not hasattr(obj, 'created_at') or not obj.created_at:
            return ''
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    def get_formatted_updated_at(self, obj):
        if obj is None or not hasattr(obj, 'updated_at') or not obj.updated_at:
            return ''
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')

    def get_formatted_deadline(self, obj):
        if obj is None or not hasattr(obj, 'deadline') or not obj.deadline:
            return ''
        return obj.deadline.strftime('%Y-%m-%d')

    def get_status_display(self, obj):
        if obj is None or not hasattr(obj, 'status') or not obj.status:
            return ''
        status_map = {
            'draft': '草稿',
            'pending': '待审核',
            'reviewed': '已审核',
            'rejected': '已拒绝',
            'published': '已发布',
            'terminated': '已终止',
        }
        return status_map.get(obj.status, obj.status)


class ContentCreateSerializer(serializers.ModelSerializer):
    """
    内容创建序列化器
    """
    deadline = serializers.DateTimeField(required=False, allow_null=True)
    tag = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Content
        fields = [
            'title',
            'short_title',
            'link',
            'content',
            'type',
            'tag',
            'deadline',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError('User authentication required')

        # 设置必填字段
        validated_data['creator_id'] = request.user.id
        validated_data['status'] = 'draft'

        # describer_id 不能为 null，设置为创建者 id
        if 'describer_id' not in validated_data or validated_data['describer_id'] is None:
            validated_data['describer_id'] = request.user.id

        try:
            return Content.objects.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError(f'Failed to create content: {str(e)}')


class ContentUpdateSerializer(serializers.ModelSerializer):
    """
    内容更新序列化器
    """
    tag = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    deadline = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Content
        fields = [
            'title',
            'short_title',
            'link',
            'content',
            'type',
            'tag',
            'deadline',
        ]


class ContentDescribeSerializer(serializers.ModelSerializer):
    """
    内容描述序列化器
    """
    class Meta:
        model = Content
        fields = [
            'title',
            'short_title',
            'content',
            'type',
            'tag',
        ]

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.describer_id = request.user.id
        instance.status = 'pending'  # 描述后变为待审核
        return super().update(instance, validated_data)


class ContentModifySerializer(serializers.ModelSerializer):
    """
    内容修改序列化器（用于 pending 状态的修改）
    """
    class Meta:
        model = Content
        fields = [
            'title',
            'short_title',
            'content',
            'type',
            'tag',
            'deadline',
        ]

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.describer_id = request.user.id
        # 保持 pending 状态不变
        instance.status = 'pending'
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """
    评论序列化器
    """
    class Meta:
        model = Comment
        fields = [
            'id',
            'comment',
            'creator_id',
            'news_id',
            'parent_comment_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LoginResponseSerializer(serializers.Serializer):
    """
    登录响应序列化器
    """
    success = serializers.BooleanField()
    user = UserSerializer()
