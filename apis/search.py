import logging

from django.db.models import Q
from flask import request, render_template
from flask.views import MethodView

from common.decorator.permission_required import login_required
from django_models.models import Content


class SearchView(MethodView):
    """
    搜索内容视图类

    处理内容搜索请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self):
        """
        处理GET请求，执行内容搜索逻辑

        返回:
            render_template: 搜索结果页面
        """
        page = request.args.get('page', default=1, type=int)
        page_size = 5
        offset = (page - 1) * page_size
        query = request.args.get('q', '').strip()
        results = []
        total_pages = 0

        if query:
            total_count = Content.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).count()
            total_pages = (total_count + page_size - 1) // page_size

            # Get paginated results
            results = Content.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).order_by('created_at')[offset:offset + page_size]

            logging.info(f"搜索查询: '{query}', 找到 {total_count} 条结果")

        return render_template('search.html', query=query, results=results, page=page, total_pages=total_pages)
