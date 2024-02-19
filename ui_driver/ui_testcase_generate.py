# -*- coding:utf-8 -*-
# @Time     :2022/7/31 2:36 下午
# @Author   :CHNJX
# @File     :ui_testcase_generate.py
# @Desc     :动态生成用例
import os

import yaml

from ui_driver.utils.logger import Logger
from ui_driver import global_val
from ui_driver.ui_testcase_object import Testcase


class TestcaseGenerate:

    def __init__(self):
        self.testcase = Testcase()
        self.data = None
        self.current_num = 0  # 存放当前执行到第几条用例  set_up 和 teardown有用
        self.logger = Logger().get_logger()

    def load_case(self, file_path: str):
        """
        加载yaml数据
        :param file_path: yaml文件路劲
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
        self.generate()

    def generate(self):
        """
        将yaml中的步骤进行转换并储存
        """
        for (title, steps) in self.data.items():
            if title == 'set_up':
                self.testcase.set_up.append(steps)
            elif title == 'data':
                self.testcase.data = steps
            elif title == 'set_up_class':
                self.testcase.set_up_class.append(steps)
            elif title == 'teardown':
                self.testcase.teardown.append(steps)
            elif title == 'teardown_class':
                self.testcase.teardown_class.append(steps)
            elif str(title).startswith('test'):
                self.testcase.ids.append(title)
                self.testcase.steps_list.append({title: steps})

    def run_case(self, test_steps: dict):
        """
        执行用例
        :param test_steps: 用例步骤
        """
        current_index = 0
        val_len = None
        global_val.clear_all_data()
        if self.current_num == 0:
            # 确保只会执行一次
            self.testcase.run_setup_class()
        self.current_num += 1
        for (i, v) in test_steps.items():
            # 参数化驱动
            if self.testcase.data.get(i):
                data_dict: dict = self.testcase.data[i]
                while val_len is None or current_index < val_len:
                    # 储存当前参数
                    cur_val = ''
                    for (keys, values) in data_dict.items():
                        val_len = len(values)
                        # 第一次进入时需要进行判断
                        if current_index < len(values):
                            global_val.actual_list[keys] = values[current_index]
                            cur_val = values[current_index]
                    self.logger.info(f'测试用例 - {i}   当前参数：{cur_val}')
                    current_index += 1
                    self.testcase.run(v)
            else:
                self.testcase.run(v)
        if self.current_num == len(self.testcase.steps_list):
            # 确保只会在用例结束后执行
            self.testcase.run_teardown_class()
