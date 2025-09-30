"""
SEU News API注册和应用配置文件

该文件负责创建和配置Flask应用实例，包括:
- 应用基本配置（密钥、会话超时等）
- 路由注册（将URL映射到相应的视图类）
- 导入所有视图模块并注册对应的URL规则

主要功能模块包括:
- 用户认证（登录、注册、登出）
- 内容管理（上传、编辑、删除、搜索）
- 内容发布（预览、发布、格式转换）
- 系统管理（添加截止日期等）
"""

import logging
import os
from datetime import timedelta

# Flask相关导入
from flask import Flask

# 本地视图导入
from apis.add_deadline import AddDeadlineView
from apis.cancel import CancelView
from apis.content_delete import DeleteEntryView
from apis.describe import DescribeView
from apis.latex import LatexView
from apis.login import LoginView
from apis.logout import LogoutView
from apis.main import MainView
from apis.upload_url import UploadUrlView
from apis.preview_edit import PreviewEditView
from apis.publish import PublishView
from apis.register import RegisterView
from apis.review import ReviewView
from apis.search import SearchView
from apis.typst import TypstView
from apis.upload import UploadView
from apis.upload_images import UploadImageView
from apis.admin import AdminView
from apis.user_admin import UserAdminView

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='A_SECRET_KEY_HERE',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        # 其他配置，如数据库连接等
    )

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except FileExistsError:
        pass

    # 注册蓝图或类视图
    app.add_url_rule('/login', view_func=LoginView.as_view('login'))
    app.add_url_rule('/register', view_func=RegisterView.as_view('register'))
    app.add_url_rule('/', view_func=MainView.as_view('main'))
    app.add_url_rule('/upload', view_func=UploadView.as_view('upload'), methods=['GET', 'POST'])
    app.add_url_rule('/describe/<int:entry_id>', view_func=DescribeView.as_view('describe'), methods=['GET', 'POST'])
    app.add_url_rule('/review/<int:entry_id>', view_func=ReviewView.as_view('review'), methods=['GET', 'POST'])
    app.add_url_rule('/cancel/<int:entry_id>', view_func=CancelView.as_view('cancel'))
    app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
    app.add_url_rule('/paste', view_func=UploadUrlView.as_view('paste'), methods=['POST'])
    app.add_url_rule('/upload_image', view_func=UploadImageView.as_view('upload_image'), methods=['POST'])
    app.add_url_rule('/typst/<date>', view_func=TypstView.as_view('typst_pub'))
    app.add_url_rule('/preview_edit', view_func=PreviewEditView.as_view('preview_edit'))
    app.add_url_rule('/latex/<date>', view_func=LatexView.as_view('latex_entries'))
    app.add_url_rule('/delete/<int:entry_id>', view_func=DeleteEntryView.as_view('delete_entry'), methods=['POST'])
    app.add_url_rule('/add_deadline', view_func=AddDeadlineView.as_view('add_deadline'), methods=['GET', 'POST'])
    app.add_url_rule('/publish', view_func=PublishView.as_view('publish'), methods=['GET', 'POST'])
    app.add_url_rule('/admin', view_func=AdminView.as_view('admin'), methods=['GET'])
    app.add_url_rule('/user_admin', view_func=UserAdminView.as_view('user_admin'), methods=['GET'])
    return app


if __name__ == '__main__':
    logging.info("已迁移到cmd.py")
