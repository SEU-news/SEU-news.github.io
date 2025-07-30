from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from functools import wraps
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
import requests
import os
import hashlib
import base64
from urllib.parse import urlparse
import re
import json
import subprocess
import email.message
import smtplib
import time

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

EDITOR_LIST = ["editor1", "editor2"]
ADMIN_LIST = ["admin"]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

LINK_REGEX = re.compile(r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)")

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

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  uploader TEXT NOT NULL,
                  upload_time TIMESTAMP NOT NULL,
                  title TEXT NOT NULL,
                  link TEXT,
                  description TEXT,
                  describer TEXT,
                  reviewer TEXT,
                  due_time TIMESTAMP,
                  status TEXT,
                  type TEXT,
                  locked_by TEXT,
                  lock_time TIMESTAMP,
                  use_image INTEGER DEFAULT 0,
                  publish_date TIMESTAMP DEFAULT NULL,
                  tag TEXT,
                  short_title TEXT)''')
    
    try:
        c.execute("ALTER TABLE entries ADD COLUMN use_image INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute("ALTER TABLE entries ADD COLUMN publish_date TIMESTAMP DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
        
    try:
        c.execute("ALTER TABLE entries ADD COLUMN tag TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE entries ADD COLUMN short_title TEXT")
    except sqlite3.OperationalError:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  author TEXT NOT NULL,
                  content TEXT NOT NULL,
                  reply_to INTEGER,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pastes
                 (hash TEXT PRIMARY KEY,
                  title TEXT,
                  content TEXT NOT NULL,
                  uploader TEXT NOT NULL,
                  upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

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
        if 'username' not in session or session['username'] not in ADMIN_LIST:
            return abort(401)
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] not in EDITOR_LIST:
            return abort(401)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
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
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                     (username, generate_password_hash(password)))
            conn.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/')
@login_required
def main():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    cutoff = datetime.now() - timedelta(minutes=15)
    c.execute("UPDATE entries SET locked_by=NULL, lock_time=NULL WHERE lock_time IS NOT NULL AND lock_time < ?", (cutoff,))
    conn.commit()
    
    c.execute("SELECT * FROM entries WHERE publish_date IS NULL ORDER BY upload_time DESC")
    entries = c.fetchall()
    conn.close()
    return render_template('main.html', entries=entries)

@app.route('/stats')
@login_required
def stats():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    five_days_ago = datetime.now() - timedelta(days=5)
    c.execute("SELECT uploader, COUNT(*) AS count FROM entries WHERE upload_time >= ? GROUP BY uploader ORDER BY count DESC LIMIT 20", (five_days_ago,))
    uploader_stats = c.fetchall()
    c.execute("SELECT describer, COUNT(*) AS count FROM entries WHERE upload_time >= ? AND describer IS NOT NULL GROUP BY describer ORDER BY count DESC LIMIT 20", (five_days_ago,))
    describer_stats = c.fetchall()
    c.execute("SELECT reviewer, COUNT(*) AS count FROM entries WHERE upload_time >= ? AND reviewer IS NOT NULL GROUP BY reviewer ORDER BY count DESC LIMIT 20", (five_days_ago,))
    reviewer_stats = c.fetchall()
    conn.close()
    return render_template('stats.html', uploader_stats=uploader_stats, describer_stats=describer_stats, reviewer_stats=reviewer_stats)

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
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO entries 
                    (uploader, describer, upload_time, title, short_title, description, due_time, status, type, tag)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (session['username'], session['username'], datetime.now(), title, short_title, description, due_time, 'described', entry_type, tag))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))
    
    return render_template('upload.html')

@app.route('/describe/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def describe(entry_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        entry_type = request.form['entry_type']
        description = request.form['description']
        due_time = request.form['due_time']
        use_image = 1 if request.form.get('use_image') == 'on' else 0
        tag = request.form.get('tag')
        short_title = request.form.get('short_title') or title
        
        c.execute("""UPDATE entries 
                    SET title=?, short_title=?, due_time=?, description=?, describer=?, status=?, type=?, use_image=?, tag=?
                    WHERE id=?""",
                 (title, short_title, due_time, description, session['username'], 'described', entry_type, use_image, tag, entry_id))
        
        c.execute("UPDATE entries SET locked_by=NULL, lock_time=NULL WHERE id=?", (entry_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))
    else:
        c.execute("SELECT * FROM entries WHERE id=?", (entry_id,))
        entry = c.fetchone()
        
        c.execute("SELECT locked_by, lock_time FROM entries WHERE id=?", (entry_id,))
        lock_info = c.fetchone()
        if lock_info and lock_info[0] and lock_info[0] != session['username']:
            lock_time = datetime.strptime(lock_info[1], "%Y-%m-%d %H:%M:%S.%f") if lock_info[1] else None
            if lock_time and datetime.now() - lock_time < timedelta(minutes=15):
                flash("该条目正被其他人编辑")
                conn.close()
                return redirect(url_for('main'))
        
        c.execute("UPDATE entries SET locked_by=?, lock_time=? WHERE id=?", (session['username'], datetime.now(), entry_id))
        conn.commit()
        conn.close()
        return render_template('describe.html', entry=entry)

@app.route('/review/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def review(entry_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        action = request.form['action']
        
        c.execute("SELECT * FROM entries WHERE ID=?", (entry_id,))
        entry = c.fetchone()
        
        modified_entry = list(entry)
        modified_entry[3] = request.form.get('title', entry[3])
        modified_entry[5] = request.form.get('description', entry[5])
        modified_entry[8] = request.form.get('due_time', entry[8])
        modified_entry[10] = request.form.get('entry_type', entry[10])
        modified_entry[15] = request.form.get('tag', entry[15])
        
        if (session['username'] == entry[6] or session['username'] == entry[7]) and action != "modify":
            flash("不可通过自己所写的内容！")
            conn.close()
            return render_template('review.html', entry=modified_entry)
        
        title = request.form['title']
        due_time = request.form['due_time']
        description = request.form['description']
        entry_type = request.form['entry_type']
        use_image = 1 if request.form.get('use_image') == 'on' else 0
        tag = request.form.get('tag')
        short_title = request.form.get('short_title')
        unchanged = (title == entry[3] and 
                     due_time == entry[8] and 
                     description == entry[5] and 
                     entry_type == entry[10] and 
                     use_image == entry[13] and
                     tag == entry[15] and
                     short_title == entry[16])

        if action == 'approve':
            if not unchanged:
                flash("内容已作出修改，无法 approve")
                conn.close()
                return render_template('review.html', entry=modified_entry)
            
            c.execute("UPDATE entries SET reviewer=?, status=?, short_title=?, tag=? WHERE id=?", 
                     (session['username'], 'approved', short_title, tag, entry_id))
        else:
            if unchanged:
                flash("内容未作出修改，无法 modify")
                conn.close()
                return render_template('review.html', entry=modified_entry)
            
            c.execute("UPDATE entries SET title=?, short_title=?, due_time=?, description=?, reviewer=?, status=?, type=?, use_image=?, tag=? WHERE id=?",
                      (title, short_title, due_time, description, session['username'], 'modified', entry_type, use_image, tag, entry_id))
        
        c.execute("UPDATE entries SET locked_by=NULL, lock_time=NULL WHERE id=?", (entry_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))
    else:
        c.execute("SELECT * FROM entries WHERE id=?", (entry_id,))
        entry = c.fetchone()
        
        c.execute("SELECT locked_by, lock_time FROM entries WHERE id=?", (entry_id,))
        lock_info = c.fetchone()
        if lock_info and lock_info[0] and lock_info[0] != session['username']:
            lock_time = datetime.strptime(lock_info[1], "%Y-%m-%d %H:%M:%S.%f") if lock_info[1] else None
            if lock_time and datetime.now() - lock_time < timedelta(minutes=15):
                flash("该条目正被其他人编辑")
                conn.close()
                return redirect(url_for('main'))
        
        c.execute("UPDATE entries SET locked_by=?, lock_time=? WHERE id=?", (session['username'], datetime.now(), entry_id))
        conn.commit()
        conn.close()
        return render_template('review.html', entry=entry)

@app.route('/cancel/<int:entry_id>')
@login_required
def cancel(entry_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT locked_by FROM entries WHERE id=?", (entry_id,))
    entry_lock_info = c.fetchone()
    if entry_lock_info and entry_lock_info[0] == session['username']:
        c.execute("UPDATE entries SET locked_by=NULL, lock_time=NULL WHERE id=?", (entry_id,))
        conn.commit()
    conn.close()
    return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        original_password = request.form.get('original_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash("New passwords do not match")
            return redirect(url_for('change_password'))
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (session['username'],))
        user = c.fetchone()
        if user and check_password_hash(user[2], original_password):
            c.execute("UPDATE users SET password=? WHERE username=?", (generate_password_hash(new_password), session['username']))
            conn.commit()
            flash("Password successfully updated. Please log in again.")
            session.pop('username', None)
            conn.close()
            return redirect(url_for('login'))
        else:
            flash("Original password is incorrect")
            conn.close()
        return redirect(url_for('change_password'))
    return render_template('change_password.html')

@app.route('/paste', methods=['POST'])
@login_required
def paste():
    link = request.form['link'].strip()
    if not link or not is_valid_url(link):
        flash('请输入有效的地址')
        return redirect(url_for('main'))
    parsed = urlparse(link)
    canonical_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id FROM entries WHERE link=?", (canonical_url,))
    if c.fetchone():
        conn.close()
        flash("该链接已经上传")
        return redirect(url_for('main'))
    title = fetch_title(link)
    print(title)
    c.execute("""INSERT INTO entries 
                (uploader, upload_time, title, link, due_time, status, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (session['username'], datetime.now(), title, canonical_url, None, 'pending', '活动预告'))
    conn.commit()
    conn.close()
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
        flash("图片上传成功，并已添加到条目, 图片链接：<a href='" + dynamic_img_url + "' target='_blank'>" + dynamic_img_url + "</a>")
        return redirect(url_for('main'))
    else:
        flash("不支持的文件格式")
        return redirect(url_for('main'))

@app.route('/admin')
@editor_required
def admin():
    page = request.args.get('page', default=1, type=int)
    page_size = 12
    offset = (page - 1) * page_size
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM entries")
    total_count = c.fetchone()[0]
    total_pages = (total_count + page_size - 1) // page_size
    c.execute("SELECT * FROM entries ORDER BY upload_time DESC LIMIT ? OFFSET ?", (page_size, offset))
    entries = c.fetchall()
    conn.close()
    default_publish_date = datetime.now().strftime("%Y-%m-%d")
    return render_template('admin.html', entries=entries, page=page, total_pages=total_pages, default_publish_date=default_publish_date)

@app.route('/admin/edit/<int:entry_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit(entry_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        uploader = request.form['uploader']
        upload_time = request.form['upload_time']
        title = request.form['title']
        link = request.form['link']
        description = request.form['description']
        describer = request.form['describer']
        reviewer = request.form['reviewer']
        due_time = request.form['due_time']
        status = request.form['status']
        entry_type = request.form['entry_type']
        c.execute("""UPDATE entries SET uploader=?, upload_time=?, title=?, link=?, description=?, describer=?, reviewer=?, due_time=?, status=?, type=? WHERE id=?""",
                  (uploader, upload_time, title, link, description, describer, reviewer, due_time, status, entry_type, entry_id))
        conn.commit()
        conn.close()
        flash("条目已更新")
        return redirect(url_for('admin'))
    else:
        c.execute("SELECT * FROM entries WHERE id=?", (entry_id,))
        entry = c.fetchone()
        conn.close()
        return render_template('admin_edit.html', entry=entry)

@app.route('/admin/delete/<int:entry_id>', methods=['POST'])
@admin_required
def admin_delete(entry_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    flash("条目已删除")
    return redirect(url_for('admin'))

@app.route('/admin/publish', methods=['POST'])
@editor_required
def admin_publish():
    entry_ids = request.form.getlist("entry_ids")
    publish_time_input = request.form.get("publish_time")
    if not entry_ids:
        flash("请至少选择一个条目")
        return redirect(url_for('admin'))
    try:
        publish_time = datetime.strptime(publish_time_input, "%Y-%m-%d")
    except (ValueError, TypeError):
        publish_time = datetime.now()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for eid in entry_ids:
        c.execute("UPDATE entries SET publish_date=? WHERE id=?", (publish_time, eid))
    conn.commit()
    conn.close()
    flash("选定条目的发布时间已更新")
    return redirect(url_for('admin'))

@app.route('/admin/publish_today', methods=['POST'])
@editor_required
def admin_publish_today():
    publish_time = datetime.now().date()
    today = datetime.now().date()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE entries SET publish_date=? WHERE date(upload_time)=?", (publish_time, today))
    conn.commit()
    conn.close()
    flash("今天上传的条目的发布时间已更新")
    return redirect(url_for('admin'))

@app.route('/admin/unpublish', methods=['POST'])
@editor_required
def admin_unpublish():
    entry_ids = request.form.getlist("entry_ids")
    if not entry_ids:
        flash("请至少选择一个条目")
        return redirect(url_for('admin'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for eid in entry_ids:
        c.execute("UPDATE entries SET publish_date=NULL WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    flash("选定条目已取消发布")
    return redirect(url_for('admin'))

@app.route('/admin/make_invalid', methods=['POST'])
@editor_required
def admin_make_invalid():
    entry_ids = request.form.getlist("entry_ids")
    if not entry_ids:
        flash("请至少选择一个条目")
        return redirect(url_for('admin'))
    invalid_date = datetime(1970, 1, 1)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for eid in entry_ids:
        c.execute("UPDATE entries SET publish_date=? WHERE id=?", (invalid_date, eid))
    conn.commit()
    conn.close()
    flash("选定条目已标记为无效")
    return redirect(url_for('admin'))

@app.route('/admin/user_admin', methods=['GET'])
@admin_required
def user_admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, username FROM users")
    users = c.fetchall()
    conn.close()
    return render_template('user_admin.html', users=users)

@app.route('/admin/user_edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        flash("User not found")
        return redirect(url_for('user_admin'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if not new_password:
            flash("请输入新密码")
            return redirect(url_for('user_edit', user_id=user_id))
        c.execute("UPDATE users SET password=? WHERE id=?", (generate_password_hash(new_password), user_id))
        conn.commit()
        conn.close()
        flash("密码更新成功")
        return redirect(url_for('user_admin'))
    conn.close()
    return render_template('user_edit.html', user=user)

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
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        like_query = f'%{query}%'
        c.execute("SELECT COUNT(*) FROM entries WHERE title LIKE ? OR description LIKE ?", (like_query, like_query))
        total_count = c.fetchone()[0]
        total_pages = (total_count + page_size - 1) // page_size

        c.execute("""SELECT * FROM entries 
                     WHERE title LIKE ? OR description LIKE ?
                     ORDER BY upload_time DESC 
                     LIMIT ? OFFSET ?""",
                  (like_query, like_query, page_size, offset))
        results = c.fetchall()
        conn.close()

    return render_template('search.html', query=query, results=results, page=page, total_pages=total_pages)

def typst(date):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(date, today_str)
    if date != today_str:
        c.execute("SELECT title, description, link, tag, type, id FROM entries WHERE DATE(publish_date)=? ORDER BY upload_time ASC", (date,))
    else:
        c.execute("SELECT title, description, link, tag, type, id FROM entries WHERE DATE(publish_date)=? OR publish_date IS NULL ORDER BY upload_time ASC", (date,))
    entries = c.fetchall()
    conn.close()
    other, college, club, lecture  = [], [], [], []
    for title, description, link, tag, sector, num in entries:
        if sector == "DDLOnly":
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
        if(tag == "讲座" or sector == "讲座"):
            lecture.append({"title": title, "description": description, "link": link, "id": num})
        elif(tag == "院级活动"):
            college.append({"title": title, "description": description, "link": link, "id": num})
        elif(tag == "社团活动"):
            club.append({"title": title, "description": description, "link": link, "id": num})
        else:
            other.append({"title": title, "description": description, "link": link, "id": num})
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
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT title, link, tag, due_time, publish_date, short_title, type, id FROM entries WHERE due_time IS NOT NULL AND due_time > ? AND DATE(publish_date) <= ? AND publish_date >= '2023-01-01' ORDER BY due_time ASC", (date, date))
    due_entries = c.fetchall()
    conn.close()
    other_due, college_due, club_due, lecture_due  = [], [], [], []
    for title, link, tag, due_time, publish_date, short_title, sector, num in due_entries:
        if short_title:
            title = short_title
        if allowed_file(link):
            link = None
        if(tag == "讲座" or sector == "讲座"):
            lecture_due.append({"title": title, "link": link, "due_time": due_time, "publish_date": publish_date, "id": num})
        elif(tag == "院级活动"):
            college_due.append({"title": title, "link": link, "due_time": due_time, "publish_date": publish_date, "id": num})
        elif(tag == "社团活动"):
            club_due.append({"title": title, "link": link, "due_time": due_time, "publish_date": publish_date, "id": num})
        else:
            other_due.append({"title": title, "link": link, "due_time": due_time, "publish_date": publish_date, "id": num})
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
    return json.dumps(typst(date), ensure_ascii=False, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/preview_edit")
def preview_edit():
    return render_template("preview_edit.html")

@app.route('/latex/<date>')
@login_required
def latex_entries(date):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT title, description, link, tag, describer FROM entries WHERE DATE(publish_date)=? ORDER BY tag ASC", (date,))
    entries = c.fetchall()
    conn.close()
    
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
    for title, description, link, tag, describer in entries:
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

@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT uploader FROM entries WHERE id=?", (entry_id,))
    entry = c.fetchone()
    if not entry:
        conn.close()
        flash("条目不存在")
        return redirect(url_for('main'))
    if entry[0] != session['username']:
        conn.close()
        flash("你没有权限删除此条目，仅可删除自己上传的条目")
        return redirect(url_for('main'))
    c.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    flash("条目已删除")
    return redirect(url_for('main'))

@app.route('/message_board', methods=['GET'])
@login_required
def message_board():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE reply_to IS NULL ORDER BY timestamp DESC")
    messages = [dict(row) for row in c.fetchall()]
    for message in messages:
        c.execute("SELECT * FROM messages WHERE reply_to = ? ORDER BY timestamp ASC", (message['id'],))
        message['replies'] = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('message_board.html', messages=messages)

@app.route('/post_message', methods=['POST'])
@login_required
def post_message():
    content = request.form['content']
    reply_to = request.form.get('reply_to') or None
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (author, content, reply_to) VALUES (?, ?, ?)",
              (session['username'], content, reply_to))
    conn.commit()
    conn.close()
    flash("留言已发表")
    return redirect(url_for('message_board'))

@app.route('/reply/<int:message_id>', methods=['GET'])
@login_required
def reply_message(message_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE id=?", (message_id,))
    orig = c.fetchone()
    conn.close()
    return render_template('reply.html', orig=orig)

@app.route('/pastebin', methods=['GET', 'POST'])
# @login_required
def pastebin():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not content:
            flash("Paste content cannot be empty")
            return redirect(url_for('pastebin'))
        try:
            uname = session['username']
        except:
            uname = 'guest'
        hash_input = title + content + uname + str(datetime.now())
        digest = hashlib.sha256(hash_input.encode('utf-8')).digest()
        paste_hash = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip("=")[:10]
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO pastes (hash, title, content, uploader) VALUES (?, ?, ?, ?)",
                  (paste_hash, title, content, uname))
        conn.commit()
        conn.close()
        flash("Paste created successfully")
        return redirect(url_for('pastebin_view', paste_hash=paste_hash))
    return render_template('pastebin.html')

@app.route('/pastebin/<paste_hash>')
def pastebin_view(paste_hash):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT title, content, uploader, upload_time FROM pastes WHERE hash=?", (paste_hash,))
    paste = c.fetchone()
    conn.close()
    if not paste:
        flash("Paste not found")
        return redirect(url_for('paste_bin'))
    return render_template('pastebin_view.html', paste=paste)


@app.route('/admin/files', methods=['GET', 'POST'])
@admin_required
def admin_files():
    upload_folder = os.path.join(app.root_path, 'static', 'admin_uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    if request.method == 'POST':
        if 'uploadFile' not in request.files:
            flash("没有文件上传")
            return redirect(url_for('admin_files'))
        file = request.files['uploadFile']
        if file.filename == '':
            flash("未选择文件")
            return redirect(url_for('admin_files'))
        if file:
            filename = file.filename
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            flash("文件上传成功")
            return redirect(url_for('admin_files'))
        else:
            flash("只允许上传 .html 和 .pdf 文件")
            return redirect(url_for('admin_files'))
    files = os.listdir(upload_folder)
    return render_template('admin_files.html', files=files)

@app.route('/admin/files/delete/<filename>', methods=['POST'])
@admin_required
def admin_file_delete(filename):
    upload_folder = os.path.join(app.root_path, 'static', 'admin_uploads')
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash("文件已删除")
    else:
        flash("文件未找到")
    return redirect(url_for('admin_files'))

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
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""INSERT INTO entries 
                     (uploader, describer, upload_time, title, link, short_title, description, due_time, publish_date, status, tag, type)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (session['username'], session['username'], datetime.now(), short_title, link_value, short_title, '', due_time, publish_time, 'Approved', tag, "DDLOnly"))
        conn.commit()
        conn.close()
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
            subprocess.run(["./typst", "compile", "--font-path", "/home/nik_nul/font", "news_template.typ", "./static/latest.pdf"], check=True)
        except subprocess.CalledProcessError:
           flash("Compilation failed. Please check typst installation and source file.")
        return render_template("publish.html", content=new_content)
    else:
        content = ""
        if os.path.exists("latest.json"):
            with open("latest.json", "r") as f:
                content = f.read()
        return render_template("publish.html", content=content)

def read_mailing_list():
    try:
        with open('mailinglist', 'r') as f:
            emails = [line.strip() for line in f.readlines() if line.strip()]
            return emails
    except FileNotFoundError:
        return []

def generate_news_html(date):
    news_data = typst(date)
    
    toc_html = "<h2>目录</h2><ul>"
    toc_counter = 0
    
    sections = {
        'other': '校级活动',
        'lecture': '讲座',
        'college': '院级活动', 
        'club': '社团活动'
    }
    
    for section_key, section_title in sections.items():
        has_news = section_key in news_data['data'] and news_data['data'][section_key]
        has_due = section_key in news_data['due'] and news_data['due'][section_key]
        
        if has_news or has_due:
            toc_counter += 1
            section_id = f"section-{toc_counter}"
            toc_html += f'<li><a href="#{section_id}">{section_title}</a>'
            
            if has_news:
                toc_html += '<ul>'
                for i, item in enumerate(news_data['data'][section_key]):
                    item_id = f"{section_id}-item-{i+1}"
                    toc_html += f'<li><a href="#{item_id}">{item["title"]}</a></li>'
                toc_html += '</ul>'
            
            toc_html += '</li>'
    
    toc_html += "</ul><hr>"
    
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <link rel="preload" href="https://nik-nul.github.io/css/news.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
        <noscript><link rel="stylesheet" href="https://nik-nul.github.io/css/news.css"></noscript>
        <title>南哪消息 {date}</title>
    </head>
    <body>
        <h1>南哪消息 {date}</h1>
        <div class="toc">
            {toc_html}
        </div>
    """
    
    toc_counter = 0
    for section_key, section_title in sections.items():
        has_news = section_key in news_data['data'] and news_data['data'][section_key]
        has_due = section_key in news_data['due'] and news_data['due'][section_key]
        
        if has_news or has_due:
            toc_counter += 1
            section_id = f"section-{toc_counter}"
            html_content += f'<div class="section"><h2 id="{section_id}">{section_title}</h2>'
            
            if has_due:
                html_content += '<table><thead><tr><th>活动标题</th><th>截止时间</th><th>刊载时间</th></tr></thead><tbody>'
                
                for item in news_data['due'][section_key]:
                    link_html = f'<a href="{item["link"]}" target="_blank">{item["title"]}</a>' if item.get('link') else item['title']
                    due_time = item['due_time'][:10] if len(item['due_time']) >= 10 else item['due_time']
                    publish_time = item['publish_date'][:10] if item.get('publish_date') and len(item['publish_date']) >= 10 else item.get('publish_date', '')
                    html_content += f'<tr><td>{link_html}</td><td>{due_time}</td><td>{publish_time}</td></tr>'
                
                html_content += '</tbody></table>'
            
            if has_news:
                html_content += '<ul>'
                
                for i, item in enumerate(news_data['data'][section_key]):
                    item_id = f"{section_id}-item-{i+1}"
                    html_content += f'<li><h3 id="{item_id}">{item["title"]}</h3>'
                    
                    if item.get('link'):
                        html_content += f'原文链接： <a href="{item["link"]}" target="_blank">{item["link"]}</a>'
                    
                    if item.get('description'):
                        desc_html = ""
                        for desc_part in item['description']:
                            if desc_part['type'] == 'text':
                                desc_html += desc_part['content'].replace('\n', '<br>')
                            elif desc_part['type'] == 'link':
                                desc_html += f' <a href="{desc_part["content"]}" target="_blank">{desc_part["content"]}</a>'
                        html_content += f'<br>{desc_html}'
                    
                    html_content += '</li>'
                
                html_content += '</ul>'
            
            html_content += '</div>'
    
    html_content += """
        <hr>
        <p>南哪小报编辑部<br>{}</p>
        <hr>
    </body>
    </html>
    """.format(date)
    
    return html_content

def send_news_email(date, recipient_list=None):
    if recipient_list is None:
        recipient_list = read_mailing_list()
    
    if not recipient_list:
        return False, "邮件列表为空"
    
    html_content = generate_news_html(date)
    
    msg = email.message.EmailMessage()
    msg["Subject"] = f"南哪消息 {date}"
    msg["From"] = "南哪小报编辑部 <231220103@smail.nju.edu.cn>"
    msg["Bcc"] = ", ".join(recipient_list)
    msg.set_content(html_content, subtype="html")
    
    for attempt in range(5):
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            return True, f"邮件发送成功，发送给 {len(recipient_list)} 个收件人"
        except Exception as e:
            if attempt == 4:
                return False, f"邮件发送失败: {str(e)}"
            time.sleep(1)
    
    return False, "邮件发送失败"

@app.route('/send_email', methods=['GET', 'POST'])
@admin_required
def send_email():
    if request.method == 'POST':
        date = request.form.get('date')
        if not date:
            flash("请选择日期")
            return redirect(url_for('send_email'))
        
        success, message = send_news_email(date)
        flash(message)
        
        if success:
            return redirect(url_for('send_email'))
        else:
            return redirect(url_for('send_email'))
    
    today = datetime.now().strftime("%Y-%m-%d")
    mailing_list = read_mailing_list()
    return render_template('send_email.html', today=today, mailing_list=mailing_list)

if __name__ == '__main__':
    # app.run(host="localhost", debug=True, port=45251)
    app.run(host="0.0.0.0", debug=False, port=80)
