import logging

from flask import session, render_template, request
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content, User_info


class MainView(MethodView):
    """
    主页面视图类

    处理主页面的GET请求，显示所有内容条目。
    """

    decorators = [PermissionDecorators.login_required]  # 应用装饰器到整个视图类

    def get(self):
        """
        处理GET请求，显示主页面

        获取所有内容条目并按更新时间倒序排列，处理状态显示和权限控制。

        返回:
            render_template: 主页面模板，包含内容条目列表
        """

        # 懒加载
        qs = Content.objects.select_related().all().order_by('-updated_at')
        total = qs.count()  # 总条数

        # 当前页
        page = int(request.args.get('page', 1))

        # 默认每页条数
        page_size = 10
        legal_provisions = [5, 10, 20, 50]
        try:
            # 尝试从请求获取用户输入
            page_size = int(request.args.get('page_size', page_size))
            page_size = int(page_size)  # 转成数字
            if page_size not in legal_provisions:
                raise ValueError(f"非法 page_size: {page_size}")
            if total < page_size:
                page_size = max([x for x in legal_provisions if x <= total], default=None)
                logging.warning(f"用户选择了主页展示的 page_size 小于 总条目, 调整为: {page_size}")
            else: logging.info(f"用户选择了主页展示的 page_size: {page_size}")
        except (ValueError, TypeError) as e:
            logging.warning(f"用户请求了非法 page_size，使用默认值20。错误信息: {e}")
            page_size = 10

        # 计算偏移
        offset = (page - 1) * page_size

        # 一次查出所有行
        # contents = Content.objects.select_related().all().order_by('-updated_at')

        # 分页
        contents = qs[offset:offset + page_size]  # 当前页数据
        total_pages = (total + page_size - 1) // page_size

        # 当前页附近页码
        nearby_start = max(1, page - 2)
        nearby_end = min(total_pages, page + 2)

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

        return render_template(
            'main.html',
            entries=contents,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            nearby_start=nearby_start,
            nearby_end=nearby_end,
        )
