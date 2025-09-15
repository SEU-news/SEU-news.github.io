import json
import logging
import os
import subprocess

from flask import render_template, request, flash
from flask.views import MethodView

from common.decorator.permission_required import editor_required


class PublishView(MethodView):
    """
    发布内容视图类

    处理发布内容管理页面的请求。
    """

    decorators = [editor_required]  # 应用editor_required装饰器

    def get(self):
        """
        处理GET请求，显示发布内容管理页面

        返回:
            render_template: 发布内容管理页面模板
        """
        content = ""
        if os.path.exists("latest.json"):
            with open("latest.json", "r") as f:
                content = f.read()
        return render_template("publish.html", content=content)

    def post(self):
        """
        处理POST请求，执行发布内容管理逻辑

        返回:
            render_template: 发布内容管理页面模板
        """
        new_content = request.form.get("content", "")
        with open("./latest.json", "w") as f:
            f.write(new_content)
        parsed = json.loads(new_content)
        with open("./archived/" + parsed["data"]["date"] + ".json", "w") as f:
            f.write(new_content)
        try:
            subprocess.run(
                ["./typst", "compile", "--font-path", "/home/nik_nul/font", "news_template.typ", "./static/latest.pdf"],
                check=True)
            logging.info(f"成功编译typst文件，日期: {parsed['data']['date']}")
        except subprocess.CalledProcessError as e:
            logging.error(f"typst编译失败: {str(e)}")
            flash("Compilation failed. Please check typst installation and source file.")
        return render_template("publish.html", content=new_content)
