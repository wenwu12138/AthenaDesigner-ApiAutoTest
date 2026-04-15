#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 10:56
# @Author : 闻武
"""
日志封装，可设置不同等级的日志颜色，适配PyInstaller打包环境
"""
import logging
from logging import handlers
from typing import Text
import colorlog
import time
import os
import sys
from common.setting import ensure_path_sep


# 控制控制台编码和日志编码统一 避免乱码
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass

# Align console streams to UTF-8 so manual pytest runs print Chinese logs correctly.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class LogHandler:
    """ 日志打印封装，支持PyInstaller打包环境 """
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(
            self,
            filename: Text,
            level: Text = "info",
            when: Text = "D",
            fmt: Text = "%(levelname)-8s%(asctime)s%(name)s:%(filename)s:%(lineno)d %(message)s"
    ):
        # 确定日志文件的基础目录（适配PyInstaller打包）
        self.base_dir = self._get_base_dir()
        # 确保日志目录存在
        self._ensure_log_dir()

        # 修正文件名路径，使用基础目录
        filename = os.path.join(self.base_dir, filename)
        self.logger = logging.getLogger(filename)

        # 防止日志重复输出
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        formatter = self.log_color()

        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))
        # 往屏幕上输出
        screen_output = logging.StreamHandler(sys.stdout)
        # 设置屏幕上显示的格式
        screen_output.setFormatter(formatter)
        # 往文件里写入#指定间隔时间自动生成文件的处理器
        time_rotating = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=3,
            encoding='utf-8'
        )
        # 设置文件里写入的格式
        time_rotating.setFormatter(format_str)
        # 把对象加到logger里
        self.logger.addHandler(screen_output)
        self.logger.addHandler(time_rotating)
        self.log_path = ensure_path_sep(os.path.join(self.base_dir, 'logs\\log.log'))

    @classmethod
    def _get_base_dir(cls) -> Text:
        """获取基础目录，适配PyInstaller打包环境"""
        if getattr(sys, 'frozen', False):
            # 打包后的临时目录
            return sys._MEIPASS
        else:
            # 开发环境下的项目根目录（根据实际项目结构调整）
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _ensure_log_dir(self) -> None:
        """确保日志目录存在"""
        log_dir = os.path.join(self.base_dir, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            # 可选项：在开发环境下打印日志目录信息
            if not getattr(sys, 'frozen', False):
                print(f"日志目录已创建: {log_dir}")

    @classmethod
    def log_color(cls):
        """ 设置日志颜色 """
        log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }

        formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=log_colors_config
        )
        return formatter


# 生成日志文件名时使用相对路径，避免硬编码斜杠
now_time_day = time.strftime("%Y-%m-%d", time.localtime())
# 使用os.path.join处理路径，增强跨平台兼容性
INFO = LogHandler(os.path.join('logs', f"info-{now_time_day}.log"), level='info')
ERROR = LogHandler(os.path.join('logs', f"error-{now_time_day}.log"), level='error')
WARNING = LogHandler(os.path.join('logs', f'warning-{now_time_day}.log'))

if __name__ == '__main__':
    ERROR.logger.error("测试错误日志")
    INFO.logger.info("测试信息日志")
    WARNING.logger.warning("测试警告日志")
