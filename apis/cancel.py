from flask import redirect, url_for
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators


class CancelView(MethodView):
    """
    取消操作视图类

    处理取消操作请求。
    """

    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

    def get(self, entry_id):
        """
        处理GET请求，取消操作并返回主页

        参数:
            entry_id (int): 内容条目ID

        返回:
            redirect: 重定向到主页面
        """
        return redirect(url_for('main'))
