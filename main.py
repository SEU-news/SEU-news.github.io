import copy
import hashlib
import json
import logging
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse

import django
import requests
from bs4 import BeautifulSoup
from django.db import IntegrityError
from django.db.models import Q
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort

from django_config import configure_django

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(name)s - %(message)s')

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


def fetch_title(url):
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
            pass
    return "标题获取失败"


EDITOR_LIST = ["editor1", "editor2", "111"]
ADMIN_LIST = ["admin", "222", "111"]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

LINK_REGEX = re.compile(
    r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)")


def allowed_file(filename):
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def hash_file(file_obj):
    file_obj.seek(0)
    file_content = file_obj.read()
    file_hash = hashlib.md5(file_content).hexdigest()
    file_obj.seek(0)
    return file_hash


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        username = session.get('username')

        if not username:
            abort(401)

        user = User_info.objects.filter(username=username).first()

        # 如果用户不存在或没有权限，都返回403
        if not user or not user.has_admin_permission():
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


def editor_required(f):
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('请填写用户名和密码')
            return render_template('login.html')

        try:
            user = User_info.objects.get(username=username)
        except User_info.DoesNotExist:
            flash('user doesnot exist')

        if user:
            # 计算输入密码的MD5
            input_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
            # 比较哈希值
            if user.password_MD5 == input_hash:
                session.permanent = True
                session['username'] = username
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
# @admin_required
def register():
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

            flash('注册成功！请登录')
            return redirect(url_for('login'))

        except IntegrityError:
            # 作为备用错误处理
            flash('注册失败，请重试')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/')
@login_required
def main():
    contents = Content.objects.filter(
        publish_at__isnull=True
    ).order_by('updated_at')

    return render_template('main.html', entries=contents)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_time = request.form['due_time']
        entry_type = request.form['entry_type']
        tag = request.form.get('tag')
        short_title = request.form.get('short_title') or title

        content = Content.objects.create(
            uploader=session['username'],
            describer=session['username'],
            title=title,
            short_title=short_title,
            content=description,
            status='pending',
            type=entry_type,
            tag=tag,
            deadline=due_time
        )
        return redirect(url_for('main'))

    return render_template('upload.html')


@app.route('/describe/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def describe(entry_id):
    if request.method == 'POST':
        title = request.form['title']
        entry_type = request.form['entry_type']
        description = request.form['description']
        due_time = request.form['due_time']
        use_image = 1 if request.form.get('use_image') == 'on' else 0
        tag = request.form.get('tag')
        short_title = request.form.get('short_title') or title
        content = Content.objects.create(
            uploader=session['username'],
            describer=session['username'],
            title=title,
            short_title=short_title,
            content=description,
            status='pending',
            type=entry_type,
            tag=tag,
            deadline=due_time
        )
        return redirect(url_for('main'))
    else:
        try:
            entry = Content.objects.get(id=entry_id)
        except Content.DoesNotExist:
            entry = None

        return render_template('describe.html', entry=entry)


#
@app.route('/review/<int:entry_id>', methods=['POST'])
@login_required
def review(entry_id):
    action = request.form['action']

    content = Content.object.get(id=entry_id)
    m_content = copy.copy(content)
    m_content.title = request.form.get('title', content.title)
    m_content.content = request.form.get('description', content.content)
    m_content.deadline = request.form.get('due_time', content.deadline)
    m_content.type = request.form.get('entry_type', content.type)
    m_content.tag = request.form.get('tag', content.tag)

    if (session['username'] == content.describer_id or session['username'] == content.creator_id) and action != "modify":
        flash("不可通过自己所写的内容！")
        return render_template('review.html', entry=content)
    title = request.form['title']
    due_time = request.form['due_time']
    description = request.form['description']
    entry_type = request.form['entry_type']
    use_image = 1 if request.form.get('use_image') == 'on' else 0
    tag = request.form.get('tag')
    short_title = request.form.get('short_title')
    is_modified = any([
        content.title != title,
        content.content != description,
        content.deadline != due_time,
        content.type != entry_type,
        content.tag != tag,
        content.short_title != short_title
    ])

    if action == 'approve':
        if is_modified:
            flash("内容已作出修改，无法 approve")
            return render_template('review.html', entry=m_content)
        content.reviewer_id = session['username']
        content.status = 'reviewed'
        content.save()
    else:
        if not is_modified:
            flash("内容未作出修改，无法 modify")
            return render_template('review.html', entry=m_content)

        content.reviewer_id = session['username']
        content.status = 'reviewed'
        content.title = title
        content.content = description
        content.deadline = due_time
        content.type = entry_type
        content.tag = tag
        content.short_title = short_title
        content.save()
    return redirect(url_for('main'))


# @app.route('/cancel/<int:entry_id>')
# @login_required
# def cancel(entry_id):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("SELECT locked_by FROM entries WHERE id=?", (entry_id,))
#     entry_lock_info = c.fetchone()
#     if entry_lock_info and entry_lock_info[0] == session['username']:
#         c.execute("UPDATE entries SET locked_by=NULL, lock_time=NULL WHERE id=?", (entry_id,))
#         conn.commit()
#     conn.close()
#     return redirect(url_for('main'))
#
@app.route('/logout')
def logout():
    session.pop('username', None)
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
    print(title)
    entry = Content.objects.create(
        uploader=session['username'],
        title=title,
        link=canonical_url,
        due_time=None,
        status='draft',
        type='活动预告'
    )
    flash('地址添加成功')
    return redirect(url_for('main'))


@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        flash("没有文件上传")
        return redirect(url_for('main'))
    file = request.files['image']
    if file.filename == '':
        flash("未选择文件")
        return redirect(url_for('main'))
    if file and allowed_file(file.filename):
        extension = file.filename.rsplit('.', 1)[1].lower()
        file_hash = hash_file(file)
        filename = f"{file_hash}.{extension}"
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id FROM entries WHERE link=?", (filename,))
        if c.fetchone():
            conn.close()
            flash("该图片已经上传")
            return redirect(url_for('main'))
        conn.close()
        upload_folder = os.path.join(app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        dynamic_img_url = url_for('static', filename='uploads/' + filename, _external=True)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO entries
                         (uploader, upload_time, title, link, due_time, status, type)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (session['username'], datetime.now(), file.filename, filename, None, 'pending', '活动预告'))
        conn.commit()
        conn.close()
        flash(
            "图片上传成功，并已添加到条目, 图片链接：<a href='" + dynamic_img_url + "' target='_blank'>" + dynamic_img_url + "</a>")
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
@app.route('/search', methods=['GET'])
@login_required
def search():
    page = request.args.get('page', default=1, type=int)
    page_size = 5
    offset = (page - 1) * page_size
    query = request.args.get('q', '').strip()
    results = []
    total_pages = 0

    if query:
        like_query = query  # 不需要手动添加 %%，Django ORM 的 __icontains 会自动处理

        # 获取总数
        total_count = Content.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).count()
        total_pages = (total_count + page_size - 1) // page_size

        # 获取分页结果
        results = Content.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('created_at')[offset:offset + page_size]

    return render_template('search.html', query=query, results=results, page=page, total_pages=total_pages)


#
def typst(date):
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(date, today_str)
    if date != today_str:
        content_query = Content.objects.filter(publish_at__date=date)
    else:
        content_query = Content.objects.filter(
            Q(publish_at__date=date) | Q(publish_at__isnull=True)
        )
    other, college, club, lecture = [], [], [], []
    for content_item in content_query:
        title = content_item.title
        description = content_item.description
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
        deadline__isnull=False,  # due_time IS NOT NULL
        deadline__gt=date,  # due_time > date
        publish_time__date__lte=date,  # DATE(publish_date) <= date
        publish_time__date__gte=date(2023, 1, 1)  # publish_date >= '2023-01-01'
    ).order_by('due_time')
    other_due, college_due, club_due, lecture_due = [], [], [], []
    for content_item in due_content:
        title = content_item.title
        short_title = content_item.short_title
        deadline = content_item.deadline
        publish_time = content_item.publish_time
        link = content_item.link
        tag = content_item.tag
        type = content_item.type
        id = content_item.id
        if short_title:
            title = short_title
        if allowed_file(link):
            link = None
        if (tag == "讲座" or type == "讲座"):
            lecture_due.append(
                {"title": title, "link": link, "due_time": deadline, "publish_date": publish_time, "id": id})
        elif (tag == "院级活动"):
            college_due.append(
                {"title": title, "link": link, "due_time": deadline, "publish_date": publish_time, "id": id})
        elif (tag == "社团活动"):
            club_due.append(
                {"title": title, "link": link, "due_time": deadline, "publish_date": publish_time, "id": id})
        else:
            other_due.append(
                {"title": title, "link": link, "due_time": deadline, "publish_date": publish_time, "id": id})
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
    return json.dumps(typst(date), ensure_ascii=False, indent=2), 200, {
        'Content-Type': 'application/json; charset=utf-8'}


@app.route("/preview_edit")
def preview_edit():
    return render_template("preview_edit.html")


@app.route('/latex/<date>')
@login_required
def latex_entries(date):
    content = Content.objects.filter(publish_at__date=date)

    def escape_latex(text):
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
    for cotent_item in content:
        title = cotent_item.title
        tag = cotent_item.tag
        link = cotent_item.link
        describer = cotent_item.describer_id
        title = escape_latex(title)
        title = title.rstrip('\r\n')
        description = escape_latex(description).replace('\n', r'\\')
        if tag in ["讲座", "院级活动", "社团活动"]:
            latex_output += r"\subsection{" + title + "} % " + tag + " describer: " + describer + "\n"
        else:
            latex_output += r"\section{" + title + "} % " + tag + " describer: " + describer + "\n"
        latex_output += description + "\n"
        if link and len(link) > 10:
            latex_output += "\\\\详见：" + r"\url{" + link + "}" + "\n\n"
    return latex_output, 200, {'Content-Type': 'text/plain; charset=utf-8'}


#
@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    try:
        content = Content.objects.get(id=entry_id)
        if content.uploader != session['username']:
            flash("你没有权限删除此条目，仅可删除自己上传的条目")
            return redirect(url_for('main'))
        content.delete()
        flash("条目已删除")
        return redirect(url_for('main'))
    except Content.DoesNotExist:
        flash("条目不存在")
        return redirect(url_for('main'))


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
@app.route('/add_deadline', methods=['GET', 'POST'])
@login_required
def add_deadline():
    if request.method == 'POST':
        link = request.form.get('link', '').strip()
        link_value = link if link else None
        short_title = request.form.get('short_title', '').strip()
        tag = request.form.get('tag', '').strip()
        today = datetime.now().strftime("%Y-%m-%d")
        publish_time = request.form.get('publish_time', today)
        due_time = request.form.get('due_time', today)
        news = Content.objects.create(
            creator_id=session['username'],
            describer_id=session['username'],
            title=short_title,
            link=link_value,
            short_title=short_title,
            content='',
            deadline=due_time,
            publish_at=publish_time,
            status='pending',
            tag=tag,
            type="DDLOnly",
        )
        flash("Deadline entry added successfully")
        return redirect(url_for('main'))
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template('add_deadline.html', today=today)


@app.route('/publish', methods=["GET", "POST"])
@editor_required
def publish():
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
        except subprocess.CalledProcessError:
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
    # app.run(host="localhost", debug=True, port=45251)
    app.run(host="0.0.0.0", debug=False, port=42610)
