import logging
from datetime import datetime

from django.utils import timezone
from flask import render_template, request, session, flash, redirect, url_for
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import User_info, Content


class AddDeadlineView(MethodView):
    """
    添加截止日期视图类

    处理添加截止日期条目的请求。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]  # 应用登录_required装饰器

    def get(self):
        """
        处理GET请求，显示添加截止日期页面

        返回:
            render_template: 添加截止日期页面模板
        """
        today = timezone.now().strftime("%Y-%m-%d")
        return render_template('add_deadline.html', today=today)

    def post(self):
        """
        处理POST请求，执行添加截止日期逻辑

        返回:
            redirect: 重定向到主页面
        """
        link = request.form.get('link', '').strip()
        link_value = link if link else None
        short_title = request.form.get('short_title', '').strip()
        tag = request.form.get('tag', '').strip()
        today = timezone.now().strftime("%Y-%m-%d")
        publish_time = request.form.get('publish_time', today)
        due_time = request.form.get('due_time', today)

        user = User_info.objects.get(username=session['username'])

        publish_datetime = datetime.strptime(publish_time, '%Y-%m-%d') if publish_time else None
        deadline_datetime = datetime.strptime(due_time, '%Y-%m-%d') if due_time else None

        # 为publish_datetime和deadline_datetime添加时区信息
        if publish_datetime:
            publish_datetime = timezone.make_aware(publish_datetime)
        if deadline_datetime:
            deadline_datetime = timezone.make_aware(deadline_datetime)

        news = Content.objects.create(
            creator_id=user.id,
            describer_id=user.id,
            title=short_title,
            link=link_value,
            short_title=short_title,
            content='',
            deadline=deadline_datetime,
            publish_at=publish_datetime,
            status='pending',
            tag=tag,
            type="DDLOnly",
        )
        logging.info(f"用户 {user.username} 添加了截止日期条目: {short_title}")
        flash("Deadline entry added successfully")
        return redirect(url_for('main'))
