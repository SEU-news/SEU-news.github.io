"""
认证相关视图

包含：登录、注册、登出、获取当前用户、修改密码
"""

import logging

from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import User_info
from api.serializers import UserSerializer
from api.services import AuthService
from api.core.exceptions import APIException


logger = logging.getLogger(__name__)


class LoginAPIView(APIView):
    """
    用户登录 API
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            # 使用服务层处理登录逻辑
            user = AuthService.login(username, password)

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

        except APIException as e:
            # 统一异常处理
            logger.warning(f"用户登录失败: {username} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


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

        try:
            # 使用服务层处理注册逻辑
            user = AuthService.register(username, password, realname, student_id)

            logger.info(f"用户注册成功: {username}")
            return Response({
                'success': True,
                'message': '注册成功！请登录'
            })

        except APIException as e:
            # 统一异常处理
            logger.warning(f"用户注册失败: {username} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


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
        return Response({
            'success': True,
            'message': '登出成功'
        })


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

        try:
            # 使用服务层处理密码修改逻辑
            user = AuthService.change_password(request.user, old_password, new_password)

            logger.info(f"用户修改密码: {user.username}")
            return Response({
                'success': True,
                'message': '密码修改成功'
            })

        except APIException as e:
            # 统一异常处理
            logger.warning(f"用户修改密码失败: {request.user.username} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)
