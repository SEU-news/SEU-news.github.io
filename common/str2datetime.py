from datetime import datetime

from global_static import SHANGHAI_TZ


def str2datetime(date_str: str):
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
