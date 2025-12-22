import logging
from urllib.parse import urlparse

from flask import request, flash, redirect, url_for, session
from flask.views import MethodView

from common.content_status import STATUS_DRAFT
from common.decorator.permission_required import PermissionDecorators
from common.methods.fetch_title import fetch_title
from common.methods.is_valid_url import is_valid_url
from common.methods.save_context import get_main_page_context
from django_models.models import Content, User_info


class UploadUrlView(MethodView):
    """
    粘贴链接视图类

    处理粘贴链接并自动获取标题的请求。
    """

    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

    def post(self):
        """
        处理POST请求，粘贴链接并自动获取标题

        返回:
            redirect: 重定向到主页面
        """
        link = request.form['link'].strip()
        if not link or not is_valid_url(link):
            self.logger.info("用户尝试上传链接但未提供有效地址")
            flash('请输入有效的地址')
            context_id = request.args.get('context_id')
            page_params = get_main_page_context(context_id)
            return redirect(url_for(
                'main',
                page=page_params['page'],
                page_size=page_params['page_size'],
                q=page_params['q'],
                sort_field=page_params['sort_field'],
                sort_order=page_params['sort_order']
            ))

        parsed = urlparse(link)
        canonical_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        title = fetch_title(link)
        self.logger.info(f"获取链接标题: {title} from {link}")

        # Get user ID
        try:
            user = User_info.objects.get(username=session['username'])
        except User_info.DoesNotExist:
            self.logger.error(f"用户 {session['username']} 不存在")
            flash('用户不存在，请重新登录')
            context_id = request.args.get('context_id')
            page_params = get_main_page_context(context_id)
            return redirect(url_for(
                'main',
                page=page_params['page'],
                page_size=page_params['page_size'],
                q=page_params['q'],
                sort_field=page_params['sort_field'],
                sort_order=page_params['sort_order']
            ))

        try:
            Content.objects.create(
                creator_id=user.id,
                describer_id=user.id,
                title=title,
                short_title=title,
                content='',
                link=canonical_url,
                status=STATUS_DRAFT,
                type='新建URL',
            )
            self.logger.info(f"用户 {user.username} 通过链接创建了内容: {title}")
            flash('地址添加成功')
        except Exception as e:
            self.logger.error(f"保存链接失败: {str(e)}")
            flash(f"保存失败: {str(e)}")

        context_id = request.args.get('context_id')
        page_params = get_main_page_context(context_id)
        return redirect(url_for(
            'main',
            page=page_params['page'],
            page_size=page_params['page_size'],
            q=page_params['q'],
            sort_field=page_params['sort_field'],
            sort_order=page_params['sort_order']
        ))
