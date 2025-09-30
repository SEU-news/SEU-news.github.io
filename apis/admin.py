import logging

from flask import session, render_template, request
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content, User_info


class AdminView(MethodView):

    decorators = [PermissionDecorators.admin_required]# 应用装饰器到整个视图类

    def get(self):
        """
        处理GET请求，显示主页面

        获取所有内容条目并按更新时间倒序排列，处理状态显示和权限控制。

        返回:
            render_template: 主页面模板，包含内容条目列表
        """
        # 获取排序参数，默认按 created_at 降序
        sort_field = request.args.get('sort_field', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 只允许我们定义好的字段，避免注入
        allowed_fields = ['created_at', 'updated_at']
        if sort_field not in allowed_fields:
            sort_field = 'created_at'

        order_by = f"-{sort_field}" if sort_order == 'desc' else sort_field

        # 搜索关键字
        query = request.args.get('q', '').strip()

        # 懒加载 + 排序
        qs = Content.objects.select_related().all().order_by(order_by)
        if query:
            qs = qs.filter(title__icontains=query)
        total = qs.count()  # 总条数

        # 当前页
        page = int(request.args.get('page', default=1, type=int))

        legal_provisions = [10, 20, 50, 100]
        try:
            # 尝试从请求获取用户输入
            page_size = request.args.get('page_size', default=10)
            page_size = int(page_size)  # 转成数字
            if page_size not in legal_provisions:
                raise ValueError(f"非法 page_size: {page_size}")
            if total == 0:
                page_size = legal_provisions[0]  # 总条目为0时默认取最小值
            elif total < page_size:
                page_size = min([x for x in legal_provisions if x >= total], default=legal_provisions[-1])
                logging.warning(f"用户选择了主页展示的 page_size 小于 总条目, 调整为: {page_size}")
            else:
                logging.info(f"用户选择了主页展示的 page_size: {page_size}")
        except (ValueError, TypeError) as e:
            page_size = 10  # 默认每页条数
            logging.warning(f"用户请求了非法 page_size，使用默认值 {page_size}。错误信息: {e}")

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
        #获取权限

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
            'admin.html',
            entries=contents,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            nearby_start=nearby_start,
            nearby_end=nearby_end,
            query=query,
        )