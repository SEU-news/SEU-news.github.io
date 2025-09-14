import hashlib
import json
import logging
import os
import subprocess
import traceback
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Django相关导入 (Django framework)
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app
from flask.views import MethodView

# 本地应用导入 (Local application imports)
from common.allowed_file import allowed_file
from common.decorator.permission_required import login_required, editor_required
from common.fetch_title import fetch_title
from common.is_valid_url import is_valid_url
from django_models.models import User_info, Content
from global_static import *


# 第三方库导入 (Third-party packages)


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
    app.add_url_rule('/paste', view_func=PasteView.as_view('paste'), methods=['POST'])
    app.add_url_rule('/upload_image', view_func=UploadImageView.as_view('upload_image'), methods=['POST'])
    app.add_url_rule('/search', view_func=SearchView.as_view('search'), methods=['GET'])
    app.add_url_rule('/typst/<date>', view_func=TypstView.as_view('typst_pub'))
    app.add_url_rule('/preview_edit', view_func=PreviewEditView.as_view('preview_edit'))
    app.add_url_rule('/latex/<date>', view_func=LatexView.as_view('latex_entries'))
    app.add_url_rule('/delete/<int:entry_id>', view_func=DeleteEntryView.as_view('delete_entry'), methods=['POST'])
    app.add_url_rule('/add_deadline', view_func=AddDeadlineView.as_view('add_deadline'), methods=['GET', 'POST'])
    app.add_url_rule('/publish', view_func=PublishView.as_view('publish'), methods=['GET', 'POST'])

    return app


class LoginView(MethodView):
    """登录类视图"""

    def get(self):
        """处理 GET 请求，展示登录页面"""
        return render_template('login.html')

    def post(self):
        """处理 POST 请求，验证登录信息"""
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('请填写用户名和密码')
            return render_template('login.html')

        try:
            user = User_info.objects.get(username=username)
            input_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

            if user.password_MD5 == input_hash:
                session.permanent = True  # 设置持久会话
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


class RegisterView(MethodView):
    """
    用户注册视图类

    处理用户注册的GET和POST请求，提供注册表单展示和用户创建功能。
    """

    def get(self):
        """
        处理GET请求，显示注册表单页面

        返回:
            render_template: 注册页面模板
        """
        return render_template('register.html')

    def post(self):
        """
        处理POST请求，执行用户注册逻辑

        从表单获取用户名和密码，进行验证后创建新用户。

        返回:
            redirect: 注册成功重定向到登录页面，失败则返回注册页面
        """
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


class MainView(MethodView):
    """
    主页面视图类

    处理主页面的GET请求，显示所有内容条目。
    """

    decorators = [login_required]  # 应用装饰器到整个视图类

    def get(self):
        """
        处理GET请求，显示主页面

        获取所有内容条目并按更新时间倒序排列，处理状态显示和权限控制。

        返回:
            render_template: 主页面模板，包含内容条目列表
        """
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


class UploadView(MethodView):
    """
    上传内容视图类
    
    处理内容上传的GET和POST请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self):
        """
        处理GET请求，显示上传内容页面
        
        返回:
            render_template: 上传页面模板
        """
        return render_template('upload.html')

    def post(self):
        """
        处理POST请求，执行内容上传逻辑
        
        从表单获取内容信息，进行处理后创建新内容条目。
        
        返回:
            redirect: 上传成功重定向到主页面
        """
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


class DescribeView(MethodView):
    """
    描述内容视图类
    
    处理内容描述的GET和POST请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self, entry_id):
        """
        处理GET请求，显示描述内容页面
        
        参数:
            entry_id (int): 内容条目ID
            
        返回:
            render_template: 描述页面模板
        """
        try:
            entry = Content.objects.get(id=entry_id)
        except Content.DoesNotExist:
            entry = None
        return render_template('describe.html', entry=entry)

    def post(self, entry_id):
        """
        处理POST请求，执行内容描述逻辑
        
        参数:
            entry_id (int): 内容条目ID
            
        返回:
            redirect: 处理完成后重定向到主页面
        """
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


class ReviewView(MethodView):
    """
    审核内容视图类
    
    处理内容审核的GET和POST请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self, entry_id):
        """
        处理GET请求，显示审核内容页面
        
        参数:
            entry_id (int): 内容条目ID
            
        返回:
            render_template: 审核页面模板
        """
        try:
            entry = Content.objects.get(id=entry_id)
            return render_template('review.html', entry=entry)
        except Content.DoesNotExist:
            flash("内容不存在")
            return redirect(url_for('main'))

    def post(self, entry_id):
        """
        处理POST请求，执行内容审核逻辑
        
        参数:
            entry_id (int): 内容条目ID
            
        返回:
            redirect: 处理完成后重定向到主页面
        """
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


class CancelView(MethodView):
    """
    取消操作视图类
    
    处理取消操作请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self, entry_id):
        """
        处理GET请求，取消操作并返回主页
        
        参数:
            entry_id (int): 内容条目ID
            
        返回:
            redirect: 重定向到主页面
        """
        return redirect(url_for('main'))


class LogoutView(MethodView):
    """
    用户登出视图类
    
    处理用户登出请求。
    """

    def get(self):
        """
        处理GET请求，执行用户登出操作
        
        返回:
            redirect: 重定向到登录页面
        """
        username = session.get('username', 'unknown')
        session.pop('username', None)
        logging.info(f"用户登出: {username}")
        return redirect(url_for('login'))


class PasteView(MethodView):
    """
    粘贴链接视图类
    
    处理粘贴链接并自动获取标题的请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def post(self):
        """
        处理POST请求，粘贴链接并自动获取标题
        
        返回:
            redirect: 重定向到主页面
        """
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
            publish_at=datetime.now(),
            status='draft',
            type='活动预告',
            tag=''  # Add required field
        )
        logging.info(f"用户 {user.username} 通过链接创建了内容: {title}")
        flash('地址添加成功')
        return redirect(url_for('main'))


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


class SearchView(MethodView):
    """
    搜索内容视图类
    
    处理内容搜索请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self):
        """
        处理GET请求，执行内容搜索逻辑
        
        返回:
            render_template: 搜索结果页面
        """
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


class TypstView(MethodView):
    """
    Typst数据视图类
    
    处理Typst格式数据的请求。
    """

    def get(self, date):
        """
        处理GET请求，发布typst格式的数据API
        
        参数:
            date (str): 日期字符串
            
        返回:
            json: Typst格式的数据
        """
        logging.info(f"请求typst数据，日期: {date}")
        return json.dumps(typst(date), ensure_ascii=False, indent=2), 200, {
            'Content-Type': 'application/json; charset=utf-8'}


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


class PreviewEditView(MethodView):
    """
    预览编辑视图类
    
    处理预览编辑页面的请求。
    """

    def get(self):
        """
        处理GET请求，显示预览编辑页面
        
        返回:
            render_template: 预览编辑页面模板
        """
        return render_template("preview_edit.html")


class LatexView(MethodView):
    """
    LaTeX内容视图类
    
    处理生成LaTeX格式内容的请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

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


#
class DeleteEntryView(MethodView):
    """
    删除内容条目视图类
    
    处理删除内容条目的请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def post(self, entry_id):
        """
        处理POST请求，删除内容条目
        
        参数:
            entry_id (int): 内容条目ID
            
        返回:
            redirect: 重定向到主页面
        """
        try:
            content = Content.objects.filter(id=entry_id).order_by('id').first()
            if not content:
                flash("项目不存在")
                return redirect(url_for('main'))

            current_user = User_info.objects.filter(username=session['username']).order_by('id').first()

            if content.creator_id != current_user.id:
                flash("你没有权限删除此项目，仅可删除自己上传的项目")
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


class AddDeadlineView(MethodView):
    """
    添加截止日期视图类
    
    处理添加截止日期条目的请求。
    """

    decorators = [login_required]  # 应用登录_required装饰器

    def get(self):
        """
        处理GET请求，显示添加截止日期页面
        
        返回:
            render_template: 添加截止日期页面模板
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return render_template('add_deadline.html', today=today)

    def post(self):
        """
        处理POST请求，执行添加截止日期逻辑
        
        返回:
            redirect: 重定向到主页面
        """
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
            with open("latest.json", "r", encoding='utf-8') as f:
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

        with open("./latest.json", "w", encoding='utf-8') as f:
            f.write(new_content)

        try:
            parsed = json.loads(new_content)
            # 写入归档文件
            with open("./archived/" + parsed["data"]["date"] + ".json", "w", encoding='utf-8') as f:
                f.write(new_content)

            try:
                subprocess.run(
                    ["./typst", "compile", "--font-path", "/home/nik_nul/font", "news_template.typ",
                     "./static/latest.pdf"],
                    # windows debug
                    # ["typst.exe", "compile", "--font-path", "./font", "news_template.typ",
                    #  "./static/latest.pdf"],
                    check=True)
                logging.info(f"成功编译typst文件，日期: {parsed['data']['date']}")
                flash("内容发布成功，PDF已生成")
            except subprocess.CalledProcessError as e:
                logging.error(f"typst编译失败: {str(e)}")
                flash("Compilation failed. Please check typst installation and source file.")
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


if __name__ == '__main__':
    logging.info("已迁移到cmd.py")
