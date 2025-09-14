from functools import wraps

from flask import session, redirect, url_for, abort

from django_models.models import User_info


def login_required(f):
    """装饰器：要求用户登录"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """装饰器：要求管理员权限"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        username = session.get('username')

        if not username:
            abort(401)

        user = User_info.objects.filter(username=username).first()

        if not user or not user.has_admin_permission():
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


def editor_required(f):
    """装饰器：要求编辑权限"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        username = session.get('username')

        if not username:
            abort(401)

        user = User_info.objects.filter(username=username).first()

        # 如果用户不存在或没有权限，都返回403
        if not user or not user.has_editor_permission():
            abort(403)

        return f(*args, **kwargs)

    return decorated_function
