"""
认证相关视图

包含：登录、注册、登出、获取当前用户、修改密码
"""

import logging
import hashlib

from django.contrib.auth import login, logout
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import User_info
from api.serializers import UserSerializer, LoginResponseSerializer


logger = logging.getLogger(__name__)


class LoginAPIView(APIView):
    """
    用户登录 API
    """
    permission_classes = [AllowAny]

    def post(self, request):
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
