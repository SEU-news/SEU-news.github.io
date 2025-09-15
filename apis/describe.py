from flask import render_template, request, session, redirect, url_for
from flask.views import MethodView

from common.decorator.permission_required import login_required
from django_models.models import Content, User_info


class DescribeView(MethodView):
    """
    描述内容视图类

    处理内容描述的GET和POST请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self, entry_id):
        """
        处理GET请求，显示描述内容页面

        参数:
            entry_id (int): 内容条目ID

        返回:
            render_template: 描述页面模板
        """
        try:
            entry = Content.objects.get(id=entry_id)
        except Content.DoesNotExist:
            entry = None
        return render_template('describe.html', entry=entry)

    def post(self, entry_id):
        """
        处理POST请求，执行内容描述逻辑

        参数:
            entry_id (int): 内容条目ID

        返回:
            redirect: 处理完成后重定向到主页面
        """
        title = request.form['title']
        entry_type = request.form['entry_type']
        description = request.form['description']
        due_time_str = request.form['due_time']
        tag = request.form.get('tag', '')
        short_title = request.form.get('short_title') or title
        link = request.form.get('link')
        user = User_info.objects.get(username=session['username'])
        deadline_value = None
        if due_time_str and due_time_str.strip():
            deadline_value = due_time_str
        content_data = {
            'creator_id': user.id,
            'describer_id': user.id,
            'title': title,
            'short_title': short_title,
            'content': description,
            'status': 'pending',
            'type': entry_type,
            'tag': tag,
        }
        if deadline_value is not None:
            content_data['deadline'] = deadline_value
        try:
            content = Content.objects.get(id=entry_id)
        except Content.DoesNotExist:
            content = Content.objects.create(**content_data)
            return redirect(url_for('main'))
        content.describer_id = content_data.get('describer_id', content.describer_id)
        content.title = content_data.get('title', content.title)
        content.short_title = content_data.get('short_title', content.short_title)
        content.content = content_data.get('content', content.content)
        content.status = content_data.get('status', content.status)
        content.type = content_data.get('type', content.type)
        content.tag = content_data.get('tag', content.tag)
        content.deadline = content_data.get('deadline', content.deadline)
        content.save()  # 保存更改
        return redirect(url_for('main'))
