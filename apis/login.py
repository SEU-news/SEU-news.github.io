import hashlib
import logging

from flask import render_template, request, flash, session, redirect, url_for
from flask.views import MethodView

from django_models.models import User_info


class LoginView(MethodView):
    """登录类视图"""

    def get(self):
        """处理 GET 请求，展示登录页面"""
        return render_template('login.html')

    def post(self):
        """处理 POST 请求，验证登录信息"""
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('请填写用户名和密码')
            return render_template('login.html')

        try:
            user = User_info.objects.get(username=username)
            input_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

            if user.password_MD5 == input_hash:
                session.permanent = True  # 设置持久会话
                session['username'] = username
                logging.info(f"用户登录成功: {username}")
                return redirect(url_for('main'))
            else:
                logging.warning(f"用户登录失败，密码错误: {username}")
                flash('Invalid username or password')
        except User_info.DoesNotExist:
            logging.warning(f"用户登录失败，用户不存在: {username}")
            flash('Invalid username or password')

        return render_template('login.html')
