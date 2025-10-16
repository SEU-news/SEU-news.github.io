from flask import redirect, url_for, flash
from flask.views import MethodView
from django.db import transaction

from common.decorator.permission_required import PermissionDecorators
from common.content_status import STATUS_DRAFT
from django_models.models import Content


class CancelView(MethodView):
    """
    取消操作视图类

    处理取消操作请求，将内容状态转为草稿状态。
    """

    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

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
                entry = Content.objects.select_for_update().get(id=entry_id)
                # 将条目状态设置为草稿状态
                entry.status = STATUS_DRAFT
                entry.save(update_fields=['status'])
                flash("内容已取消并转为草稿状态")
        except Content.DoesNotExist:
            flash("内容不存在")
        except Exception:
            flash("操作失败")
            
        return redirect(url_for('main'))