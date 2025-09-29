import logging

from flask import session, flash, redirect, url_for
from flask.views import MethodView

from common.content_status import ContentStatus
from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content, User_info


class DeleteEntryView(MethodView):
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
            # 检查是否有编辑或管理员权限
            if not (current_user.has_editor_permission() or current_user.has_admin_permission()):
                self.logger.warning(f"用户 {current_user.username} 尝试删除内容但没有足够权限")
                flash("你没有权限执行此操作")
                return redirect(url_for('main'))
        except User_info.DoesNotExist:
            self.logger.error(f"删除操作时用户不存在: {session.get('username')}")
            flash("用户信息错误，请重新登录")
            return redirect(url_for('login'))

        try:
            content = Content.objects.get(id=entry_id)
            current_user = User_info.objects.get(username=session['username'])

            # 使用ContentStatus类处理状态转换
            content_status = ContentStatus(content.status)
            # 尝试使用abandon方法(从draft到terminated)或archive方法(从published到terminated)
            if not (content_status.abandon() or content_status.archive()):
                self.logger.warning(f"内容 ID: {entry_id} 状态 {content.status} 无法转换为terminated状态")
                flash("当前状态下无法删除此项目")
                return redirect(url_for('main'))

            # 应用状态转换结果
            content.status = content_status.string_en()
            content.save(update_fields=['status', 'updated_at'])

            self.logger.info(
                f"用户 {current_user.username} 将内容 '{content.title}' (ID: {entry_id}) 状态设置为terminated")
            flash("条目已删除")
            return redirect(url_for('main'))

        except Content.DoesNotExist:
            self.logger.warning(f"尝试删除不存在的内容ID: {entry_id}")
            flash("条目不存在")
            return redirect(url_for('main'))
        except User_info.DoesNotExist:
            self.logger.error(f"删除操作时用户不存在: {session.get('username')}")
            flash("用户信息错误，请重新登录")
            return redirect(url_for('login'))
