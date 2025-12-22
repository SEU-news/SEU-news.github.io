from flask import redirect, url_for, request
from flask.views import MethodView
from common.methods.save_context import get_main_page_context
from common.decorator.permission_required import PermissionDecorators


class CancelView(MethodView):
    """
    取消操作视图类

    处理取消操作请求。
    """

    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

    def get(self, entry_id):
        """
               处理GET请求，取消操作并返回主页面的原位置
               """
        # 1. 获取上下文ID
        context_id = request.args.get('context_id')
        # 2. 获取所有验证后的参数（自动处理默认值和二次验证）
        page_params = get_main_page_context(context_id)
        # 3. 重定向到主页面，携带所有参数（与你的MainView参数一致）
        return redirect(url_for(
            'main',  # 你的MainView的路由名称（请确保与实际注册的名称一致）
            page=page_params['page'],
            page_size=page_params['page_size'],
            q=page_params['q'],
            sort_field=page_params['sort_field'],
            sort_order=page_params['sort_order']
        ))
