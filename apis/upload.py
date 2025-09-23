import logging
from datetime import datetime

from flask import render_template, request, session, flash, redirect, url_for
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from common.database.content import ContentService
from django_models.models import User_info, Content


class UploadView(MethodView):
    """
    上传内容视图类

    处理内容上传的GET和POST请求，需要登录和编辑权限。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]

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

        try:
            # 从表单中提取内容信息
            ContentService.create(
                title=request.form['title'],
                content_text=request.form['description'],
                username=session['username'],
                type=request.form['entry_type'],
                due_time=request.form.get('due_time', '').strip(),
                tag=request.form.get('tag', ''),
                short_title=request.form.get('short_title',None)
            )
            return redirect(url_for('main'))
        except User_info.DoesNotExist:
            flash('User not found. Please log in again.')
            return redirect(url_for('login'))
        except (ValueError, Exception) as e:
            logging.error(f"创建内容时发生错误: {str(e)}")
            flash(str(e) if isinstance(e, ValueError) else '创建内容时发生错误')
            return render_template('upload.html')