from flask import redirect, url_for, request, flash
from flask.views import MethodView
from common.decorator.permission_required import PermissionDecorators
from django_models.models import User_info
import hashlib
import logging

class PasswordChangeView(MethodView):
    """
    取消操作视图类

    处理取消操作请求。
    """

    decorators = [PermissionDecorators.admin_required, PermissionDecorators.login_required]  # 应用登录_required装饰器

    def post(self):

        try:
            # 获取前端提交的数据
            user_id = request.form['user_id']
            new_password = request.form['new_password']

            # 验证数据
            if not user_id or not new_password:
                flash('用户ID和新密码不能为空.')
                return redirect('user_admin')  # 重定向到用户管理页面

            # 获取用户对象
            user = User_info.objects.get(id=user_id)

            user.password_MD5 = hashlib.md5(new_password.encode('utf-8')).hexdigest()
            user.save()

            # 成功消息
            logging.info(f'用户 {user.username} 的密码已成功修改')

        except Exception as e:
            # 错误处理
            logging.warning(f'修改密码时发生错误: {str(e)}')
            flash('修改密码时发生错误')
        return redirect(url_for('user_admin'))