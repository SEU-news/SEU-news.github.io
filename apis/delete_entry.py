import logging

from flask import session, flash, redirect, url_for
from flask.views import MethodView

from common.decorator.permission_required import login_required
from django_models.models import Content, User_info


class DeleteEntryView(MethodView):
    """
    删除内容条目视图类

    处理删除内容条目的请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def post(self, entry_id):
        """
        处理POST请求，删除内容条目

        参数:
            entry_id (int): 内容条目ID

        返回:
            redirect: 重定向到主页面
        """
        try:
            content = Content.objects.get(id=entry_id)
            current_user = User_info.objects.get(username=session['username'])

            if content.creator_id != current_user.id:
                flash("你没有权限删除此条目，仅可删除自己上传的条目")
                return redirect(url_for('main'))
            content.delete()
            logging.info(f"用户 {current_user.username} 删除了内容: {content.title}")
            flash("条目已删除")
            return redirect(url_for('main'))
        except Content.DoesNotExist:
            logging.warning(f"尝试删除不存在的内容ID: {entry_id}")
            flash("条目不存在")
            return redirect(url_for('main'))
        except User_info.DoesNotExist:
            logging.error(f"删除操作时用户不存在: {session.get('username')}")
            flash("用户信息错误，请重新登录")
            return redirect(url_for('login'))
