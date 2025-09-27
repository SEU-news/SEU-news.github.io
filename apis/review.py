import logging
import traceback
from datetime import datetime

from django.db import transaction
from flask import render_template, flash, redirect, url_for, request, session
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from common.content_status import STATUS_REVIEWED, STATUS_PUBLISHED, STATUS_REJECTED, STATUS_PENDING, STATUS_DRAFT
from django_models.models import Content, User_info


class ReviewView(MethodView):
    """
    审核内容视图类

    处理内容审核的GET和POST请求。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

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

            # 检查内容状态是否允许审核
            if entry.status not in [STATUS_DRAFT, STATUS_PENDING, STATUS_REVIEWED, STATUS_REJECTED]:
                self.logger.warning(f"尝试审核不允许的状态内容，ID: {entry_id}, 状态: {entry.status}")
                flash("该内容状态不允许审核")
                return redirect(url_for('main'))

            self.logger.debug(f"成功获取内容详情，ID: {entry_id}")
            return render_template('review.html', entry=entry)
        except Content.DoesNotExist:
            self.logger.warning(f"尝试访问不存在的内容，ID: {entry_id}")
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
            self.logger.info(f"开始处理审核请求，entry_id: {entry_id}, action: {action}")

            if not action:
                self.logger.warning("未指定操作类型")
                flash("未指定操作")
                return redirect(url_for('main'))

            with transaction.atomic():
                content = Content.objects.select_for_update().get(id=entry_id)
                current_user = User_info.objects.get(username=session['username'])

                # 检查内容状态是否允许审核
                if content.status not in [STATUS_DRAFT, STATUS_PENDING, STATUS_REVIEWED, STATUS_REJECTED]:
                    self.logger.warning(f"尝试审核不允许的状态内容，ID: {entry_id}, 状态: {content.status}")
                    flash("该内容状态不允许审核")
                    return redirect(url_for('main'))

                self.logger.info(
                    f"用户 {current_user.username}(ID:{current_user.id}) 开始审核内容(ID:{content.id})，原状态: {content.status}")

                # 检查是否尝试审核自己创建的内容
                if ((current_user.id == content.describer_id or current_user.id == content.creator_id)
                        and action == "approve"):
                    self.logger.warning(f"用户 {current_user.username} 尝试审核自己创建的内容(ID:{content.id})")
                    flash("不可审核自己所写的内容！")
                    return render_template('review.html', entry=content)

                # 获取表单数据
                title = request.form.get('title', '').strip() or content.title
                description = request.form.get('description', '').strip() or content.content
                due_time_str = request.form.get('due_time', '').strip()
                entry_type = request.form.get('entry_type', '').strip() or content.type
                tag = request.form.get('tag', '').strip()
                short_title = request.form.get('short_title', '').strip() or content.short_title

                self.logger.debug(f"获取表单数据完成，标题: {title}, 类型: {entry_type}")

                # 处理截止日期
                due_time = content.deadline
                if due_time_str:
                    try:
                        due_time = datetime.strptime(due_time_str, '%Y-%m-%d').date()
                        self.logger.debug(f"截止日期解析成功: {due_time}")
                    except ValueError:
                        self.logger.warning(f"无效的日期格式: {due_time_str}")
                        flash("日期格式错误")
                        return render_template('review.html', entry=content)

                # 检查内容是否被修改
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

                self.logger.info(f"内容是否被修改: {is_modified}")

                # 根据操作类型处理内容
                if action == 'approve':
                    if is_modified:
                        self.logger.info("内容已修改，无法直接批准")
                        flash("内容已作出修改，无法直接批准。请使用'修改并审核'按钮。")
                        return render_template('review.html', entry=content)

                    content.reviewer_id = current_user.id
                    content.status = STATUS_REVIEWED
                    content.save(update_fields=['reviewer_id', 'status', 'updated_at'])
                    self.logger.info(f"内容已批准，ID: {content.id}，审核者: {current_user.username}")
                    flash("内容已批准")

                elif action == 'modify':
                    content.reviewer_id = current_user.id
                    content.status = STATUS_REVIEWED
                    content.title = title
                    content.content = description
                    content.deadline = due_time
                    content.type = entry_type
                    content.tag = tag
                    content.short_title = short_title
                    content.save()
                    self.logger.info(f"内容已修改并审核通过，ID: {content.id}，审核者: {current_user.username}")
                    flash("内容已修改并审核通过")

                elif action == 'publish':
                    content.reviewer_id = current_user.id
                    content.status = STATUS_PUBLISHED
                    if is_modified:
                        content.title = title
                        content.content = description
                        content.deadline = due_time
                        content.type = entry_type
                        content.tag = tag
                        content.short_title = short_title
                    content.save()
                    self.logger.info(f"内容已发布，ID: {content.id}，审核者: {current_user.username}")
                    flash("内容已发布")

                elif action == 'reject':
                    content.reviewer_id = current_user.id
                    content.status = STATUS_REJECTED
                    content.save(update_fields=['reviewer_id', 'status', 'updated_at'])
                    self.logger.info(f"内容已拒绝，ID: {content.id}，审核者: {current_user.username}")
                    flash("内容已拒绝")

                else:
                    self.logger.warning(f"未知操作: {action}")
                    flash(f"未知操作: {action}")
                    return render_template('review.html', entry=content)

                # 记录审核后状态
                self.logger.info(
                    f"审核完成，内容ID: {content.id}，新状态: {content.status}，审核者: {current_user.username}")

        except Content.DoesNotExist:
            self.logger.error(f"内容不存在，ID: {entry_id}")
            flash("内容不存在")
            return redirect(url_for('main'))
        except User_info.DoesNotExist:
            self.logger.error(f"用户不存在: {session.get('username')}")
            flash("用户不存在，请重新登录")
            return redirect(url_for('login'))
        except Exception as e:
            self.logger.error(f"审核操作失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            flash(f"操作失败: {str(e)}")
            try:
                content = Content.objects.get(id=entry_id)
                return render_template('review.html', entry=content)
            except Exception:
                self.logger.error("无法加载内容详情页面")
                return redirect(url_for('main'))

        return redirect(url_for('main'))
