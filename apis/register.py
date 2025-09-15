import hashlib
import logging

from django.db import IntegrityError
from flask import render_template, request, flash, redirect, url_for
from flask.views import MethodView

from django_models.models import User_info


class RegisterView(MethodView):
    """
    用户注册视图类

    处理用户注册的GET和POST请求，提供注册表单展示和用户创建功能。
    """

    def get(self):
        """
        处理GET请求，显示注册表单页面

        返回:
            render_template: 注册页面模板
        """
        return render_template('register.html')

    def post(self):
        """
        处理POST请求，执行用户注册逻辑

        从表单获取用户名和密码，进行验证后创建新用户。

        返回:
            redirect: 注册成功重定向到登录页面，失败则返回注册页面
        """
        username = request.form['username']
        password = request.form['password']

        # 基础验证
        if not username or not password:
            flash('用户名和密码不能为空')
            return render_template('register.html')

        if len(password) < 6:  # 添加密码长度检查
            flash('密码长度至少6位')
            return render_template('register.html')

        # 检查用户名是否已存在（提前验证）
        if User_info.objects.filter(username=username).exists():
            flash('用户名已存在')
            return render_template('register.html')

        # 创建用户
        try:
            # 先创建基础用户对象
            user = User_info(
                username=username,
                password_MD5=hashlib.md5(password.encode('utf-8')).hexdigest()
            )
            # 设置其他必填字段的默认值
            user.avatar = ''  # 设置默认头像
            user.realname = ''  # 设置空默认值
            user.student_id = ''  # 设置空默认值
            user.role = User_info.PERMISSION_NONE  # 设置默认权限

            # 保存用户对象
            user.save()

            logging.info(f"用户注册成功: {username}")
            flash('注册成功！请登录')
            return redirect(url_for('login'))

        except IntegrityError:
            # 作为备用错误处理
            logging.error(f"用户注册失败，数据库错误: {username}")
            flash('注册失败，请重试')
            return render_template('register.html')
