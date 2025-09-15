from flask import render_template
from flask.views import MethodView


class PreviewEditView(MethodView):
    """
    预览编辑视图类

    处理预览编辑页面的请求。
    """

    def get(self):
        """
        处理GET请求，显示预览编辑页面

        返回:
            render_template: 预览编辑页面模板
        """
        return render_template("preview_edit.html")
