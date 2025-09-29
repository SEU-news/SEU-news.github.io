from flask import render_template


def register_error_handlers(app):
    """
    注册应用的错误处理器

    参数:
        app (Flask): Flask应用实例
    """

    @app.errorhandler(400)
    def bad_request(e):
        """
        处理400错误请求

        参数:
            e (Exception): 错误异常对象

        返回:
            tuple: 渲染的模板和HTTP状态码
        """
        return render_template('400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        """
        处理401未授权错误

        参数:
            e (Exception): 错误异常对象

        返回:
            tuple: 渲染的模板和HTTP状态码
        """
        return render_template('401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        """
        处理403禁止访问错误

        参数:
            e (Exception): 错误异常对象

        返回:
            tuple: 渲染的模板和HTTP状态码
        """
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        """
        处理404错误

        参数:
            e (Exception): 错误异常对象

        返回:
            tuple: 渲染的模板和HTTP状态码
        """
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """
        处理500服务器内部错误

        参数:
            e (Exception): 错误异常对象

        返回:
            tuple: 渲染的模板和HTTP状态码
        """
        return render_template('500.html'), 500