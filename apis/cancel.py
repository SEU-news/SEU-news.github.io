import logging
from flask import redirect, url_for, flash, request, session
from flask.views import MethodView
from django.db import transaction

from common.decorator.permission_required import PermissionDecorators
from common.content_status import STATUS_DRAFT
from django_models.models import Content, User_info


class CancelView(MethodView):
    """
    取消操作视图类

    处理取消操作请求，将内容状态转为草稿状态。
    """

    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

    def get(self, entry_id):
        """
        处理GET请求，将内容状态转为草稿状态并返回主页

        参数:
            entry_id (int): 内容条目ID

        返回:
            redirect: 重定向到主页面
        """
        try:
            with transaction.atomic():
                content = Content.objects.select_for_update().get(id=entry_id)
                current_user = User_info.objects.get(username=session['username'])
                
                self.logger.info(
                    f"用户 {current_user.username}(ID:{current_user.id}) 开始取消内容(ID:{content.id})，原状态: {content.status}")

                # 将条目状态设置为草稿状态
                content.status = STATUS_DRAFT
                content.reviewer_id = current_user.id
                content.save(update_fields=['status', 'reviewer_id'])
                
                self.logger.info(
                    f"取消完成，内容ID: {content.id}，新状态: {content.status}，操作者: {current_user.username}")
                flash("内容已取消并转为草稿状态")
                
        except Content.DoesNotExist:
            self.logger.warning(f"尝试取消不存在的内容，ID: {entry_id}")
            flash("内容不存在")
        except User_info.DoesNotExist:
            self.logger.error(f"用户不存在: {session.get('username')}")
            flash("用户不存在，请重新登录")
            return redirect(url_for('login'))
        except Exception as e:
            self.logger.error(f"取消操作失败: {str(e)}")
            flash("操作失败")
            
        return redirect(url_for('main'))