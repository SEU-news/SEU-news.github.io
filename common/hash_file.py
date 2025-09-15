import hashlib
from typing import BinaryIO


def hash_file(file_obj: BinaryIO, algorithm: str = 'md5', chunk_size: int = 8192) -> str:
    """
    计算文件对象的哈希值，支持大文件分块处理

    Args:
        file_obj: 二进制模式打开的文件对象
        algorithm: 哈希算法，默认为'md5'，可选'sha1', 'sha256', 'sha512'等
        chunk_size: 分块大小，默认为8192字节

    Returns:
        str: 文件的十六进制哈希值
    """
    try:
        # 获取哈希算法对象
        hash_func = hashlib.new(algorithm)

        # 重置文件指针到开始位置
        file_obj.seek(0)

        # 分块读取文件内容并更新哈希
        while chunk := file_obj.read(chunk_size):
            hash_func.update(chunk)

        # 再次重置文件指针到开始位置
        file_obj.seek(0)

        return hash_func.hexdigest()

    except (ValueError, AttributeError) as e:
        raise ValueError(f"不支持的哈希算法: {algorithm}") from e
