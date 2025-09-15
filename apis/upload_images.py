import hashlib
import logging
import os
from datetime import datetime

from flask import request, flash, redirect, url_for, session, current_app
from flask.views import MethodView

from common.allowed_file import allowed_file
from common.decorator.permission_required import login_required
from django_models.models import User_info, Content
from global_static import FILE_PATH


class UploadImageView(MethodView):
    """
    上传图片视图类

    处理图片上传请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def post(self):
        """
        处理POST请求，执行图片上传逻辑

        返回:
            redirect: 重定向到主页面
        """
        if 'image' not in request.files:
            flash("没有文件上传")
            return redirect(url_for('main'))
        file = request.files['image']
        if file.filename == '':
            flash("未选择文件")
            return redirect(url_for('main'))

            # 修复：检查文件大小的方法

        if file and allowed_file(file.filename):
            filename = file.filename

            # 检查是否已存在相同文件名的内容
            user = User_info.objects.get(username=session['username'])
            existing_content = Content.objects.filter(
                title=filename
            )
            if existing_content:
                flash("该图片已经上传")
                return redirect(url_for('main'))
            filename, extension = os.path.splitext(file.filename)
            md5_hash = hashlib.md5(filename.encode('utf-8')).hexdigest()
            link = f"{md5_hash}{extension}"
            upload_folder = os.path.join(current_app.root_path, FILE_PATH)
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, link)
            file.save(file_path)
            try:
                # 创建新的Content对象
                content = Content(
                    creator_id=user.id,
                    describer_id=user.id,
                    title=md5_hash,
                    deadline=datetime(2099, 12, 31),
                    publish_at=datetime.now(),
                    link=link,
                    status='draft',
                    type='活动预告'
                )

                # 添加图片到image_list
                if content.add_image(file_path):
                    content.save()
                    logging.info(f"用户 {user.username} 上传了图片: {filename}")
                    flash("图片上传成功，并已添加到数据库")
                else:
                    logging.error(f"图片处理失败: {filename}")
                    flash("图片处理失败")

            except Exception as e:
                logging.error(f"保存图片失败: {str(e)}")
                flash(f"保存失败: {str(e)}")
            return redirect(url_for('main'))

        else:
            flash("不支持的文件格式")
            return redirect(url_for('main'))
