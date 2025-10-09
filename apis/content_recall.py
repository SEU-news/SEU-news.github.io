import logging

from flask import session, flash, redirect, url_for
from flask.views import MethodView

from common.content_status import STATUS_DRAFT
from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content, User_info

class RecallEntryView(MethodView):
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

    def post(self, entry_id):
        """
        处理POST请求，将内容条目状态设置为terminated（软删除）

        参数:
            entry_id (int): 内容条目ID

        返回:
            redirect: 重定向到主页面
        """
        # 手动检查用户权限（编辑或管理员权限）
        if 'username' not in session:
            return redirect(url_for('login'))

        try:
            current_user = User_info.objects.get(username=session['username'])
            # 检查是否有管理员权限
            if not current_user.has_admin_permission():
                self.logger.warning(f"用户 {current_user.username} 尝试删除内容但没有足够权限")
                flash("你没有权限执行此操作")
                return redirect(url_for('admin'))
        except User_info.DoesNotExist:
            self.logger.error(f"召回操作时用户不存在: {session.get('username')}")
            flash("用户信息错误，请重新登录")
            return redirect(url_for('login'))

        try:
            content = Content.objects.get(id=entry_id)
            current_user = User_info.objects.get(username=session['username'])
            if current_user.has_admin_permission():
                content.status = STATUS_DRAFT
                content.save(update_fields=['status', 'updated_at'])
            self.logger.info(
                f"用户 {current_user.username} 将内容 '{content.title}' (ID: {entry_id}) 状态设置为draft")
            flash("条目已召回")
            return redirect(url_for('admin'))

        except Content.DoesNotExist:
            self.logger.warning(f"尝试召回不存在的内容ID: {entry_id}")
            flash("条目不存在")
            return redirect(url_for('admin'))
        except User_info.DoesNotExist:
            self.logger.error(f"召回操作时用户不存在: {session.get('username')}")
            flash("用户信息错误，请重新登录")
            return redirect(url_for('login'))