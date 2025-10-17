import logging
from datetime import datetime

from django.db import transaction
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
        try:
            with transaction.atomic():
                content = Content.objects.select_for_update().get(id=entry_id)
                current_user = User_info.objects.get(username=session['username'])
                
                self.logger.info(
                    f"用户 {current_user.username}(ID:{current_user.id}) 开始描述内容(ID:{content.id})，原状态: {content.status}")

                # 获取表单数据
                title = request.form.get('title', '').strip() or content.title
                description = request.form.get('description', '').strip() or content.content
                due_time_str = request.form.get('due_time', '').strip()
                entry_type = request.form.get('entry_type', '').strip() or content.type
                tag = request.form.get('tag', '').strip()
                short_title = request.form.get('short_title', '').strip() or content.short_title

                self.logger.debug(f"获取表单数据完成，标题: {title}, 类型: {entry_type}")

                # 处理截止日期
                deadline_value = content.deadline
                if due_time_str:
                    try:
                        deadline_value = datetime.strptime(due_time_str, '%Y-%m-%d').date()
                    except ValueError:
                        self.logger.warning(f"无效的日期格式: {due_time_str}")
                        flash("日期格式错误")
                        return render_template('describe.html', entry=content)

                # 更新内容字段
                content.describer_id = current_user.id
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
                    content.save(update_fields=['describer_id', 'title', 'short_title', 'content', 
                                              'type', 'tag', 'deadline', 'status', 'updated_at'])
                    self.logger.info(
                        f"描述完成，内容ID: {content.id}，新状态: {content.status}，操作者: {current_user.username}")
                    flash("内容已更新并提交审核")
                else:
                    self.logger.warning(
                        f"用户 {current_user.username} 尝试更新内容 ID {entry_id} 时状态转换失败，当前状态: {content.status}")
                    flash("当前状态下无法提交审核")

        except Content.DoesNotExist:
            # 不应该创建新内容，这种情况应该由upload.py处理
            self.logger.error(f"用户 {session.get('username')} 尝试更新不存在的内容 ID: {entry_id}")
            flash("内容不存在，请先上传内容")
            return redirect(url_for('main'))
        except User_info.DoesNotExist:
            self.logger.error(f"用户不存在: {session.get('username')}")
            flash("用户不存在，请重新登录")
            return redirect(url_for('login'))
        except Exception as e:
            self.logger.error(f"描述操作失败: {str(e)}")
            flash("操作失败")

        return redirect(url_for('main'))