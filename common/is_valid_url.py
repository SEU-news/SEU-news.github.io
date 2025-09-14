from urllib.parse import urlparse
from typing import Union


def is_valid_url(url: str, allowed_schemes: Union[list, tuple] = None) -> bool:
    """
    验证URL字符串的基本格式有效性

    Args:
        url: 要验证的URL字符串
        allowed_schemes: 允许的协议列表，默认为('http', 'https', 'ftp')

    Returns:
        bool: URL格式是否有效
    """
    if allowed_schemes is None:
        allowed_schemes = ('http', 'https', 'ftp')

    try:
        result = urlparse(url)
        # 检查必需组件和允许的协议
        return all([
            result.scheme in allowed_schemes,
            result.netloc,  # 确保有网络位置信息
            '.' in result.netloc or result.netloc == 'localhost'  # 基本域名格式检查
        ])
    except (ValueError, AttributeError):
        return False

if __name__ == '__main__':
    # 基本使用
    print(is_valid_url("https://example.com"))  # True
    print(is_valid_url("invalid-url"))  # False

    # 自定义允许的协议
    print(is_valid_url("ftp://ftp.example.com", ['ftp']))  # True
    print(is_valid_url("https://example.com", ['ftp']))  # False

    # 测试边界情况
    test_urls = [
        "http://localhost:8080",
        "https://sub.domain.co.uk/path?query=value",
        "mailto:user@example.com",  # 不在默认允许协议中
        "just-a-string"
    ]

    for url in test_urls:
        print(f"{url}: {is_valid_url(url)}")