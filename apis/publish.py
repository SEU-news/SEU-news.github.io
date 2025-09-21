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

    decorators = [PermissionDecorators.editor_required]
    json_path = "./static/latest.json"
    # 添加typst模板路径类属性
    typst_template_path = "news_template.typ"
    # 添加字体目录和PDF输出路径类属性
    fonts_dir = "./fonts"
    pdf_path = "./static/latest.pdf"

    def __init__(self):
        try:
            os_name = GLOBAL_CONFIG.get_config_value("os.name")
            # 添加系统命令路径类属性
            self.typst_cmd = "typst.exe" if os_name == "windows" else "./typst"
        except Exception as e:
            logging.error(f"初始化PublishView时获取配置失败: {str(e)}")
            # 设置默认值
            self.typst_cmd = "./typst"
        # 初始化logger实例
        self.logger = logging.getLogger(__name__)

    def get(self):
        """
        处理GET请求，显示发布内容管理页面

        返回:
            render_template: 发布内容管理页面模板
        """
        content = ""
        try:
            # 修复：使用self.json_path访问类属性
            if os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as f:
                    content = f.read()
        except FileNotFoundError:
            self.logger.warning(f"JSON文件未找到: {self.json_path}")
            flash("内容文件未找到")
        except PermissionError:
            self.logger.error(f"没有权限读取文件: {self.json_path}")
            flash("没有权限读取内容文件")
        except Exception as e:
            self.logger.error(f"读取内容时发生未知错误: {str(e)}")
            flash("读取内容时发生错误")
        return render_template("publish.html", content=content)

    def post(self):
        """
        处理POST请求，执行发布内容管理逻辑

        返回:
            render_template: 发布内容管理页面模板
        """
        new_content = request.form.get("content", "")

        try:
            os.makedirs("./archived", exist_ok=True)
            os.makedirs("./static", exist_ok=True)
        except PermissionError:
            self.logger.error("没有权限创建目录")
            flash("没有权限创建必要的目录")
            return render_template("publish.html", content=new_content)
        except Exception as e:
            self.logger.error(f"创建目录时发生错误: {str(e)}")
            flash("创建目录时发生错误")
            return render_template("publish.html", content=new_content)

        try:
            # 统一使用类属性路径
            with open(self.json_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except PermissionError:
            self.logger.error(f"没有权限写入文件: {self.json_path}")
            flash("没有权限写入内容文件")
            return render_template("publish.html", content=new_content)
        except Exception as e:
            self.logger.error(f"写入内容文件时发生错误: {str(e)}")
            flash("保存内容时发生错误")
            return render_template("publish.html", content=new_content)

        try:
            parsed = json.loads(new_content)
            # 写入归档文件
            try:
                with open(
                        "./archived/" + parsed["data"]["date"] + ".json", "w", encoding="utf-8"
                ) as f:
                    f.write(new_content)
            except KeyError as e:
                self.logger.error(f"JSON格式错误，缺少必要字段: {str(e)}")
                flash("JSON结构错误，缺少日期字段")
                return render_template("publish.html", content=new_content)
            except PermissionError:
                self.logger.error("没有权限写入归档文件")
                flash("没有权限写入归档文件")
                return render_template("publish.html", content=new_content)
            except Exception as e:
                self.logger.error(f"写入归档文件时发生错误: {str(e)}")
                flash("保存归档文件时发生错误")
                return render_template("publish.html", content=new_content)

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
                result = subprocess.run(typst_cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    self.logger.info(f"成功编译typst文件，日期: {parsed['data']['date']}")
                    flash("内容发布成功，PDF已生成")
                else:
                    self.logger.error(f"typst编译失败: {result.stderr}")
                    flash("PDF生成失败，请检查内容格式")
            except subprocess.TimeoutExpired:
                self.logger.error("typst编译超时")
                flash("PDF生成超时，请稍后重试")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"typst编译失败: {str(e)}")
                flash("PDF生成失败，请检查内容格式")
            except FileNotFoundError:
                self.logger.error("typst命令未找到")
                flash("PDF生成工具未找到，请联系管理员")
            except Exception as e:
                self.logger.error(f"执行PDF生成时发生未知错误: {str(e)}")
                flash("生成PDF时发生未知错误")

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            flash("内容格式错误，不是有效的JSON格式")
        except KeyError as e:
            self.logger.error(f"JSON格式错误，缺少必要字段: {str(e)}")
            flash("JSON结构错误，缺少必要字段")
        except Exception as e:
            self.logger.error(f"发布过程中出现错误: {str(e)}")
            flash(f"发布失败: {str(e)}")

        return render_template("publish.html", content=new_content)
