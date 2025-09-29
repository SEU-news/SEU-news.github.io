import hashlib
import logging
import os


from flask import request, flash, redirect, url_for, session, current_app
from flask.views import MethodView

from common.content_status import STATUS_DRAFT
from common.decorator.permission_required import PermissionDecorators
from common.global_static import UPLOAD_FILE_PATH
from common.methods.allowed_file import allowed_image
from django_models.models import User_info, Content


class UploadImageView(MethodView):
    """
    上传图片视图类

    处理图片上传请求。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]  # 应用登录_required装饰器

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

    def post(self):
        """
        处理POST请求，执行图片上传逻辑

        返回:
            redirect: 重定向到主页面
        """
        if 'image' not in request.files:
            self.logger.info("用户尝试上传图片但未选择文件")
            flash("没有文件上传")
            return redirect(url_for('main'))
        file = request.files['image']
        if file.filename == '':
            self.logger.info("用户未选择文件")
            flash("未选择文件")
            return redirect(url_for('main'))

        username = session['username']
        if file and allowed_image(file.filename):
            filename = file.filename

            # 检查是否已存在相同文件名的内容
            user = User_info.objects.get(username)

            # 使用文件名作为标题
            title = os.path.splitext(filename)[0]

            # 生成基于文件名和文件内容的hash值，用于创建新的唯一文件名
            file_content = file.read()
            file_hash = hashlib.md5(filename.encode('utf-8') + file_content).hexdigest()

            # 重置文件指针到开始位置，以便后续保存文件
            file.seek(0)

            # 获取文件扩展名并创建新的文件名
            _, extension = os.path.splitext(filename)
            new_filename = f"{file_hash}{extension}"

            # 创建当月的文件夹
            now = datetime.now()
            month_folder = now.strftime("%Y-%m")
            upload_folder = os.path.join(current_app.root_path, UPLOAD_FILE_PATH, month_folder)
            os.makedirs(upload_folder, exist_ok=True)

            # 保存文件到服务器
            file_path = os.path.join(upload_folder, new_filename)
            file.save(file_path)

            try:
                # 创建新的Content对象
                content = Content(
                    creator_id=user.id,
                    describer_id=user.id,
                    title=title,  # 使用原始文件名（不含扩展名）作为标题
                    short_title=title,
                    content='',
                    status=STATUS_DRAFT,
                    type='新建Images'
                )

                # 添加图片到image_list
                if content.add_image(file_path):
                    content.save()
                    self.logger.info(
                        f"用户 {user.username} 上传了图片: {filename}，保存为: {os.path.join(month_folder, new_filename)}")
                    flash("图片上传成功，并已添加到数据库")
                else:
                    self.logger.error(f"图片处理失败: {filename}")
                    flash("图片处理失败")

            except Exception as e:
                self.logger.error(f"保存图片失败: {str(e)}")
                flash(f"保存失败: {str(e)}")
            return redirect(url_for('main'))

        else:
            self.logger.warning(f"用户 {username} 尝试上传不支持的文件格式: {file.filename}")
            flash("不支持的文件格式")
            return redirect(url_for('main'))
