import logging
import os
import sys
import threading


class Config:
    def __init__(self):
        logging.info("[Config] 初始化配置")
        self._lock = threading.RLock()
        self.config = self._read_config()
        self._supplement_config()
        logging.info("[Config] 配置初始化完成")

    def _supplement_config(self):
        logging.info("[Config] 补充配置项")
        self.config['python.version'] = sys.version
        if os.name=='nt':
            self.config['os.name']='windows'
        elif os.name=='posix':
            self.config['os.name']='linux'
        else:
            self.config['os.name']='unknown'

    def _read_config(self, file_path="config.txt", delimiter=':'):
        """
        从文本文件中读取配置项。

        参数:
            file_path (str): 配置文件的路径。
            delimiter (str): 用于分隔键和值的分隔符，默认为冒号（:）。

        返回:
            dict: 一个字典，键是配置项名称，值是对应的配置值。
        """
        config = {}
        logging.info(f"[Config] 正在读取配置文件 '{file_path}'")
        try:
            with self._lock:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()  # 去除行首尾的空白字符（包括换行符）
                        if not line:  # 确保不是空行
                            continue
                        if line.startswith('#'):
                            logging.info(f"[Config] 注释: {line}")
                            continue
                        parts = line.split(delimiter)
                        if len(parts) == 2:
                            key, value = parts
                            config[key] = value
                            logging.info(f"[Config] 已读取配置项: {key}")
                        else:
                            logging.warn(f"[Config] 警告: 跳过格式无效的行: {line}")
        except FileNotFoundError:
            logging.error(f"[Config] 错误: 文件未找到 '{file_path}'")
            sys.exit(1)
        except Exception as e:
            logging.error(f"[Config] 读取文件时发生错误: {e}")
            sys.exit(1)
        return config

    def get_config_value(self, key):
        """
        获取指定键的配置值。

        参数:
            key (str): 配置项键名。

        返回:
            str: 对应的配置值，如果没有找到，则返回None。
        """
        with self._lock:
            logging.info(f"[Config] 获取配置项: {key}")
            return self.config.get(key)


GLOBAL_CONFIG = Config()
