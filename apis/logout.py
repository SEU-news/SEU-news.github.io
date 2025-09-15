import logging

from flask import session, redirect, url_for
from flask.views import MethodView


class LogoutView(MethodView):
    """
    用户登出视图类

    处理用户登出请求。
    """

    def get(self):
        """
        处理GET请求，执行用户登出操作

        返回:
            redirect: 重定向到登录页面
        """
        username = session.get('username', 'unknown')
        session.pop('username', None)
        logging.info(f"用户登出: {username}")
        return redirect(url_for('login'))
