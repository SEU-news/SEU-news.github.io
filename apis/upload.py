import logging
from datetime import datetime

from flask import render_template, request, session, flash, redirect, url_for
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import User_info, Content


class UploadView(MethodView):
    """
    上传内容视图类

    处理内容上传的GET和POST请求。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]  # 应用登录_required装饰器

    def get(self):
        """
        处理GET请求，显示上传内容页面

        返回:
            render_template: 上传页面模板
        """
        return render_template('upload.html')

    def post(self):
        """
        处理POST请求，执行内容上传逻辑

        从表单获取内容信息，进行处理后创建新内容条目。

        返回:
            redirect: 上传成功重定向到主页面
        """
        title = request.form['title']
        description = request.form['description']
        due_time = request.form.get('due_time', '').strip()
        entry_type = request.form['entry_type']
        tag = request.form.get('tag', '')
        short_title = request.form.get('short_title') or title

        try:
            user = User_info.objects.get(username=session['username'])
        except User_info.DoesNotExist:
            flash('User not found. Please log in again.')
            return redirect(url_for('login'))

        deadline_value = None
        if due_time:
            try:
                if len(due_time) == 10:  # "YYYY-MM-DD"
                    deadline_value = datetime.strptime(due_time, '%Y-%m-%d')
                else:
                    deadline_value = datetime.fromisoformat(due_time)
            except ValueError:
                flash('Invalid date format for deadline')
                return render_template('upload.html')

        if deadline_value is None:
            deadline_value = datetime(2099, 12, 31)

        content = Content.objects.create(
            creator_id=user.id,
            describer_id=user.id,
            title=title,
            short_title=short_title,
            content=description,
            link='',
            status='pending',
            type=entry_type,
            tag=tag,
            deadline=deadline_value,
            publish_at=datetime.now()
        )

        logging.info(f"用户 {user.username} 创建了新内容: {title}")
        return redirect(url_for('main'))
