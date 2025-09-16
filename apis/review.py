import logging
import traceback

from django.db import transaction
from flask import render_template, flash, redirect, url_for, request, session
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content, User_info


class ReviewView(MethodView):
    """
    审核内容视图类

    处理内容审核的GET和POST请求。
    """

    decorators = [PermissionDecorators.login_required, PermissionDecorators.editor_required]  # 应用登录_required装饰器

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
