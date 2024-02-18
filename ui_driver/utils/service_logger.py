# -*- coding:utf-8 -*-
# @Time     :2023/2/3 7:48 上午
# @Author   :CHNJX
# @File     :service_logger.py
# @Desc     :日志构造器

import logging
import os
import sys
import time
from datetime import datetime


class Logger:
    def __init__(self, logger_name='AirtestLogger'):
        self.logger = logging.getLogger(logger_name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)  # 设置日志级别

            # 创建一个handler，用于写入日志文件
            log_directory = "logs"
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
            log_file_path = os.path.join(log_directory, datetime.now().strftime('%Y-%m-%d') + '.log')
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # 创建一个handler，用于将日志输出到控制台
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 定义handler的输出格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [Line:%(lineno)d] - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # 给logger添加handler
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
