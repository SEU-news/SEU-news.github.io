import logging

from flask import render_template, request, session, redirect, url_for, flash
from flask.views import MethodView

from common.content_status import ContentStatus
from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content, User_info


class DescribeView(MethodView):
    """
    描述内容视图类，专门处理image和url，将draft草稿状态转为pending待审核状态

    处理内容描述的GET和POST请求。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]  # 应用登录_required装饰器

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

    def get(self, entry_id):
        """
        处理GET请求，显示描述内容页面

        参数:
            entry_id (int): 内容条目ID

        返回:
            render_template: 描述页面模板
        """
        try:
            content = Content.objects.get(id=entry_id)
            self.logger.info(f"用户 {session.get('username')} 正在编辑内容 ID: {entry_id}")
        except Content.DoesNotExist:
            self.logger.warning(f"尝试访问不存在的内容 ID: {entry_id}")
            return redirect(url_for('main'))
        return render_template('describe.html', entry=content)

    def post(self, entry_id):
        """
        处理POST请求，执行内容描述逻辑

        参数:
            entry_id (int): 内容条目ID

        返回:
            redirect: 处理完成后重定向到主页面
        """
        # 从表单获取数据
        title = request.form['title']
        entry_type = request.form['entry_type']
        description = request.form['description']
        due_time_str = request.form['due_time']
        tag = request.form.get('tag', '')
        short_title = request.form.get('short_title') or title
        # link不可能做更新，所以不需要重新获取

        # 处理死线日期
        deadline_value = None
        if due_time_str and due_time_str.strip():
            deadline_value = due_time_str

        # 获取当前用户
        user = User_info.objects.get(username=session['username'])

        try:
            # 尝试获取现有内容
            content = Content.objects.get(id=entry_id)

            # 更新内容字段
            content.describer_id = user.id
            content.title = title
            content.short_title = short_title
            content.content = description
            content.type = entry_type
            content.tag = tag
            content.deadline = deadline_value

            # 使用ContentStatus控制状态转移: draft->pending
            status_manager = ContentStatus(content.status)
            if status_manager.submit():
                content.status = status_manager.string_en()
                content.save()
                self.logger.info(
                    f"用户 {user.username} 更新了内容 ID {entry_id}: {title}，状态已更新为 {content.status}")
            else:
                self.logger.warning(
                    f"用户 {user.username} 尝试更新内容 ID {entry_id} 时状态转换失败，当前状态: {content.status}")

        except Content.DoesNotExist:
            # 不应该创建新内容，这种情况应该由upload.py处理
            self.logger.error(f"用户 {user.username} 尝试更新不存在的内容 ID: {entry_id}")
            flash("内容不存在，请先上传内容")

        return redirect(url_for('main'))
