import logging
from datetime import datetime
from urllib.parse import urlparse

from flask import request, flash, redirect, url_for, session
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from common.methods.fetch_title import fetch_title
from common.methods.is_valid_url import is_valid_url
from django_models.models import Content, User_info


class PasteView(MethodView):
    """
    粘贴链接视图类

    处理粘贴链接并自动获取标题的请求。
    """

    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

    def post(self):
        """
        处理POST请求，粘贴链接并自动获取标题

        返回:
            redirect: 重定向到主页面
        """
        link = request.form['link'].strip()
        if not link or not is_valid_url(link):
            flash('请输入有效的地址')
            return redirect(url_for('main'))
        parsed = urlparse(link)
        canonical_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if Content.objects.filter(link=canonical_url).exists():
            flash("该链接已经上传")
            return redirect(url_for('main'))
        title = fetch_title(link)
        logging.info(f"获取链接标题: {title} from {link}")

        # Get user ID
        user = User_info.objects.get(username=session['username'])

        entry = Content.objects.create(
            creator_id=user.id,
            title=title,
            short_title=title,
            content='',
            link=canonical_url,
            deadline=datetime(2099, 12, 31),
            publish_at=datetime.now(),
            status='draft',
            type='活动预告',
            tag=''  # Add required field
        )
        logging.info(f"用户 {user.username} 通过链接创建了内容: {title}")
        flash('地址添加成功')
        return redirect(url_for('main'))
