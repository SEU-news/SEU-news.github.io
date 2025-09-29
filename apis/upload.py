import logging
from datetime import datetime

from django.utils import timezone
from flask import render_template, request, session, flash, redirect, url_for
from flask.views import MethodView

from common.content_status import STATUS_PENDING
from common.decorator.permission_required import PermissionDecorators
from django_models.models import User_info, Content


class UploadView(MethodView):
    """
    上传内容视图类

    处理内容上传的GET和POST请求，需要登录和编辑权限。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

    def get(self):
        """
        处理GET请求，显示上传内容页面

        Returns:
            render_template: 上传页面模板
        """
        return render_template('upload.html')

    def post(self):
        """
        处理POST请求，执行内容上传逻辑

        从表单获取内容信息，进行验证后创建新内容条目。

        Returns:
            redirect: 上传成功重定向到主页面，失败时重定向回上传页面
        """
        # 从表单中提取内容信息
        title = request.form['title']
        content_text = request.form['description']
        username = session['username']
        content_type = request.form['entry_type']
        due_time = request.form.get('due_time', '').strip()
        tag = request.form.get('tag', '')
        short_title = request.form.get('short_title') or title

        # 获取当前登录用户信息
        try:
            user = User_info.objects.get(username=username)
        except User_info.DoesNotExist:
            self.logger.error(f"用户 {username} 不存在，请重新登录")
            flash('User not found. Please log in again.')
            return redirect(url_for('login'))

        # 处理截止时间，支持两种格式: YYYY-MM-DD 或 ISO标准格式
        deadline = None  # 默认截止时间
        if due_time:
            try:
                if len(due_time) == 10:  # "YYYY-MM-DD"格式
                    deadline = datetime.strptime(due_time, '%Y-%m-%d')
                    deadline = timezone.make_aware(deadline)
                else:  # ISO标准格式
                    deadline = datetime.fromisoformat(due_time)
                    # 注意：fromisoformat可能已经包含时区信息，如果没有则添加上海时区
                    if deadline.tzinfo is None:
                        deadline = timezone.make_aware(deadline)
            except ValueError:
                self.logger.warning(f"用户 {user.username} 提供了无效的截止时间格式: {due_time}")
                flash('Invalid date format for deadline')
                return render_template('upload.html')

        # 创建新的内容记录
        try:
            content = Content.objects.create(
                creator_id=user.id,
                describer_id=user.id,
                title=title,
                short_title=short_title,
                content=content_text,
                link='',
                status=STATUS_PENDING,
                type=content_type,
                tag=tag,
                deadline=deadline,
            )

            # 记录内容创建操作的日志
            self.logger.info(f"用户 {user.username} 创建了新内容 ID: {content.id} {title}")
        except Exception as e:
            self.logger.error(f"创建内容时发生错误: {str(e)}")
            flash('创建内容时发生错误，请稍后重试')
            return render_template('upload.html')

        return redirect(url_for('main'))
