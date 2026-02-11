"""
API 视图

定义所有 API 端点的视图逻辑
"""

import logging

from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import User_info, Content, Comment
from api.serializers import (
    UserSerializer,
    ContentSerializer,
    ContentCreateSerializer,
    ContentUpdateSerializer,
    ContentDescribeSerializer,
    CommentSerializer,
    LoginResponseSerializer,
)
from api.permissions import IsEditorOrAdmin, IsAdmin, IsOwnerOrAdmin, IsCreatorOrAdmin


logger = logging.getLogger(__name__)


# ==================== 认证相关 ====================

class LoginAPIView(APIView):
    """
    用户登录 API
    """
    permission_classes = [AllowAny]

    def post(self, request):
        import hashlib

        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'success': False, 'message': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User_info.objects.get(username=username)
            input_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

            if user.password_MD5 == input_hash:
                # 使用 Django 的 login() 函数正确设置 session
                from django.contrib.auth import login

                # 设置 backend 属性（required by Django login()）
                user.backend = 'api.authentication.User_infoBackend'

                # 使用 Django 的 login() 函数
                login(request, user)

                logger.info(f"用户登录成功: {username}")

                serializer = UserSerializer(user)
                return Response({
                    'success': True,
                    'user': serializer.data
                })
            else:
                logger.warning(f"用户登录失败，密码错误: {username}")
                return Response(
                    {'success': False, 'message': '用户名或密码错误'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except User_info.DoesNotExist:
            logger.warning(f"用户登录失败，用户不存在: {username}")
            return Response(
                {'success': False, 'message': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterAPIView(APIView):
    """
    用户注册 API
    """
    permission_classes = [AllowAny]

    def post(self, request):
        import hashlib

        username = request.data.get('username')
        password = request.data.get('password')
        realname = request.data.get('realname', '')
        student_id = request.data.get('student_id', '')

        if not username or not password:
            return Response(
                {'success': False, 'message': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 6:
            return Response(
                {'success': False, 'message': '密码长度至少6位'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查用户名是否已存在
        if User_info.objects.filter(username=username).exists():
            return Response(
                {'success': False, 'message': '用户名已存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User_info(
                username=username,
                password_MD5=hashlib.md5(password.encode('utf-8')).hexdigest(),
                realname=realname,
                student_id=student_id,
                avatar='',
                role=User_info.PERMISSION_NONE
            )
            user.save()

            logger.info(f"用户注册成功: {username}")
            return Response({'success': True, 'message': '注册成功！请登录'})

        except IntegrityError:
            logger.error(f"用户注册失败，数据库错误: {username}")
            return Response(
                {'success': False, 'message': '注册失败，请重试'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(APIView):
    """
    用户登出 API
    允许任何用户调用（即使未登录也不会出错）
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.user.username if hasattr(request.user, 'username') else request.session.get('username', 'unknown')
        logout(request)
        logger.info(f"用户登出: {username}")
        return Response({'success': True, 'message': '登出成功'})


class CurrentUserAPIView(APIView):
    """
    获取当前用户信息 API
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordAPIView(APIView):
    """
    修改密码 API
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import hashlib

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'success': False, 'message': '旧密码和新密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证旧密码
        old_hash = hashlib.md5(old_password.encode('utf-8')).hexdigest()
        if request.user.password_MD5 != old_hash:
            return Response(
                {'success': False, 'message': '旧密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新密码
        request.user.password_MD5 = hashlib.md5(new_password.encode('utf-8')).hexdigest()
        request.user.save()

        logger.info(f"用户修改密码: {request.user.username}")
        return Response({'success': True, 'message': '密码修改成功'})


# ==================== 内容管理 ====================

class ContentListAPIView(generics.ListCreateAPIView):
    """
    内容列表 API
    GET: 获取内容列表（分页）
    POST: 创建新内容（需要 Editor 权限）
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContentCreateSerializer
        return ContentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsEditorOrAdmin()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # 自定义 create 方法，确保返回正确的响应
        logger.info(f'POST data: {request.data}')
        logger.info(f'POST data type: {type(request.data)}')

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f'Serializer validation errors: {serializer.errors}')
            logger.error(f'Serializer validated_data: {serializer.validated_data}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f'Serializer validated data: {serializer.validated_data}')

        # 保存实例
        self.perform_create(serializer)

        # 检查 instance
        if not hasattr(serializer, 'instance') or serializer.instance is None:
            logger.error('Serializer.instance is None after perform_create!')
            return Response({'error': 'Failed to create content'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        content = serializer.instance
        logger.info(f'Created content: id={content.id}, title={content.title}, type={content.type}')

        headers = self.get_success_headers(serializer.data)
        # 返回创建的数据（使用 ContentSerializer 序列化）
        response_serializer = ContentSerializer(content, context={'request': request})

        logger.info(f'Response serializer data: {response_serializer.data}')

        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = Content.objects.all().order_by('-updated_at')

        # 搜索
        query = self.request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(title__icontains=query)

        # 排序
        sort_field = self.request.query_params.get('sort', 'updated_at')
        sort_order = self.request.query_params.get('order', 'desc')
        allowed_fields = ['id', 'created_at', 'updated_at', 'deadline', 'title']

        if sort_field in allowed_fields:
            order_by = f"-{sort_field}" if sort_order == 'desc' else sort_field
            queryset = queryset.order_by(order_by)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        legal_sizes = [10, 20, 50, 100]

        if page_size not in legal_sizes:
            page_size = 10

        total = queryset.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # 当前页数据
        results = queryset[offset:offset + page_size]

        serializer = ContentSerializer(results, many=True, context={'request': request})
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'results': serializer.data
        })


class ContentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    内容详情 API
    GET: 获取内容详情
    PUT/PATCH: 更新内容（需要 Editor 权限或为创建者）
    DELETE: 删除内容（需要为创建者）
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Content.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContentUpdateSerializer
        return ContentSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsCreatorOrAdmin()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ContentSerializer(instance, context={'request': request})
        return Response(serializer.data)


class ContentDescribeAPIView(generics.UpdateAPIView):
    """
    内容描述 API
    POST: 描述内容（需要 Editor 权限）
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]
    serializer_class = ContentDescribeSerializer
    queryset = Content.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success': True, 'message': '描述提交成功'})


class ContentReviewAPIView(APIView):
    """
    内容审核 API
    POST: 审核内容（通过/拒绝）（需要 Editor 或 Admin 权限）
    注意：不能审核自己创建或描述的内容
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        try:
            content = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response(
                {'success': False, 'message': '内容不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 检查不能审核自己创建或描述的内容
        if request.user.id == content.creator_id or request.user.id == content.describer_id:
            return Response(
                {'success': False, 'message': '不可审核自己所写的内容！'},
                status=status.HTTP_403_FORBIDDEN
            )

        action = request.data.get('action')  # 'approve' or 'reject'
        comment = request.data.get('comment', '')

        if action not in ['approve', 'reject']:
            return Response(
                {'success': False, 'message': '无效的操作'},
                status=status.HTTP_400_BAD_REQUEST
            )

        content.reviewer_id = request.user.id

        if action == 'approve':
            content.status = 'reviewed'
        else:
            content.status = 'rejected'

        content.save()

        logger.info(f"内容审核: {pk}, action={action}, reviewer={request.user.username}")
        return Response({'success': True, 'message': '审核成功'})


class ContentRecallAPIView(APIView):
    """
    内容撤回 API
    POST: 撤回内容（需要为创建者）
    """
    permission_classes = [IsAuthenticated, IsCreatorOrAdmin]
    queryset = Content.objects.all()

    def post(self, request, pk):
        try:
            content = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response(
                {'success': False, 'message': '内容不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 设置为已终止状态
        content.status = 'terminated'
        content.save()

        logger.info(f"内容撤回: {pk}, user={request.user.username}")
        return Response({'success': True, 'message': '撤回成功'})


# ==================== 搜索 ====================

class SearchAPIView(APIView):
    """
    搜索 API
    POST: 搜索内容
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('q', '').strip()

        if not query:
            return Response({
                'success': True,
                'count': 0,
                'results': []
            })

        # 搜索标题和内容
        results = Content.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-updated_at')

        serializer = ContentSerializer(results, many=True, context={'request': request})
        return Response({
            'success': True,
            'count': results.count(),
            'results': serializer.data
        })


# ==================== 发布（占位）====================

class PublishAPIView(APIView):
    """
    批量发布内容
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        content_ids = request.data.get('content_ids', [])
        if not content_ids:
            return Response(
                {'success': False, 'message': '请提供要发布的内容ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.utils import timezone

        updated_count = 0
        failed_items = []

        for content_id in content_ids:
            try:
                content = Content.objects.get(id=content_id)
                # 只有已审核的内容才能发布
                if content.status == 'reviewed':
                    content.status = 'published'
                    content.publish_at = timezone.now()
                    content.save()
                    updated_count += 1
                else:
                    failed_items.append({
                        'id': content_id,
                        'reason': f'状态为 {content.status}，不能发布'
                    })
            except Content.DoesNotExist:
                failed_items.append({'id': content_id, 'reason': '内容不存在'})

        return Response({
            'success': True,
            'updated': updated_count,
            'failed': failed_items
        })


class TypstAPIView(APIView):
    """
    生成Typst格式文档
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request, date):
        from django.utils import timezone
        from datetime import datetime

        try:
            publish_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 查询该日期发布的内容
        contents = Content.objects.filter(
            publish_at__date=publish_date,
            status='published'
        ).order_by('-publish_at')

        typst_content = self._generate_typst(contents)

        return Response({
            'success': True,
            'date': date,
            'count': len(contents),
            'typst': typst_content
        })

    def _generate_typst(self, contents):
        """生成 Typst 格式文档"""
        lines = [
            '# 新闻简报',
            f'发布日期: {timezone.now().strftime("%Y年%m月%d日")}',
            ''
        ]

        for content in contents:
            lines.extend([
                f'## {content.title}',
                f'{content.content}',
                f'来源: {content.link}',
                ''
            ])

        return '\n'.join(lines)


class LatexAPIView(APIView):
    """
    生成LaTeX格式文档
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request, date):
        from django.utils import timezone
        from datetime import datetime

        try:
            publish_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 查询该日期发布的内容
        contents = Content.objects.filter(
            publish_at__date=publish_date,
            status='published'
        ).order_by('-publish_at')

        latex_content = self._generate_latex(contents)

        return Response({
            'success': True,
            'date': date,
            'count': len(contents),
            'latex': latex_content
        })

    def _generate_latex(self, contents):
        """生成 LaTeX 格式文档"""
        lines = [
            '\\documentclass{article}',
            '\\usepackage{ctex}',
            '\\begin{document}',
            '\\title{新闻简报}',
            f'\\author{{发布日期: {timezone.now().strftime("%Y年%m月%d日")}}}',
            '\\maketitle',
            ''
        ]

        for content in contents:
            lines.extend([
                f'\\section*{{{content.title}}}',
                f'{content.content}',
                f'\\textbf{{来源: {content.link}}}',
                ''
            ])

        lines.append('\\end{document}')
        return '\n'.join(lines)


# ==================== 管理功能（占位）====================

class UserAdminListAPIView(APIView):
    """
    用户列表 API
    GET: 获取用户列表（支持分页、排序、搜索、权限筛选）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        # 获取查询参数
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        sort_field = request.query_params.get('sort', 'created_at')
        sort_order = request.query_params.get('order', 'desc')
        query = request.query_params.get('q', '')
        role_filter = request.query_params.get('role', '')

        # 验证分页大小
        legal_sizes = [10, 20, 50, 100]
        if page_size not in legal_sizes:
            page_size = 10

        # 验证排序字段
        allowed_fields = ['id', 'username', 'realname', 'student_id', 'role', 'created_at']
        if sort_field not in allowed_fields:
            sort_field = 'created_at'

        # 构建查询集
        queryset = User_info.objects.all()

        # 搜索（用户名或学号）
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(student_id__icontains=query)
            )

        # 权限筛选
        if role_filter and role_filter.isdigit():
            queryset = queryset.filter(role=int(role_filter))

        # 排序
        order_by = f"-{sort_field}" if sort_order == 'desc' else sort_field
        queryset = queryset.order_by(order_by)

        # 分页
        total = queryset.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # 当前页数据
        results = queryset[offset:offset + page_size]

        # 序列化
        serializer = UserSerializer(results, many=True, context={'request': request})

        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'results': serializer.data
        })


class AddDeadlineAPIView(APIView):
    """
    添加截止日期 API（占位）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        content_id = request.data.get('content_id')
        deadline = request.data.get('deadline')

        if not content_id or not deadline:
            return Response({'success': False, 'message': 'content_id 和 deadline 不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from datetime import datetime
            deadline_dt = datetime.fromisoformat(deadline)

            content = Content.objects.get(id=content_id)
            content.deadline = deadline_dt
            content.save()

            logger.info(f"用户 {request.user.username} 为内容 {content_id} 设置截止日期: {deadline}")

            return Response({'success': True, 'message': '截止日期设置成功'})
        except Content.DoesNotExist:
            return Response({'success': False, 'message': '内容不存在'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'success': False, 'message': '日期格式无效'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 新增API视图 ====================

class UploadImageAPIView(APIView):
    """
    上传图片
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'success': False, 'message': '未找到图片文件'}, status=status.HTTP_400_BAD_REQUEST)

        import uuid
        import os
        from django.conf import settings

        image = request.FILES['image']
        filename = f"{uuid.uuid4().hex}_{image.name}"
        filepath = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

        # 保存文件
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        return Response({
            'success': True,
            'image_url': f"/media/uploads/{filename}"
        })


class PasteAPIView(APIView):
    """
    粘贴URL并创建内容
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({'success': False, 'message': 'URL不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建内容对象
        content = Content.objects.create(
            creator_id=request.user.id,
            describer_id=request.user.id,  # 设置描述者为当前用户
            title=url,  # 暂时用URL作为标题
            link=url,
            content='',  # 空内容，等待后续编辑
            status='draft',
            type='paste'
        )

        return Response({'success': True, 'content_id': content.id})


class ContentCancelAPIView(APIView):
    """
    取消内容
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, pk):
        try:
            content = Content.objects.get(id=pk)
            content.status = 'cancelled'
            content.save()
            return Response({'success': True, 'message': '内容已取消'})
        except Content.DoesNotExist:
            return Response({'success': False, 'message': '内容不存在'}, status=status.HTTP_404_NOT_FOUND)


class PreviewAPIView(APIView):
    """
    预览编辑
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        entries = request.data.get('entries', [])
        # 生成预览HTML/Markdown
        preview_html = self._generate_preview(entries)
        return Response({'success': True, 'preview': preview_html})

    def _generate_preview(self, entries):
        """生成预览HTML"""
        html = '<div class="preview-container">'

        for entry_id in entries:
            try:
                content = Content.objects.get(id=entry_id)
                html += f'<h3>{content.title}</h3>'
                html += f'<p>{content.content}</p>'
                if content.link:
                    html += f'<p><a href="{content.link}" target="_blank">来源链接</a></p>'
                html += '<hr>'
            except Content.DoesNotExist:
                pass

        html += '</div>'
        return html


class UserRoleEditAPIView(APIView):
    """
    编辑用户角色
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        try:
            user = User_info.objects.get(id=user_id)
        except User_info.DoesNotExist:
            return Response({'success': False, 'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'add' or 'remove'
        permission = request.data.get('permission')  # 'editor' or 'admin'

        if permission == 'editor':
            perm_bit = User_info.PERMISSION_EDITOR
        elif permission == 'admin':
            perm_bit = User_info.PERMISSION_ADMIN
        else:
            return Response({'success': False, 'message': '无效的权限类型'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'add':
            user.role |= perm_bit
        elif action == 'remove':
            user.role &= ~perm_bit
        else:
            return Response({'success': False, 'message': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)

        user.save()
        return Response({'success': True, 'role': user.role, 'message': '角色更新成功'})


class UserEditAPIView(APIView):
    """
    编辑用户信息
    支持字段：realname, student_id, password
    注意：password 字段需要管理员权限（或用户修改自己的密码）
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        import hashlib

        try:
            user = User_info.objects.get(id=user_id)

            # 权限检查：只能编辑自己或管理员可以编辑任何人
            if user_id != request.user.id and not request.user.has_admin_perm:
                return Response({'success': False, 'message': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

            # 更新字段
            if 'realname' in request.data:
                user.realname = request.data['realname']
            if 'student_id' in request.data:
                user.student_id = request.data['student_id']

            # 密码字段需要特殊处理
            if 'password' in request.data:
                password = request.data['password']

                # 权限检查：修改密码需要管理员权限或修改自己的密码
                if user_id != request.user.id and not request.user.has_admin_perm:
                    return Response({'success': False, 'message': '无权修改他人密码'}, status=status.HTTP_403_FORBIDDEN)

                # 密码验证
                if len(password) < 6:
                    return Response({'success': False, 'message': {'password': ['密码长度至少6位']}}, status=status.HTTP_400_BAD_REQUEST)

                user.password_MD5 = hashlib.md5(password.encode('utf-8')).hexdigest()
                logger.info(f"用户 {request.user.username} 修改了用户 {user.username} 的密码")

            user.save()
            serializer = UserSerializer(user)
            return Response({'success': True, 'user': serializer.data, 'message': '用户信息更新成功'})

        except User_info.DoesNotExist:
            return Response({'success': False, 'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


class AdminDashboardAPIView(APIView):
    """
    管理面板数据
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        from django.utils import timezone
        from django.db.models import Count

        # 统计数据
        total_users = User_info.objects.count()
        total_contents = Content.objects.count()
        pending_reviews = Content.objects.filter(status='pending').count()
        published_today = Content.objects.filter(
            status='published',
            publish_at__date=timezone.now().date()
        ).count()

        # 状态分布统计（使用 aggregation 高效计算）
        status_stats = Content.objects.values('status').annotate(count=Count('id'))
        status_counts = {stat['status']: stat['count'] for stat in status_stats}

        # 确保所有状态都有值（为空则返回 0）
        all_statuses = ['draft', 'pending', 'reviewed', 'rejected', 'published', 'terminated']
        for s in all_statuses:
            status_counts.setdefault(s, 0)

        return Response({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_contents': total_contents,
                'pending_reviews': pending_reviews,
                'published_today': published_today,
                'status_counts': status_counts
            }
        })


class ContentStatusUpdateAPIView(APIView):
    """
    内容状态更新 API
    POST: 修改内容状态（需要 Admin 权限）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            content = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response(
                {'success': False, 'message': '内容不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')

        # 验证状态转换的有效性
        valid_transitions = {
            'draft': ['terminated', 'pending'],
            'pending': ['draft', 'reviewed', 'rejected', 'terminated'],
            'reviewed': ['draft', 'published', 'terminated'],
            'rejected': ['draft', 'terminated'],
            'published': ['terminated'],
            'terminated': ['draft'],
        }

        current_status = content.status

        if new_status not in valid_transitions.get(current_status, []):
            return Response(
                {'success': False, 'message': f'无法从 {current_status} 转换到 {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 清除相关字段（状态转换时）
        if new_status == 'draft':
            content.reviewer_id = None
        elif new_status in ['reviewed', 'rejected']:
            content.reviewer_id = request.user.id

        content.status = new_status
        content.save()

        logger.info(f"内容状态更新: {pk}, {current_status} -> {new_status}, user={request.user.username}")
        return Response({'success': True, 'message': '状态更新成功'})
