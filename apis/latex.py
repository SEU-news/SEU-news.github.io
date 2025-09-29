# 不知道干嘛的，什么用呢？

import logging

from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content


class LatexView(MethodView):
    """
    LaTeX内容视图类

    处理生成LaTeX格式内容的请求。
    """

    decorators = [PermissionDecorators.login_required]  # 应用登录_required装饰器

    def get(self, date):
        """
        处理GET请求，生成LaTeX格式的内容

        参数:
            date (str): 日期字符串

        返回:
            str: LaTeX格式的内容
        """
        content = Content.objects.filter(publish_at__date=date)

        def escape_latex(text):
            """转义LaTeX特殊字符"""
            if not text:
                return ""
            text = text.replace('\\', r'\textbackslash{}')
            special_chars = {
                '&': r'\&',
                '%': r'\%',
                '$': r'\$',
                '#': r'\#',
                '_': r'\_',
                '{': r'\{',
                '}': r'\}',
                '~': r'\textasciitilde{}',
                '^': r'\^{}',
            }
            for char, replacement in special_chars.items():
                text = text.replace(char, replacement)
            return text

        latex_output = ""
        for content_item in content:
            title = content_item.title
            tag = content_item.tag
            link = content_item.link
            describer = content_item.describer_id
            description = content_item.content
            title = escape_latex(title)
            title = title.rstrip('\r\n')
            description = escape_latex(description).replace('\n', r'\\')
            if tag in ["讲座", "院级活动", "社团活动"]:
                latex_output += r"\subsection{" + title + "} % " + tag + " describer: " + str(describer) + "\n"
            else:
                latex_output += r"\section{" + title + "} % " + tag + " describer: " + str(describer) + "\n"
            latex_output += description + "\n"
            if link and len(link) > 10:
                latex_output += "\\\\详见：" + r"\url{" + link + "}" + "\n\n"

        logging.info(f"生成LaTeX内容，日期: {date}")
        return latex_output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
