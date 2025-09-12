import copy
import hashlib
import json
import logging
import os
import re
import subprocess
from datetime import timedelta
from functools import wraps
from urllib.parse import urlparse

import django
import requests
from bs4 import BeautifulSoup
from django.db import IntegrityError
from django.db.models import Q
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from django.db import transaction

from django_config import configure_django

from django.utils import timezone

from datetime import datetime

import logging
import traceback




def get_timezone_aware_datetime(date_str):
    """将字符串日期转换为时区感知的datetime对象"""
    naive_dt = datetime.strptime(date_str, '%Y-%m-%d')
    return timezone.make_aware(naive_dt)


# 配置日志系统
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

configure_django()
django.setup()

from django_models.models import User_info, Content

app = Flask(__name__)
app.secret_key = 'A_SECRET_KEY_HERE'
app.permanent_session_lifetime = timedelta(days=7)

EMAIL_ADDRESS = "test@smail.nju.edu.cn"
EMAIL_PASSWORD = "A_SECRET_KEY_HERE"
SMTP_SERVER = "smtp.exmail.qq.com"
SMTP_PORT = 465
FILE_PATH = 'static/uploads'


def fetch_title(url):
    """从URL获取网页标题"""
    for _ in range(2):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            with requests.get(url, headers=headers, stream=True, timeout=5) as response:
                response.raise_for_status()
                partial_content = ""
                for chunk in response.iter_content(chunk_size=4096):
                    partial_content += chunk.decode('utf-8', errors='replace')
                    if "</head>" in partial_content.lower():
                        soup = BeautifulSoup(partial_content, 'html.parser')
                        meta_tag = soup.find("meta", property="og:title")
                        if meta_tag and meta_tag.get("content"):
                            return meta_tag.get("content")
                        title_tag = soup.find("title")
                        if title_tag and title_tag.string:
                            return title_tag.string.strip()
            soup = BeautifulSoup(partial_content, 'html.parser')
            meta_tag = soup.find("meta", property="og:title")
            if meta_tag and meta_tag.get("content"):
                return meta_tag.get("content")
        except Exception as e:
            logging.warning(f"获取标题失败，URL: {url}, 错误: {str(e)}")
    return "标题获取失败"


EDITOR_LIST = ["editor1", "editor2", "111"]
ADMIN_LIST = ["admin", "222", "111"]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

LINK_REGEX = re.compile(
    r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)")


def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def hash_file(file_obj):
    """计算文件的MD5哈希值"""
    file_obj.seek(0)
    file_content = file_obj.read()
    file_hash = hashlib.md5(file_content).hexdigest()
    file_obj.seek(0)
    return file_hash


def is_valid_url(url):
    """验证URL格式是否正确"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def login_required(f):
    """装饰器：要求用户登录"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """装饰器：要求管理员权限"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        username = session.get('username')

        if not username:
            abort(401)

        user = User_info.objects.filter(username=username).first()

        if not user or not user.has_admin_permission():
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


def editor_required(f):
    """装饰器：要求编辑权限"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        username = session.get('username')

        if not username:
            abort(401)

        user = User_info.objects.filter(username=username).first()

        # 如果用户不存在或没有权限，都返回403
        if not user or not user.has_editor_permission():
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录页面"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('请填写用户名和密码')
            return render_template('login.html')

        try:
            user = User_info.objects.get(username=username)
            # 计算输入密码的MD5
            input_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
            # 比较哈希值
            if user.password_MD5 == input_hash:
                session.permanent = True
                session['username'] = username
                logging.info(f"用户登录成功: {username}")
                return redirect(url_for('main'))
            else:
                logging.warning(f"用户登录失败，密码错误: {username}")
                flash('Invalid username or password')
        except User_info.DoesNotExist:
            logging.warning(f"用户登录失败，用户不存在: {username}")
            flash('Invalid username or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
# @admin_required
def register():
    """用户注册页面"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 基础验证
        if not username or not password:
            flash('用户名和密码不能为空')
            return render_template('register.html')

        if len(password) < 6:  # 添加密码长度检查
            flash('密码长度至少6位')
            return render_template('register.html')

        # 检查用户名是否已存在（提前验证）
        if User_info.objects.filter(username=username).exists():
            flash('用户名已存在')
            return render_template('register.html')

        # 创建用户
        try:
            # 先创建基础用户对象
            user = User_info(
                username=username,
                password_MD5=hashlib.md5(password.encode('utf-8')).hexdigest()
            )
            # 设置其他必填字段的默认值
            user.avatar = ''  # 设置默认头像
            user.realname = ''  # 设置空默认值
            user.student_id = ''  # 设置空默认值
            user.role = User_info.PERMISSION_NONE  # 设置默认权限

            # 保存用户对象
            user.save()

            logging.info(f"用户注册成功: {username}")
            flash('注册成功！请登录')
            return redirect(url_for('login'))

        except IntegrityError:
            # 作为备用错误处理
            logging.error(f"用户注册失败，数据库错误: {username}")
            flash('注册失败，请重试')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/')
@login_required
def main():
    """主页面，显示所有内容"""
    contents = Content.objects.select_related().all().order_by('-updated_at')

    status_map = {
        'pending': '待审核',
        'published': '已发布',
        'reviewed': '已审核',
        'rejected': '已拒绝',
        'draft': '草稿'
    }

    try:
        current_user = User_info.objects.get(username=session['username'])
        current_user_id = current_user.id
    except User_info.DoesNotExist:
        current_user_id = None

    for content in contents:
        if content.created_at:
            content.formatted_created_at = content.created_at.strftime('%m-%d %H:%M')
        else:
            content.formatted_created_at = ''

        if content.updated_at:
            content.formatted_updated_at = content.updated_at.strftime('%m-%d %H:%M')
        else:
            content.formatted_updated_at = ''

        content.status_display = status_map.get(content.status, content.status)

        content.creator_id = content.creator_id
        content.describer_id = content.describer_id
        content.reviewer_id = content.reviewer_id

        content.can_delete = (current_user_id == content.creator_id)

        logging.debug(f"Content ID: {content.id}, Status: {content.status}, Display: {content.status_display}")

    return render_template('main.html', entries=contents)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """上传新内容页面"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_time = request.form.get('due_time', '').strip()
        entry_type = request.form['entry_type']
        tag = request.form.get('tag', '')
        short_title = request.form.get('short_title') or title

        try:
            user = User_info.objects.get(username=session['username'])
        except User_info.DoesNotExist:
            flash('User not found. Please log in again.')
            return redirect(url_for('login'))

        from datetime import datetime, timedelta

        deadline_value = None
        if due_time:
            try:
                if len(due_time) == 10:  # "YYYY-MM-DD"
                    deadline_value = datetime.strptime(due_time, '%Y-%m-%d')
                else:
                    deadline_value = datetime.fromisoformat(due_time)
            except ValueError:
                flash('Invalid date format for deadline')
                return render_template('upload.html')

        if deadline_value is None:
            deadline_value = datetime(2099, 12, 31)

        content = Content.objects.create(
            creator_id=user.id,
            describer_id=user.id,
            title=title,
            short_title=short_title,
            content=description,
            link='',
            status='pending',
            type=entry_type,
            tag=tag,
            deadline=deadline_value,
            publish_at=datetime.now()
        )

        logging.info(f"用户 {user.username} 创建了新内容: {title}")
        return redirect(url_for('main'))

    return render_template('upload.html')


# @app.route('/describe/<int:entry_id>', methods=['GET', 'POST'])
# @login_required
# def describe(entry_id):
#     if request.method == 'POST':
#         title = request.form['title']
#         entry_type = request.form['entry_type']
#         description = request.form['description']
#         due_time = request.form['due_time']
#         use_image = 1 if request.form.get('use_image') == 'on' else 0
#         tag = request.form.get('tag')
#         short_title = request.form.get('short_title') or title
#         content = Content.objects.create(
#             uploader=session['username'],
#             describer=session['username'],
#             title=title,
#             short_title=short_title,
#             content=description,
#             status='pending',
#             type=entry_type,
#             tag=tag,
#             deadline=due_time
#         )
#         return redirect(url_for('main'))
#     else:
#         try:
#             entry = Content.objects.get(id=entry_id)
#         except Content.DoesNotExist:
#             entry = None
#
#         return render_template('describe.html', entry=entry)


@app.route('/describe/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def describe(entry_id):
    if request.method == 'POST':
        title = request.form['title']
        entry_type = request.form['entry_type']
        description = request.form['description']
        due_time_str = request.form['due_time']
        tag = request.form.get('tag', '')
        short_title = request.form.get('short_title') or title
        link = request.form.get('link')
        user = User_info.objects.get(username=session['username'])
        deadline_value = None
        if due_time_str and due_time_str.strip():
            deadline_value = due_time_str
        content_data = {
            'creator_id': user.id,
            'describer_id': user.id,
            'title': title,
            'short_title': short_title,
            'content': description,
            'status': 'pending',
            'type': entry_type,
            'tag': tag,
        }
        if deadline_value is not None:
            content_data['deadline'] = deadline_value
        try:
            content = Content.objects.get(id=entry_id)
        except Content.DoesNotExist:
            content = Content.objects.create(**content_data)
            return redirect(url_for('main'))
        content.describer_id = content_data.get('describer_id', content.describer_id)
        content.title = content_data.get('title', content.title)
        content.short_title = content_data.get('short_title', content.short_title)
        content.content = content_data.get('content', content.content)
        content.status = content_data.get('status', content.status)
        content.type = content_data.get('type', content.type)
        content.tag = content_data.get('tag', content.tag)
        content.deadline = content_data.get('deadline', content.deadline)
        content.save()  # 保存更改
        return redirect(url_for('main'))
    else:
        try:
            entry = Content.objects.get(id=entry_id)
        except Content.DoesNotExist:
            entry = None
        return render_template('describe.html', entry=entry)


@app.route('/review/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def review(entry_id):
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            logging.info(f"开始处理审核请求，entry_id: {entry_id}, action: {action}")

            if not action:
                flash("未指定操作")
                return redirect(url_for('main'))

            with transaction.atomic():
                content = Content.objects.select_for_update().get(id=entry_id)
                current_user = User_info.objects.get(username=session['username'])

                logging.info(f"审核前状态: {content.status}")
                logging.info(f"当前用户: {current_user.username}, ID: {current_user.id}")

                if ((current_user.id == content.describer_id or current_user.id == content.creator_id)
                        and action == "approve"):
                    flash("不可审核自己所写的内容！")
                    return render_template('review.html', entry=content)

                title = request.form.get('title', '').strip() or content.title
                description = request.form.get('description', '').strip() or content.content
                due_time_str = request.form.get('due_time', '').strip()
                entry_type = request.form.get('entry_type', '').strip() or content.type
                tag = request.form.get('tag', '').strip()
                short_title = request.form.get('short_title', '').strip() or content.short_title

                due_time = content.deadline
                if due_time_str:
                    try:
                        from datetime import datetime
                        due_time = datetime.strptime(due_time_str, '%Y-%m-%d').date()
                    except ValueError:
                        flash("日期格式错误")
                        return render_template('review.html', entry=content)

                original_deadline = content.deadline.strftime('%Y-%m-%d') if content.deadline else ''
                new_deadline = due_time.strftime('%Y-%m-%d') if due_time else ''

                is_modified = any([
                    content.title != title,
                    content.content != description,
                    original_deadline != new_deadline,
                    content.type != entry_type,
                    (content.tag or '') != tag,
                    (content.short_title or '') != short_title
                ])

                logging.info(f"内容是否被修改: {is_modified}")

                if action == 'approve':
                    if is_modified:
                        flash("内容已作出修改，无法直接批准。请使用'修改并审核'按钮。")
                        return render_template('review.html', entry=content)

                    content.reviewer_id = current_user.id
                    content.status = 'reviewed'
                    content.save(update_fields=['reviewer_id', 'status', 'updated_at'])
                    flash("内容已批准")

                elif action == 'modify':
                    content.reviewer_id = current_user.id
                    content.status = 'reviewed'
                    content.title = title
                    content.content = description
                    content.deadline = due_time
                    content.type = entry_type
                    content.tag = tag
                    content.short_title = short_title
                    content.save()
                    flash("内容已修改并审核通过")

                elif action == 'publish':
                    content.reviewer_id = current_user.id
                    content.status = 'published'
                    if is_modified:
                        content.title = title
                        content.content = description
                        content.deadline = due_time
                        content.type = entry_type
                        content.tag = tag
                        content.short_title = short_title
                    content.save()
                    flash("内容已发布")

                elif action == 'reject':
                    content.reviewer_id = current_user.id
                    content.status = 'rejected'
                    content.save(update_fields=['reviewer_id', 'status', 'updated_at'])
                    flash("内容已拒绝")

                else:
                    flash(f"未知操作: {action}")
                    return render_template('review.html', entry=content)

                # 强制刷新以获取最新状态
                content.refresh_from_db()
                logging.info(f"审核后状态: {content.status}")
                logging.info(f"审核者ID: {content.reviewer_id}")

        except Content.DoesNotExist:
            logging.error(f"内容不存在，ID: {entry_id}")
            flash("内容不存在")
            return redirect(url_for('main'))
        except User_info.DoesNotExist:
            logging.error(f"用户不存在: {session.get('username')}")
            flash("用户不存在，请重新登录")
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"审核操作失败: {str(e)}")
            logging.error(traceback.format_exc())
            flash(f"操作失败: {str(e)}")
            try:
                content = Content.objects.get(id=entry_id)
                return render_template('review.html', entry=content)
            except:
                return redirect(url_for('main'))

        return redirect(url_for('main'))

    else:
        try:
            entry = Content.objects.get(id=entry_id)
            return render_template('review.html', entry=entry)
        except Content.DoesNotExist:
            flash("内容不存在")
            return redirect(url_for('main'))


@app.route('/cancel/<int:entry_id>')
@login_required
def cancel(entry_id):
    """取消操作，返回主页"""
    return redirect(url_for('main'))


@app.route('/logout')
def logout():
    """用户登出"""
    username = session.get('username', 'unknown')
    session.pop('username', None)
    logging.info(f"用户登出: {username}")
    return redirect(url_for('login'))


#
# @app.route('/change_password', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     if request.method == 'POST':
#         original_password = request.form.get('original_password')
#         new_password = request.form.get('new_password')
#         confirm_password = request.form.get('confirm_password')
#         if new_password != confirm_password:
#             flash("New passwords do not match")
#             return redirect(url_for('change_password'))
#         conn = sqlite3.connect('database.db')
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE username=?", (session['username'],))
#         user = c.fetchone()
#         if user and check_password_hash(user[2], original_password):
#             c.execute("UPDATE users SET password=? WHERE username=?", (generate_password_hash(new_password), session['username']))
#             conn.commit()
#             flash("Password successfully updated. Please log in again.")
#             session.pop('username', None)
#             conn.close()
#             return redirect(url_for('login'))
#         else:
#             flash("Original password is incorrect")
#             conn.close()
#         return redirect(url_for('change_password'))
#     return render_template('change_password.html')
#

@app.route('/paste', methods=['POST'])
@login_required
def paste():
    """粘贴链接并自动获取标题"""
    link = request.form['link'].strip()
    if not link or not is_valid_url(link):
        flash('请输入有效的地址')
        return redirect(url_for('main'))
    parsed = urlparse(link)
    canonical_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if Content.objects.filter(link=canonical_url).exists():
        flash("该链接已经上传")
        return redirect(url_for('main'))
    title = fetch_title(link)
    logging.info(f"获取链接标题: {title} from {link}")

    # Get user ID
    user = User_info.objects.get(username=session['username'])

    entry = Content.objects.create(
        creator_id=user.id,
        title=title,
        short_title=title,
        content='',
        link=canonical_url,
        deadline=datetime(2099, 12, 31),
        publish_at=None,
        status='draft',
        type='活动预告',
        tag=''  # Add required field
    )
    logging.info(f"用户 {user.username} 通过链接创建了内容: {title}")
    flash('地址添加成功')
    return redirect(url_for('main'))


@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    """上传图片"""
    if 'image' not in request.files:
        flash("没有文件上传")
        return redirect(url_for('main'))
    file = request.files['image']
    if file.filename == '':
        flash("未选择文件")
        return redirect(url_for('main'))

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
        upload_folder = os.path.join(app.root_path, FILE_PATH)
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, link)
        file.save(file_path)
        try:
            # 创建新的Content对象
            content = Content(
                creator_id=user.id,
                describer_id=user.id,
                title=md5_hash,
                deadline=None,
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


#
# @app.route('/admin')
# @editor_required
# def admin():
#     page = request.args.get('page', default=1, type=int)
#     page_size = 12
#     offset = (page - 1) * page_size
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("SELECT COUNT(*) FROM entries")
#     total_count = c.fetchone()[0]
#     total_pages = (total_count + page_size - 1) // page_size
#     c.execute("SELECT * FROM entries ORDER BY upload_time DESC LIMIT ? OFFSET ?", (page_size, offset))
#     entries = c.fetchall()
#     conn.close()
#     default_publish_date = datetime.now().strftime("%Y-%m-%d")
#     return render_template('admin.html', entries=entries, page=page, total_pages=total_pages, default_publish_date=default_publish_date)
#
# @app.route('/admin/edit/<int:entry_id>', methods=['GET', 'POST'])
# @admin_required
# def admin_edit(entry_id):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     if request.method == 'POST':
#         uploader = request.form['uploader']
#         upload_time = request.form['upload_time']
#         title = request.form['title']
#         link = request.form['link']
#         description = request.form['description']
#         describer = request.form['describer']
#         reviewer = request.form['reviewer']
#         due_time = request.form['due_time']
#         status = request.form['status']
#         entry_type = request.form['entry_type']
#         c.execute("""UPDATE entries SET uploader=?, upload_time=?, title=?, link=?, description=?, describer=?, reviewer=?, due_time=?, status=?, type=? WHERE id=?""",
#                   (uploader, upload_time, title, link, description, describer, reviewer, due_time, status, entry_type, entry_id))
#         conn.commit()
#         conn.close()
#         flash("条目已更新")
#         return redirect(url_for('admin'))
#     else:
#         c.execute("SELECT * FROM entries WHERE id=?", (entry_id,))
#         entry = c.fetchone()
#         conn.close()
#         return render_template('admin_edit.html', entry=entry)
#
# @app.route('/admin/delete/<int:entry_id>', methods=['POST'])
# @admin_required
# def admin_delete(entry_id):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("DELETE FROM entries WHERE id=?", (entry_id,))
#     conn.commit()
#     conn.close()
#     flash("条目已删除")
#     return redirect(url_for('admin'))
#
# @app.route('/admin/publish', methods=['POST'])
# @editor_required
# def admin_publish():
#     entry_ids = request.form.getlist("entry_ids")
#     publish_time_input = request.form.get("publish_time")
#     if not entry_ids:
#         flash("请至少选择一个条目")
#         return redirect(url_for('admin'))
#     try:
#         publish_time = datetime.strptime(publish_time_input, "%Y-%m-%d")
#     except (ValueError, TypeError):
#         publish_time = datetime.now()
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     for eid in entry_ids:
#         c.execute("UPDATE entries SET publish_date=? WHERE id=?", (publish_time, eid))
#     conn.commit()
#     conn.close()
#     flash("选定条目的发布时间已更新")
#     return redirect(url_for('admin'))
#
# @app.route('/admin/publish_today', methods=['POST'])
# @editor_required
# def admin_publish_today():
#     publish_time = datetime.now().date()
#     today = datetime.now().date()
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("UPDATE entries SET publish_date=? WHERE date(upload_time)=?", (publish_time, today))
#     conn.commit()
#     conn.close()
#     flash("今天上传的条目的发布时间已更新")
#     return redirect(url_for('admin'))
#
# @app.route('/admin/unpublish', methods=['POST'])
# @editor_required
# def admin_unpublish():
#     entry_ids = request.form.getlist("entry_ids")
#     if not entry_ids:
#         flash("请至少选择一个条目")
#         return redirect(url_for('admin'))
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     for eid in entry_ids:
#         c.execute("UPDATE entries SET publish_date=NULL WHERE id=?", (eid,))
#     conn.commit()
#     conn.close()
#     flash("选定条目已取消发布")
#     return redirect(url_for('admin'))
#
# @app.route('/admin/make_invalid', methods=['POST'])
# @editor_required
# def admin_make_invalid():
#     entry_ids = request.form.getlist("entry_ids")
#     if not entry_ids:
#         flash("请至少选择一个条目")
#         return redirect(url_for('admin'))
#     invalid_date = datetime(1970, 1, 1)
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     for eid in entry_ids:
#         c.execute("UPDATE entries SET publish_date=? WHERE id=?", (invalid_date, eid))
#     conn.commit()
#     conn.close()
#     flash("选定条目已标记为无效")
#     return redirect(url_for('admin'))
#
# @app.route('/admin/user_admin', methods=['GET'])
# @admin_required
# def user_admin():
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("SELECT id, username FROM users")
#     users = c.fetchall()
#     conn.close()
#     return render_template('user_admin.html', users=users)
#
# @app.route('/admin/user_edit/<int:user_id>', methods=['GET', 'POST'])
# @admin_required
# def user_edit(user_id):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
#     user = c.fetchone()
#     if not user:
#         conn.close()
#         flash("User not found")
#         return redirect(url_for('user_admin'))
#
#     if request.method == 'POST':
#         new_password = request.form.get('new_password')
#         if not new_password:
#             flash("请输入新密码")
#             return redirect(url_for('user_edit', user_id=user_id))
#         c.execute("UPDATE users SET password=? WHERE id=?", (generate_password_hash(new_password), user_id))
#         conn.commit()
#         conn.close()
#         flash("密码更新成功")
#         return redirect(url_for('user_admin'))
#     conn.close()
#     return render_template('user_edit.html', user=user)
#
# @app.route('/search', methods=['GET'])
# @login_required
# def search():
#     page = request.args.get('page', default=1, type=int)
#     page_size = 5
#     offset = (page - 1) * page_size
#     query = request.args.get('q', '').strip()
#     results = []
#     total_pages = 0
#
#     if query:
#         like_query = query  # 不需要手动添加 %%，Django ORM 的 __icontains 会自动处理
#
#         # 获取总数
#         total_count = Content.objects.filter(
#             Q(title__icontains=query) | Q(description__icontains=query)
#         ).count()
#         total_pages = (total_count + page_size - 1) // page_size
#
#         # 获取分页结果
#         results = Content.objects.filter(
#             Q(title__icontains=query) | Q(description__icontains=query)
#         ).order_by('created_at')[offset:offset + page_size]
#
#     return render_template('search.html', query=query, results=results, page=page, total_pages=total_pages)

@app.route('/search', methods=['GET'])
@login_required
def search():
    """搜索内容"""
    page = request.args.get('page', default=1, type=int)
    page_size = 5
    offset = (page - 1) * page_size
    query = request.args.get('q', '').strip()
    results = []
    total_pages = 0

    if query:
        total_count = Content.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).count()
        total_pages = (total_count + page_size - 1) // page_size

        # Get paginated results
        results = Content.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('created_at')[offset:offset + page_size]

        logging.info(f"搜索查询: '{query}', 找到 {total_count} 条结果")

    return render_template('search.html', query=query, results=results, page=page, total_pages=total_pages)

#
def typst(date):
    """生成指定日期的typst数据"""
    from datetime import datetime as dt
    from django.utils import timezone
    from datetime import date as date_class

    today_str = dt.now().strftime("%Y-%m-%d")
    logging.debug(f"生成typst数据，日期: {date}, 今日: {today_str}")

    try:
        parsed_date = dt.strptime(date, '%Y-%m-%d')
        parsed_date = timezone.make_aware(parsed_date)
    except ValueError:
        parsed_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if date != today_str:
        content_query = Content.objects.filter(publish_at__date=parsed_date.date())
    else:
        content_query = Content.objects.filter(
            Q(publish_at__date=parsed_date.date()) | Q(publish_at__isnull=True)
        )
    other, college, club, lecture = [], [], [], []
    for content_item in content_query:
        title = content_item.title
        description = content_item.content
        link = content_item.link
        tag = content_item.tag
        type = content_item.type
        id = content_item.id
        if type == "DDLOnly":
            continue
        try:
            description = re.split(LINK_REGEX, description)
        except:
            continue
        splitted = []
        for e in description:
            if is_valid_url(e):
                splitted.append({"type": "link", "content": e})
            else:
                splitted.append({"type": "text", "content": e})
        description = splitted
        if allowed_file(link):
            link = None
        if (tag == "讲座" or type == "讲座"):
            lecture.append({"title": title, "description": description, "link": link, "id": id})
        elif (tag == "院级活动"):
            college.append({"title": title, "description": description, "link": link, "id": id})
        elif (tag == "社团活动"):
            club.append({"title": title, "description": description, "link": link, "id": id})
        else:
            other.append({"title": title, "description": description, "link": link, "id": id})
    data = {
        "date": date,
        "no": 1,
        "first-v": 3,
        "lecture-v": 3,
        "other-v": 3,
        "college-v": 3,
        "club-v": 3,
        "college": college,
        "club": club,
        "lecture": lecture,
        "other": other
    }

    due_content = Content.objects.filter(
        deadline__isnull=False,
        deadline__gt=parsed_date,
        publish_at__date__lte=parsed_date.date(),
        publish_at__date__gte=date_class(2023, 1, 1)
    ).order_by('deadline')

    other_due, college_due, club_due, lecture_due = [], [], [], []
    for content_item in due_content:
        title = content_item.title
        short_title = content_item.short_title
        deadline = content_item.deadline
        publish_time = content_item.publish_at
        link = content_item.link
        tag = content_item.tag
        type = content_item.type
        id = content_item.id
        if short_title:
            title = short_title
        if allowed_file(link):
            link = None

        deadline_str = deadline.strftime('%Y-%m-%d %H:%M:%S') if deadline else None
        publish_time_str = publish_time.strftime('%Y-%m-%d %H:%M:%S') if publish_time else None

        if (tag == "讲座" or type == "讲座"):
            lecture_due.append(
                {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str, "id": id})
        elif (tag == "院级活动"):
            college_due.append(
                {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str, "id": id})
        elif (tag == "社团活动"):
            club_due.append(
                {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str, "id": id})
        else:
            other_due.append(
                {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str, "id": id})
    due = {
        "college": college_due,
        "club": club_due,
        "lecture": lecture_due,
        "other": other_due
    }

    return {"data": data, "due": due}


@app.route('/typst/<date>')
# @login_required
def typst_pub(date):
    """发布typst格式的数据API"""
    logging.info(f"请求typst数据，日期: {date}")
    return json.dumps(typst(date), ensure_ascii=False, indent=2), 200, {
        'Content-Type': 'application/json; charset=utf-8'}


@app.route("/preview_edit")
def preview_edit():
    """预览编辑页面"""
    return render_template("preview_edit.html")


@app.route('/latex/<date>')
@login_required
def latex_entries(date):
    """生成LaTeX格式的内容"""
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
#
@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    """删除内容条目"""
    try:
        content = Content.objects.get(id=entry_id)
        current_user = User_info.objects.get(username=session['username'])

        if content.creator_id != current_user.id:
            flash("你没有权限删除此条目，仅可删除自己上传的条目")
            return redirect(url_for('main'))
        content.delete()
        logging.info(f"用户 {current_user.username} 删除了内容: {content.title}")
        flash("条目已删除")
        return redirect(url_for('main'))
    except Content.DoesNotExist:
        logging.warning(f"尝试删除不存在的内容ID: {entry_id}")
        flash("条目不存在")
        return redirect(url_for('main'))
    except User_info.DoesNotExist:
        logging.error(f"删除操作时用户不存在: {session.get('username')}")
        flash("用户信息错误，请重新登录")
        return redirect(url_for('login'))


#
# @app.route('/message_board', methods=['GET'])
# @login_required
# def message_board():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     c = conn.cursor()
#     c.execute("SELECT * FROM messages WHERE reply_to IS NULL ORDER BY timestamp DESC")
#     messages = [dict(row) for row in c.fetchall()]
#     for message in messages:
#         c.execute("SELECT * FROM messages WHERE reply_to = ? ORDER BY timestamp ASC", (message['id'],))
#         message['replies'] = [dict(row) for row in c.fetchall()]
#     conn.close()
#     return render_template('message_board.html', messages=messages)
#
# @app.route('/post_message', methods=['POST'])
# @login_required
# def post_message():
#     content = request.form['content']
#     reply_to = request.form.get('reply_to') or None
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("INSERT INTO messages (author, content, reply_to) VALUES (?, ?, ?)",
#               (session['username'], content, reply_to))
#     conn.commit()
#     conn.close()
#     flash("留言已发表")
#     return redirect(url_for('message_board'))
#
# @app.route('/reply/<int:message_id>', methods=['GET'])
# @login_required
# def reply_message(message_id):
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     c = conn.cursor()
#     c.execute("SELECT * FROM messages WHERE id=?", (message_id,))
#     orig = c.fetchone()
#     conn.close()
#     return render_template('reply.html', orig=orig)
#
# @app.route('/pastebin', methods=['GET', 'POST'])
# # @login_required
# def pastebin():
#     if request.method == 'POST':
#         title = request.form.get('title', '').strip()
#         content = request.form.get('content', '').strip()
#         if not content:
#             flash("Paste content cannot be empty")
#             return redirect(url_for('pastebin'))
#         try:
#             uname = session['username']
#         except:
#             uname = 'guest'
#         hash_input = title + content + uname + str(datetime.now())
#         digest = hashlib.sha256(hash_input.encode('utf-8')).digest()
#         paste_hash = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip("=")[:10]
#         conn = sqlite3.connect('database.db')
#         c = conn.cursor()
#         c.execute("INSERT INTO pastes (hash, title, content, uploader) VALUES (?, ?, ?, ?)",
#                   (paste_hash, title, content, uname))
#         conn.commit()
#         conn.close()
#         flash("Paste created successfully")
#         return redirect(url_for('pastebin_view', paste_hash=paste_hash))
#     return render_template('pastebin.html')
#
# @app.route('/pastebin/<paste_hash>')
# def pastebin_view(paste_hash):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("SELECT title, content, uploader, upload_time FROM pastes WHERE hash=?", (paste_hash,))
#     paste = c.fetchone()
#     conn.close()
#     if not paste:
#         flash("Paste not found")
#         return redirect(url_for('paste_bin'))
#     return render_template('pastebin_view.html', paste=paste)
#
#
# @app.route('/admin/files', methods=['GET', 'POST'])
# @admin_required
# def admin_files():
#     upload_folder = os.path.join(app.root_path, 'static', 'admin_uploads')
#     os.makedirs(upload_folder, exist_ok=True)
#
#     if request.method == 'POST':
#         if 'uploadFile' not in request.files:
#             flash("没有文件上传")
#             return redirect(url_for('admin_files'))
#         file = request.files['uploadFile']
#         if file.filename == '':
#             flash("未选择文件")
#             return redirect(url_for('admin_files'))
#         if file:
#             filename = file.filename
#             file_path = os.path.join(upload_folder, filename)
#             file.save(file_path)
#             flash("文件上传成功")
#             return redirect(url_for('admin_files'))
#         else:
#             flash("只允许上传 .html 和 .pdf 文件")
#             return redirect(url_for('admin_files'))
#     files = os.listdir(upload_folder)
#     return render_template('admin_files.html', files=files)
#
# @app.route('/admin/files/delete/<filename>', methods=['POST'])
# @admin_required
# def admin_file_delete(filename):
#     upload_folder = os.path.join(app.root_path, 'static', 'admin_uploads')
#     file_path = os.path.join(upload_folder, filename)
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         flash("文件已删除")
#     else:
#         flash("文件未找到")
#     return redirect(url_for('admin_files'))
#
# @app.route('/add_deadline', methods=['GET', 'POST'])
# @login_required
# def add_deadline():
#     if request.method == 'POST':
#         link = request.form.get('link', '').strip()
#         link_value = link if link else None
#         short_title = request.form.get('short_title', '').strip()
#         tag = request.form.get('tag', '').strip()
#         today = datetime.now().strftime("%Y-%m-%d")
#         publish_time = request.form.get('publish_time', today)
#         due_time = request.form.get('due_time', today)
#         news = Content.objects.create(
#             creator_id=session['username'],
#             describer_id=session['username'],
#             title=short_title,
#             link=link_value,
#             short_title=short_title,
#             content='',
#             deadline=due_time,
#             publish_at=publish_time,
#             status='pending',
#             tag=tag,
#             type="DDLOnly",
#         )
#         flash("Deadline entry added successfully")
#         return redirect(url_for('main'))
#     today = datetime.now().strftime("%Y-%m-%d")
#     return render_template('add_deadline.html', today=today)

@app.route('/add_deadline', methods=['GET', 'POST'])
@login_required
def add_deadline():
    """添加截止日期条目"""
    if request.method == 'POST':
        link = request.form.get('link', '').strip()
        link_value = link if link else None
        short_title = request.form.get('short_title', '').strip()
        tag = request.form.get('tag', '').strip()
        today = datetime.now().strftime("%Y-%m-%d")
        publish_time = request.form.get('publish_time', today)
        due_time = request.form.get('due_time', today)

        user = User_info.objects.get(username=session['username'])

        publish_datetime = datetime.strptime(publish_time, '%Y-%m-%d') if publish_time else None
        deadline_datetime = datetime.strptime(due_time, '%Y-%m-%d') if due_time else None

        news = Content.objects.create(
            creator_id=user.id,
            describer_id=user.id,
            title=short_title,
            link=link_value,
            short_title=short_title,
            content='',
            deadline=deadline_datetime,
            publish_at=publish_datetime,
            status='pending',
            tag=tag,
            type="DDLOnly",
        )
        logging.info(f"用户 {user.username} 添加了截止日期条目: {short_title}")
        flash("Deadline entry added successfully")
        return redirect(url_for('main'))
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template('add_deadline.html', today=today)



@app.route('/publish', methods=["GET", "POST"])
@editor_required
def publish():
    """发布内容管理页面"""
    if request.method == "POST":
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
    else:
        content = ""
        if os.path.exists("latest.json"):
            with open("latest.json", "r") as f:
                content = f.read()
        return render_template("publish.html", content=content)


#
# def read_mailing_list():
#     try:
#         with open('mailinglist', 'r') as f:
#             emails = [line.strip() for line in f.readlines() if line.strip()]
#             return emails
#     except FileNotFoundError:
#         return []
#
# def generate_news_html(date):
#     news_data = typst(date)
#
#     toc_html = "<h2>目录</h2><ul>"
#     toc_counter = 0
#
#     sections = {
#         'other': '校级活动',
#         'lecture': '讲座',
#         'college': '院级活动',
#         'club': '社团活动'
#     }
#
#     for section_key, section_title in sections.items():
#         has_news = section_key in news_data['data'] and news_data['data'][section_key]
#         has_due = section_key in news_data['due'] and news_data['due'][section_key]
#
#         if has_news or has_due:
#             toc_counter += 1
#             section_id = f"section-{toc_counter}"
#             toc_html += f'<li><a href="#{section_id}">{section_title}</a>'
#
#             if has_news:
#                 toc_html += '<ul>'
#                 for i, item in enumerate(news_data['data'][section_key]):
#                     item_id = f"{section_id}-item-{i+1}"
#                     toc_html += f'<li><a href="#{item_id}">{item["title"]}</a></li>'
#                 toc_html += '</ul>'
#
#             toc_html += '</li>'
#
#     toc_html += "</ul><hr>"
#
#     html_content = f"""
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <link rel="preload" href="https://nik-nul.github.io/css/news.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
#         <noscript><link rel="stylesheet" href="https://nik-nul.github.io/css/news.css"></noscript>
#         <title>南哪消息 {date}</title>
#     </head>
#     <body>
#         <h1>南哪消息 {date}</h1>
#         <div class="toc">
#             {toc_html}
#         </div>
#     """
#
#     toc_counter = 0
#     for section_key, section_title in sections.items():
#         has_news = section_key in news_data['data'] and news_data['data'][section_key]
#         has_due = section_key in news_data['due'] and news_data['due'][section_key]
#
#         if has_news or has_due:
#             toc_counter += 1
#             section_id = f"section-{toc_counter}"
#             html_content += f'<div class="section"><h2 id="{section_id}">{section_title}</h2>'
#
#             if has_due:
#                 html_content += '<table><thead><tr><th>活动标题</th><th>截止时间</th><th>刊载时间</th></tr></thead><tbody>'
#
#                 for item in news_data['due'][section_key]:
#                     link_html = f'<a href="{item["link"]}" target="_blank">{item["title"]}</a>' if item.get('link') else item['title']
#                     due_time = item['due_time'][:10] if len(item['due_time']) >= 10 else item['due_time']
#                     publish_time = item['publish_date'][:10] if item.get('publish_date') and len(item['publish_date']) >= 10 else item.get('publish_date', '')
#                     html_content += f'<tr><td>{link_html}</td><td>{due_time}</td><td>{publish_time}</td></tr>'
#
#                 html_content += '</tbody></table>'
#
#             if has_news:
#                 html_content += '<ul>'
#
#                 for i, item in enumerate(news_data['data'][section_key]):
#                     item_id = f"{section_id}-item-{i+1}"
#                     html_content += f'<li><h3 id="{item_id}">{item["title"]}</h3>'
#
#                     if item.get('link'):
#                         html_content += f'原文链接： <a href="{item["link"]}" target="_blank">{item["link"]}</a>'
#
#                     if item.get('description'):
#                         desc_html = ""
#                         for desc_part in item['description']:
#                             if desc_part['type'] == 'text':
#                                 desc_html += desc_part['content'].replace('\n', '<br>')
#                             elif desc_part['type'] == 'link':
#                                 desc_html += f' <a href="{desc_part["content"]}" target="_blank">{desc_part["content"]}</a>'
#                         html_content += f'<br>{desc_html}'
#
#                     html_content += '</li>'
#
#                 html_content += '</ul>'
#
#             html_content += '</div>'
#
#     html_content += """
#         <hr>
#         <p>南哪小报编辑部<br>{}</p>
#         <hr>
#     </body>
#     </html>
#     """.format(date)
#
#     return html_content
#
# def send_news_email(date, recipient_list=None):
#     if recipient_list is None:
#         recipient_list = read_mailing_list()
#
#     if not recipient_list:
#         return False, "邮件列表为空"
#
#     html_content = generate_news_html(date)
#
#     msg = email.message.EmailMessage()
#     msg["Subject"] = f"南哪消息 {date}"
#     msg["From"] = "南哪小报编辑部 <231220103@smail.nju.edu.cn>"
#     msg["Bcc"] = ", ".join(recipient_list)
#     msg.set_content(html_content, subtype="html")
#
#     for attempt in range(5):
#         try:
#             with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
#                 server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#                 server.send_message(msg)
#             return True, f"邮件发送成功，发送给 {len(recipient_list)} 个收件人"
#         except Exception as e:
#             if attempt == 4:
#                 return False, f"邮件发送失败: {str(e)}"
#             time.sleep(1)
#
#     return False, "邮件发送失败"
#
# @app.route('/send_email', methods=['GET', 'POST'])
# @admin_required
# def send_email():
#     if request.method == 'POST':
#         date = request.form.get('date')
#         if not date:
#             flash("请选择日期")
#             return redirect(url_for('send_email'))
#
#         success, message = send_news_email(date)
#         flash(message)
#
#         if success:
#             return redirect(url_for('send_email'))
#         else:
#             return redirect(url_for('send_email'))
#
#     today = datetime.now().strftime("%Y-%m-%d")
#     mailing_list = read_mailing_list()
#     return render_template('send_email.html', today=today, mailing_list=mailing_list)


if __name__ == '__main__':
    logging.info("App Start")
    # app.run(host="localhost", debug=True, port=45251)
    app.run(host="0.0.0.0", debug=True, port=42610)
