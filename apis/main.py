import logging

from flask import session, render_template
from flask.views import MethodView

from common.decorator.permission_required import login_required
from django_models.models import Content, User_info


class MainView(MethodView):
    """
    主页面视图类

    处理主页面的GET请求，显示所有内容条目。
    """

    decorators = [login_required]  # 应用装饰器到整个视图类

    def get(self):
        """
        处理GET请求，显示主页面

        获取所有内容条目并按更新时间倒序排列，处理状态显示和权限控制。

        返回:
            render_template: 主页面模板，包含内容条目列表
        """
        contents = Content.objects.select_related().all().order_by('-updated_at')

        status_map = {
            'pending': '待审核',
            'published': '已发布',
            'reviewed': '已审核',
            'rejected': '已拒绝',
            'draft': '草稿'
        }

        try:
            current_user = User_info.objects.get(username=session['username'])
            current_user_id = current_user.id
        except User_info.DoesNotExist:
            current_user_id = None

        for content in contents:
            if content.created_at:
                content.formatted_created_at = content.created_at.strftime('%m-%d %H:%M')
            else:
                content.formatted_created_at = ''

            if content.updated_at:
                content.formatted_updated_at = content.updated_at.strftime('%m-%d %H:%M')
            else:
                content.formatted_updated_at = ''

            content.status_display = status_map.get(content.status, content.status)

            content.creator_id = content.creator_id
            content.describer_id = content.describer_id
            content.reviewer_id = content.reviewer_id

            content.can_delete = (current_user_id == content.creator_id)

            logging.debug(f"Content ID: {content.id}, Status: {content.status}, Display: {content.status_display}")

        return render_template('main.html', entries=contents)
