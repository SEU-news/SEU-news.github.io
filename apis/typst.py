import json
import logging
import re
from datetime import time, datetime

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

    def _process_content_description(self, content):
        """
        处理内容描述，将文本和链接分离
        
        参数:
            content (str): 原始内容文本
            
        返回:
            list: 包含文本和链接的元素列表
        """
        try:
            description_parts = re.split(LINK_REGEX, content)
        except:
            return [{"type": "text", "content": content}]
        
        processed_parts = []
        for part in description_parts:
            if is_valid_url(part):
                processed_parts.append({"type": "link", "content": part})
            else:
                processed_parts.append({"type": "text", "content": part})
                
        return processed_parts

    def _sort_content_by_category(self, content_items, is_deadline_content=False):
        """
        根据类别对内容进行分类
        
        参数:
            content_items (QuerySet): 内容项查询集
            is_deadline_content (bool): 是否为截止日期内容
            
        返回:
            dict: 分类后的内容字典
        """
        college, club, lecture, other = [], [], [], []
        
        for content_item in content_items:
            # 提取通用字段
            title = content_item.short_title if content_item.short_title else content_item.title
            link = content_item.link
            tag = content_item.tag
            type = content_item.type
            id = content_item.id
            
            # 构造内容项
            if is_deadline_content:
                # 截止日期内容项
                deadline_str = content_item.deadline.strftime('%Y-%m-%d %H:%M:%S') if content_item.deadline else None
                publish_time_str = content_item.publish_at.strftime('%Y-%m-%d %H:%M:%S') if content_item.publish_at else None
                
                item = {
                    "title": title,
                    "link": link,
                    "due_time": deadline_str,
                    "publish_date": publish_time_str,
                    "id": id
                }
            else:
                # 普通内容项
                if content_item.type == "DDLOnly":
                    continue
                    
                description = self._process_content_description(content_item.content)
                item = {
                    "title": title,
                    "description": description,
                    "link": link,
                    "id": id
                }
            
            # 根据标签或类型分类
            if (tag == "讲座" or type == "讲座"):
                lecture.append(item)
            elif tag == "院级活动":
                college.append(item)
            elif tag == "社团活动":
                club.append(item)
            else:
                other.append(item)
                
        return {
            "college": college,
            "club": club,
            "lecture": lecture,
            "other": other
        }

    def _generate_typst_data(self, date_str):
        """生成指定日期的typst数据"""
        today_str = timezone.now().strftime("%Y-%m-%d")
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

        # 获取当日发布的普通内容，按publish_at索引优化查询条件顺序
        content_query = Content.objects.filter(
            publish_at__gte=start_of_day,
            publish_at__lte=end_of_day
        )
        
        # 对普通内容进行分类
        categorized_content = self._sort_content_by_category(content_query, is_deadline_content=False)

        data = {
            "date": date_str,
            "no": 1,
            "first-v": 3,
            "lecture-v": 3,
            "other-v": 3,
            "college-v": 3,
            "club-v": 3,
            "college": categorized_content["college"],
            "club": categorized_content["club"],
            "lecture": categorized_content["lecture"],
            "other": categorized_content["other"]
        }

        # 获取截止日期内容，筛选deadline在目标日期当天或之前，且publish_at在目标日期当天或之前的内容
        due_content = Content.objects.filter(
            deadline__isnull=False,
            deadline__gte=start_of_day,
            publish_at__lte=end_of_day
        ).order_by('deadline')

        # 对截止日期内容进行分类
        categorized_due_content = self._sort_content_by_category(due_content, is_deadline_content=True)

        due = {
            "college": categorized_due_content["college"],
            "club": categorized_due_content["club"],
            "lecture": categorized_due_content["lecture"],
            "other": categorized_due_content["other"]
        }

        return {"data": data, "due": due}
