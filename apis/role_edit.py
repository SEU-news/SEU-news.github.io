import logging

from flask import session, flash, redirect, url_for
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import User_info

class EditRoleView(MethodView):
    """
    删除内容条目视图类

    处理删除内容条目的请求。
    """

    # 修改装饰器，只需要登录即可，然后在方法内部检查具体权限
    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

    def post(self, user_id, action, permission):
        """
        处理POST请求，修改用户权限

        参数:
            user_id (int): 用户ID
            action:给予或移除权限
            permission：权限类型

        返回:
            redirect: 重定向到用户管理页面
        """
        # 手动检查用户权限（编辑或管理员权限）
        if 'username' not in session:
            return redirect(url_for('login'))

        try:
            current_user = User_info.objects.get(username=session['username'])
            # 检查是否有管理员权限
            if not current_user.has_admin_permission():
                self.logger.warning(f"用户 {current_user.username} 尝试更改权限位没有足够权限")
                flash("你没有权限执行此操作")
                return redirect(url_for('user_admin'))
        except User_info.DoesNotExist:
            self.logger.error(f"操作时用户不存在: {session.get('username')}")
            flash("用户信息错误，请重新登录")
            return redirect(url_for('login'))

        try:
            user = User_info.objects.get(id=user_id)
            current_user =  User_info.objects.get(username=session['username'])
            # 定义权限位
            if permission == 'editor':
                if action == 'grant':
                    # 授予编辑权限
                    user.role |= User_info.PERMISSION_EDITOR
                else:  # remove
                    # 移除编辑权限
                    user.role &= ~User_info.PERMISSION_EDITOR
            elif permission == 'admin':
                if action == 'grant':
                    # 授予管理员权限
                    user.role |= User_info.PERMISSION_ADMIN
                else:  # remove
                    # 移除管理员权限
                    user.role &= ~User_info.PERMISSION_ADMIN
            user.save()
            self.logger.info(
                f"用户 {current_user.username} (ID: {current_user.id})已{action}用户 '{user.username}' (ID: {user.id}){permission}权限 ")
            flash("权限已变更")
            return redirect(url_for('user_admin'))


        except User_info.DoesNotExist:
            self.logger.error(f"操作时用户不存在: {session.get('username')}")
            flash("用户信息错误")
            return redirect(url_for('user_admin'))