"""
认证服务
处理用户登录、注册、修改密码等认证相关业务逻辑
"""

from typing import Optional
from django.db import transaction
from django_models.models import User_info
from api.core.exceptions import ValidationError, AuthenticationError, ConflictError
from api.core.password_handler import PasswordHandler
from api.services.base_service import BaseService


class AuthService(BaseService):
    """认证服务类"""

    @staticmethod
    def login(username: str, password: str) -> User_info:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录成功的用户对象

        Raises:
            ValidationError: 参数验证失败
            AuthenticationError: 用户名或密码错误
        """
        import logging
        logger = logging.getLogger(__name__)

        # 验证参数
        if not username or not password:
            raise ValidationError('用户名和密码不能为空')

        # 查找用户
        try:
            user = User_info.objects.get(username=username)
            logger.info(f"找到用户: {username}, 密码哈希: {user.password_MD5}")
        except User_info.DoesNotExist:
            logger.warning(f"用户不存在: {username}")
            raise AuthenticationError('用户名或密码错误')

        # 验证密码
        input_hash = PasswordHandler.hash_password(password)
        logger.info(f"输入密码哈希: {input_hash}")

        if not PasswordHandler.verify_password(password, user.password_MD5):
            logger.warning(f"密码验证失败: {username}")
            logger.warning(f"  输入哈希: {input_hash}")
            logger.warning(f"  数据库哈希: {user.password_MD5}")
            raise AuthenticationError('用户名或密码错误')

        # 更新最后登录时间
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user

    @staticmethod
    def register(username: str, password: str, realname: str = '', student_id: str = '') -> User_info:
        """
        用户注册

        Args:
            username: 用户名
            password: 密码
            realname: 真实姓名
            student_id: 学号

        Returns:
            新创建的用户对象

        Raises:
            ValidationError: 参数验证失败
            ConflictError: 用户名已存在
        """
        # 验证参数
        if not username or not password:
            raise ValidationError('用户名和密码不能为空')

        if len(username) > 30:
            raise ValidationError('用户名长度不能超过 30 个字符')

        if len(password) < 6:
            raise ValidationError('密码长度至少为 6 位')

        # 检查用户名是否已存在
        if User_info.objects.filter(username=username).exists():
            raise ConflictError('用户名已存在')

        # 哈希密码
        hashed_password = PasswordHandler.hash_password(password)

        # 创建用户
        with BaseService.transaction():
            user = User_info.objects.create(
                username=username,
                password_MD5=hashed_password,
                realname=realname or username,
                student_id=student_id or '',
                role=0,  # 默认为普通用户
                avatar='',
            )

        return user

    @staticmethod
    def change_password(user: User_info, old_password: str, new_password: str) -> User_info:
        """
        修改密码

        Args:
            user: 当前用户对象
            old_password: 旧密码
            new_password: 新密码

        Returns:
            更新后的用户对象

        Raises:
            ValidationError: 参数验证失败
            AuthenticationError: 旧密码错误
        """
        # 验证参数
        if not old_password or not new_password:
            raise ValidationError('旧密码和新密码不能为空')

        if len(new_password) < 6:
            raise ValidationError('新密码长度至少为 6 位')

        # 验证旧密码
        if not PasswordHandler.verify_password(old_password, user.password_MD5):
            raise AuthenticationError('旧密码错误')

        # 哈希新密码
        hashed_password = PasswordHandler.hash_password(new_password)

        # 更新密码
        user.password_MD5 = hashed_password
        user.save(update_fields=['password_MD5'])

        return user
