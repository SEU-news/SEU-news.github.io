"""
发布工具函数

从Flask的apis/typst.py移植，生成Flask兼容的Typst JSON数据
"""

import logging
import os
import re
import subprocess
from datetime import time, datetime

from api.django_models import Content


logger = logging.getLogger(__name__)

# 链接正则表达式
LINK_REGEX = re.compile(
    r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)"
)


def is_valid_url(url: str) -> bool:
    """
    验证URL字符串的基本格式有效性

    Args:
        url: 要验证的URL字符串

    Returns:
        bool: URL格式是否有效
    """
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        allowed_schemes = ('http', 'https', 'ftp')
        return all([
            result.scheme in allowed_schemes,
            result.netloc,
            '.' in result.netloc or result.netloc == 'localhost'
        ])
    except (ValueError, AttributeError):
        return False


def process_content_description(content):
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


def sort_content_by_category(content_items, is_deadline_content=False):
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
        type_ = content_item.type
        id = content_item.id

        # 构造内容项
        if is_deadline_content:
            # 截止日期内容项：deadline 和 publish_at 必须都有值
            if not content_item.deadline or not content_item.publish_at:
                logger.debug(f"跳过截止日期内容: {title} (deadline={content_item.deadline}, publish_at={content_item.publish_at})")
                continue

            deadline_str = content_item.deadline.strftime('%Y-%m-%d %H:%M:%S')
            publish_time_str = content_item.publish_at.strftime('%Y-%m-%d %H:%M:%S')

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

            description = process_content_description(content_item.content)
            item = {
                "title": title,
                "description": description,
                "link": link,
                "id": id
            }

        # 根据标签或类型分类
        if (tag == "讲座" or type_ == "讲座"):
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


def generate_typst_data(date_str, base_dir=None):
    """
    生成指定日期的Flask兼容Typst JSON数据

    参数:
        date_str (str): 日期字符串，格式为 YYYY-MM-DD
        base_dir (str, optional): 项目根目录路径。如果为None，自动获取

    返回:
        dict: Flask格式的Typst数据 {"data": {...}, "due": {...}}
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logger.info(f"生成typst数据，日期: {date_str}")

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # 创建当天的开始和结束时间
        start_of_day = datetime.combine(target_date, time.min)
        end_of_day = datetime.combine(target_date, time.max)
        logger.info(f"查询时间范围: {start_of_day} 到 {end_of_day}")

    except ValueError as e:
        logger.error(f"日期解析失败: {e}")
        # 使用当前时间作为默认值
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # 获取当日发布的普通内容
    content_query = Content.objects.filter(
        status='published',
        publish_at__gte=start_of_day,
        publish_at__lte=end_of_day
    )

    # 对普通内容进行分类
    categorized_content = sort_content_by_category(content_query, is_deadline_content=False)

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

    # 获取截止日期内容，筛选deadline在目标日期当天之后（未到期）的内容
    # 修改：使用 deadline__gt 而不是 deadline__gte
    due_content = Content.objects.filter(
        status='published',
        deadline__isnull=False,
        deadline__gt=end_of_day
    ).order_by('deadline')

    # 对截止日期内容进行分类
    categorized_due_content = sort_content_by_category(due_content, is_deadline_content=True)

    due = {
        "college": categorized_due_content["college"],
        "club": categorized_due_content["club"],
        "lecture": categorized_due_content["lecture"],
        "other": categorized_due_content["other"]
    }

    return {"data": data, "due": due}


def compile_typst_pdf(json_path, output_path, fonts_dir=None, template_path=None, typst_cmd=None, base_dir=None):
    """
    调用Typst编译器生成PDF

    参数:
        json_path (str): JSON数据文件路径
        output_path (str): 输出PDF文件路径
        fonts_dir (str, optional): 字体目录路径
        template_path (str, optional): Typst模板文件路径
        typst_cmd (str, optional): Typst编译器命令路径
        base_dir (str, optional): 项目根目录路径

    返回:
        dict: {"success": bool, "message": str, "output_path": str or None}

    异常:
        subprocess.CalledProcessError: Typst编译失败时抛出
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 默认配置
    if template_path is None:
        template_path = os.path.join(base_dir, 'static', 'news_template.typ')

    if typst_cmd is None:
        # 优先使用项目根目录下的 typst 可执行文件
        exe_path = os.path.join(base_dir, 'typst.exe') if os.name == 'nt' else os.path.join(base_dir, 'typst')
        if os.path.exists(exe_path):
            typst_cmd = exe_path
        else:
            # 回退到 PATH 中的 typst 命令
            typst_cmd = 'typst'

    # 构建命令，添加 --font-path 参数指定字体目录（参考Flask原项目）
    # 这是正确的方式来指定字体，解决中文乱码问题
    cmd = [typst_cmd, 'compile', '--font-path', fonts_dir if fonts_dir else base_dir, template_path, output_path]

    # 不再设置环境变量 FONT_PATH，Typst不使用这个环境变量
    env = os.environ.copy()

    logger.info(f"执行Typst编译: {' '.join(cmd)}")
    logger.info(f"base_dir: {base_dir}")
    logger.info(f"template_path: {template_path}")
    logger.info(f"output_path: {output_path}")
    logger.info(f"json_path: {json_path}")

    try:
        # 执行编译命令，使用绝对路径
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )

        logger.info(f"Typst编译成功: {output_path}")
        logger.info(f"stdout: {result.stdout}")
        return {
            "success": True,
            "message": "PDF生成成功",
            "output_path": output_path
        }

    except subprocess.CalledProcessError as e:
        logger.error(f"Typst编译失败: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return {
            "success": False,
            "message": f"Typst编译失败: {e.stderr}",
            "output_path": None
        }
    except Exception as e:
        logger.error(f"PDF生成过程中发生错误: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"PDF生成失败: {str(e)}",
            "output_path": None
        }
