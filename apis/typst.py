import json
import logging
import re
from datetime import time, datetime, date

from django.db.models import Q
from django.utils import timezone
from flask.views import MethodView

from common.global_static import LINK_REGEX
from common.methods.is_valid_url import is_valid_url
from django_models.models import Content


class TypstView(MethodView):
    """
    Typst数据视图类

    处理Typst格式数据的请求。
    """

    def __init__(self):
        """
        初始化日志记录器
        """
        self.logger = logging.getLogger(__name__)

    def get(self, date):
        """
        处理GET请求，发布typst格式的数据API

        参数:
            date (str): 日期字符串

        返回:
            json: Typst格式的数据
        """
        self.logger.info(f"请求typst数据，日期: {date}")
        typst_data = self._generate_typst_data(date)
        return json.dumps(typst_data, ensure_ascii=False, indent=2), 200, {
            'Content-Type': 'application/json; charset=utf-8'}

    def _generate_typst_data(self, date_str):
        """生成指定日期的typst数据"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.logger.info(f"生成typst数据，日期: {date_str}, 今日: {today_str}")

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # 创建当天的开始和结束时间（使用时区感知的datetime）
            start_of_day = timezone.make_aware(datetime.combine(target_date, time.min))
            end_of_day = timezone.make_aware(datetime.combine(target_date, time.max))
            self.logger.info(f"查询时间范围: {start_of_day} 到 {end_of_day}")

        except ValueError as e:
            self.logger.error(f"日期解析失败: {e}")
            # 使用当前时间作为默认值
            now = timezone.now()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if date_str != today_str:
            content_query = Content.objects.filter(
                publish_at__gte=start_of_day,
                publish_at__lte=end_of_day
            )
        else:
            content_query = Content.objects.filter(
                Q(publish_at__gte=start_of_day, publish_at__lte=end_of_day) |
                Q(publish_at__isnull=True)
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

            if (tag == "讲座" or type == "讲座"):
                lecture.append({"title": title, "description": description, "link": link, "id": id})
            elif (tag == "院级活动"):
                college.append({"title": title, "description": description, "link": link, "id": id})
            elif (tag == "社团活动"):
                club.append({"title": title, "description": description, "link": link, "id": id})
            else:
                other.append({"title": title, "description": description, "link": link, "id": id})

        data = {
            "date": date_str,
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

        # 修复deadline条目获取问题
        try:
            target_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            # 修复查询逻辑，确保正确获取deadline条目
            due_content = Content.objects.filter(
                deadline__isnull=False,
                deadline__date__gte=target_date_obj,  # deadline日期大于等于目标日期
                publish_at__date__lte=target_date_obj,  # 发布日期小于等于目标日期
                publish_at__date__gte=date(2023, 1, 1)  # 发布日期大于等于2023年1月1日
            ).order_by('deadline')

        except ValueError:
            due_content = Content.objects.none()

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

            deadline_str = deadline.strftime('%Y-%m-%d %H:%M:%S') if deadline else None
            publish_time_str = publish_time.strftime('%Y-%m-%d %H:%M:%S') if publish_time else None

            if (tag == "讲座" or type == "讲座"):
                lecture_due.append(
                    {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str,
                     "id": id})
            elif (tag == "院级活动"):
                college_due.append(
                    {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str,
                     "id": id})
            elif (tag == "社团活动"):
                club_due.append(
                    {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str,
                     "id": id})
            else:
                other_due.append(
                    {"title": title, "link": link, "due_time": deadline_str, "publish_date": publish_time_str,
                     "id": id})

        due = {
            "college": college_due,
            "club": club_due,
            "lecture": lecture_due,
            "other": other_due
        }

        return {"data": data, "due": due}
