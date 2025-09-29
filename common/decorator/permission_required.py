from functools import wraps

from flask import session, redirect, url_for, abort

from django_models.models import User_info


class PermissionDecorators:
    """权限装饰器类，包含常用的权限控制装饰器"""

    @staticmethod
    def login_required(f):
        """
        装饰器：要求用户登录
        如果用户未登录，则重定向到登录页面
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            username = session.get('username')
            # 检查用户是否已登录
            if not username:
                return redirect(url_for('login'))

            user = User_info.objects.filter(username=username).first()
            if not user:
                return redirect(url_for('login'))

            return f(*args, **kwargs)

        return decorated_function

    @staticmethod
    def admin_required(f):
        """
        装饰器：要求管理员权限
        如果用户没有管理员权限，则返回403错误
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            username = session.get('username')

            # 检查用户是否已登录
            if not username:
                abort(401)

            user = User_info.objects.filter(username=username).first()

            # 检查用户是否存在以及是否有管理员权限
            if not user or not user.has_admin_permission():
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    @staticmethod
    def editor_required(f):
        """
        装饰器：要求编辑权限
        如果用户没有编辑权限，则返回403错误
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            username = session.get('username')

            # 检查用户是否已登录
            if not username:
                abort(401)

            user = User_info.objects.filter(username=username).first()

            # 检查用户是否存在以及是否有编辑权限
            if not user or not user.has_editor_permission():
                abort(403)

            return f(*args, **kwargs)

        return decorated_function