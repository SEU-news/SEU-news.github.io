import json
import logging
import os
import subprocess

from flask import render_template, request, flash
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from config.load_config import GLOBAL_CONFIG


class PublishView(MethodView):
    """
    发布内容视图类

    处理发布内容管理页面的请求。
    """

    decorators = [PermissionDecorators.editor_required]  # 应用editor_required装饰器
    json_path = "./static/latest.json"
    # 添加typst模板路径类属性
    typst_template_path = "news_template.typ"
    # 添加字体目录和PDF输出路径类属性
    fonts_dir = "./fonts"
    pdf_path = "./static/latest.pdf"

    def __init__(self):
        os_name = GLOBAL_CONFIG.get_config_value("os.name")
        # 添加系统命令路径类属性
        self.typst_cmd = "typst.exe" if os_name == "windows" else "./typst"

    def get(self):
        """
        处理GET请求，显示发布内容管理页面

        返回:
            render_template: 发布内容管理页面模板
        """
        content = ""
        # 修复：使用self.json_path访问类属性
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                content = f.read()
        return render_template("publish.html", content=content)

    def post(self):
        """
        处理POST请求，执行发布内容管理逻辑

        返回:
            render_template: 发布内容管理页面模板
        """
        new_content = request.form.get("content", "")

        os.makedirs("./archived", exist_ok=True)
        os.makedirs("./static", exist_ok=True)

        # 统一使用类属性路径
        with open(self.json_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        try:
            parsed = json.loads(new_content)
            # 写入归档文件
            with open(
                "./archived/" + parsed["data"]["date"] + ".json", "w", encoding="utf-8"
            ) as f:
                f.write(new_content)

            try:
                # 检查当前系统并选择相应的typst命令
                typst_cmd = [
                    self.typst_cmd,
                    "compile",
                    "--font-path",
                    self.fonts_dir,
                    self.typst_template_path,
                    self.pdf_path,
                ]
                subprocess.run(typst_cmd, check=True)
                logging.info(f"成功编译typst文件，日期: {parsed['data']['date']}")
                flash("内容发布成功，PDF已生成")
            except subprocess.CalledProcessError as e:
                logging.error(f"typst编译失败: {str(e)}")
                flash(
                    "Compilation failed. Please check typst installation and source file."
                )
            except FileNotFoundError:
                logging.error("typst命令未找到")
                flash("Typst not found. Please install typst or check the path.")

        except json.JSONDecodeError as e:
            logging.error(f"JSON解析失败: {str(e)}")
            flash("Invalid JSON format in content.")
        except KeyError as e:
            logging.error(f"JSON格式错误，缺少必要字段: {str(e)}")
            flash("Invalid JSON structure. Missing required fields.")
        except Exception as e:
            logging.error(f"发布过程中出现错误: {str(e)}")
            flash(f"发布失败: {str(e)}")

        return render_template("publish.html", content=new_content)
