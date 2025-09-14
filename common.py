import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from global_static import SHANGHAI_TZ


def get_timezone_aware_datetime(date_str):
    """
    将字符串日期转换为时区感知的datetime对象

    参数:
        date_str (str): 日期字符串，格式为'YYYY-MM-DD'

    返回:
        datetime: 时区感知的datetime对象

    异常:
        ValueError: 当日期字符串格式不正确时抛出
    """
    # 将字符串解析为naive datetime对象
    naive_dt = datetime.strptime(date_str, '%Y-%m-%d')
    # 使用上海时区对象为datetime添加时区信息
    return SHANGHAI_TZ.localize(naive_dt)


def fetch_title(url):
    """
    从指定URL获取网页标题

    该函数通过发送HTTP请求获取网页内容，解析HTML中的<title>标签或og:title元标签来提取网页标题。
    采用流式下载和部分解析的方式，提高效率并减少内存占用。

    参数:
        url (str): 目标网页的URL地址

    返回值:
        str: 成功时返回网页标题，失败时返回"标题获取失败"
    """
    # 最多尝试2次获取标题
    for _ in range(2):
        try:
            # 设置请求头，模拟浏览器访问
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # 发送GET请求，启用流式下载以支持大文件处理
            with requests.get(url, headers=headers, stream=True, timeout=5) as response:
                response.raise_for_status()
                partial_content = ""
                # 分块读取响应内容，提高处理效率
                for chunk in response.iter_content(chunk_size=4096):
                    partial_content += chunk.decode('utf-8', errors='replace')
                    # 当读取到</head>标签时，解析已获取的内容提取标题
                    if "</head>" in partial_content.lower():
                        soup = BeautifulSoup(partial_content, 'html.parser')
                        # 优先查找Open Graph标题元标签
                        meta_tag = soup.find("meta", property="og:title")
                        if meta_tag and meta_tag.get("content"):
                            return meta_tag.get("content")
                        # 查找传统的<title>标签
                        title_tag = soup.find("title")
                        if title_tag and title_tag.string:
                            return title_tag.string.strip()
            # 如果未在<head>内找到标题，则解析完整内容
            soup = BeautifulSoup(partial_content, 'html.parser')
            meta_tag = soup.find("meta", property="og:title")
            if meta_tag and meta_tag.get("content"):
                return meta_tag.get("content")
        except Exception as e:
            # 记录获取标题失败的日志信息
            logging.warning(f"获取标题失败，URL: {url}, 错误: {str(e)}")
    return "标题获取失败"

