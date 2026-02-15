"""
自定义认证后端

因为 User_info 模型不继承自 Django 的 AbstractUser，
所以需要自定义认证后端来处理用户登录和认证。
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication as DRFSessionAuthentication

from django_models.models import User_info


class SessionAuthentication(DRFSessionAuthentication):
    """
    禁用 CSRF 检查的 Session 认证类

    DRF 的 SessionAuthentication 默认会强制检查 CSRF，
    这对于 REST API 是不合适的。这个类继承并禁用了 CSRF 检查。
    """

    def enforce_csrf(self, request):
        """
        REST API 不需要 CSRF 检查，直接通过
        """
        pass  # 禁用 CSRF 检查


class User_infoBackend(ModelBackend):
    """
    自定义认证后端，用于 User_info 模型

    处理：
    1. authenticate() - 用户名密码验证
    2. get_user() - 根据 user_id 获取用户对象
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        认证用户

        Args:
            request: 请求对象
            username: 用户名
            password: 密码（明文）
            **kwargs: 其他参数

        Returns:
            User_info 实例或 None
        """
        import hashlib

        if username is None or password is None:
            return None

        try:
            user = User_info.objects.get(username=username)

            # 使用 MD5 验证密码
            input_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

            if user.password_MD5 == input_hash:
                # 设置后端属性（required for Django's login()）
                user.backend = f'{self.__class__.__module__}.{self.__class__.__name__}'
                return user

        except User_info.DoesNotExist:
            return None

        return None

    def get_user(self, user_id):
        """
        根据 user_id 获取用户对象

        Args:
            user_id: 用户 ID

        Returns:
            User_info 实例或 None
        """
        try:
            # user_id 可能是字符串，需要转换为整数
            if isinstance(user_id, str):
                user_id = int(user_id)

            return User_info.objects.get(pk=user_id)

        except (User_info.DoesNotExist, ValueError, TypeError):
            return None
