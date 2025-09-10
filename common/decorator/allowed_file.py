ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename:str)->bool:
    """
    检查文件名是否具有允许的后缀名。

    Args:
        filename (str): 要检查的文件名。

    Returns:
        bool: 如果文件具有允许的后缀名且有效则返回 True，否则返回 False。
    """
    if not filename or '.' not in filename:
        return False

    # 获取小写的文件后缀名（不带点）
    file_extension = filename.rsplit('.', 1)[-1].lower()

    # 检查后缀名是否在允许的集合中
    return file_extension in ALLOWED_EXTENSIONS