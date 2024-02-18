# @Time     :2022/7/30 5:22 下午
# @Author   :CHNJX
# @File     :page_generate.py
# @Desc     :将yaml转换成页面
import importlib
import logging
import os
import platform
import time

import yaml

from ui_driver import global_val
from ui_driver.airtest_base_page import BasePage
from ui_driver.utils import utils


class PageGenerate(BasePage):
    page_list = {}
    res = None
    yaml_cache = {}

    def load_yaml(self, filepath):
        # 使用文件修改时间来检测文件是否被修改
        last_modified = os.path.getmtime(filepath)
        if filepath not in self.yaml_cache or self.yaml_cache[filepath]['last_modified'] != last_modified:
            with open(filepath, 'r', encoding='utf-8') as file:
                self.yaml_cache[filepath] = {
                    'content': yaml.safe_load(file),
                    'last_modified': last_modified
                }
        return self.yaml_cache[filepath]['content']

    def generate_page(self, page_name: str):
        """
        获取yaml中的页面并进行储存
        :param page_name: 页面名称
        """
        if not self.page_list.get(page_name):
            # 先获取文件路径
            file_path = utils.Utils.search_file(os.path.join('pages/'),
                                                f'{page_name}.yaml')
            cur_page = self.load_yaml(file_path)
            for (key, value) in cur_page.items():
                self.page_list[key] = value
        return self.page_list.get(page_name)['actions']

    def run_action(self, page_name, action_name: str):
        """
        调用对应页面方法方法
        :param page_name: 页面名称
        :param action_name: 方法名称
        """
        # 先对页面进行转换
        actions = self.generate_page(page_name)
        if not actions.get(action_name):
            logging.error('当前页面不存在' + action_name + '方法')
            return
        self.run(page_name, actions[action_name])

    def run(self, page_name, action: list[dict]):
        """
        执行具体的action步骤
        :param action: 步骤列表  type：list[dict]
        """
        page_image_dir = f'resource/{page_name}/'
        for step in action:
            action_mapping = {
                'init': lambda: self.set_device_ip(run_value),
                'click': self.click,
                'text': lambda: setattr(self, '_result', self.get_ele_text()),
                'save': lambda: global_val.save_list.update({run_value: self._result}),
                'sleep': lambda: time.sleep(run_value),
                'find_image': lambda: self.find_image(page_image_dir + run_value),
                'input': lambda: self.handle_input_action(run_value),
                'return': lambda: self.handle_return_action(run_value),
                'find': lambda: self.handle_find_action(run_value),
                'if': lambda: self.handle_if_action(key, run_value, page_name)
            }

            for (key, value) in step.items():
                key: str
                run_value = value
                if 'if' in key:
                    action_mapping['if']()
                elif key in action_mapping:
                    action_mapping[key]()
                elif '.' in key:
                    self.handle_dynamic_import(key)

    def set_device_ip(self, ip):
        self.device_ip = ip

    def handle_if_action(self, key, run_value, page_name):
        """
        处理if逻辑
        """
        run_key = key[3:]
        if run_key in global_val.val_list.keys():
            self.run(page_name, run_value)

    def handle_find_action(self, run_value):
        """
        处理 'find' 操作
        """
        locator = {run_value[0]: run_value[1]}
        if '${' in locator:
            locator = Utils.resolve_dict(locator, global_val.val_list)
        self.find_element(locator)

    def handle_input_action(self, run_value):
        """
        处理 'input' 操作
        """
        if '${' in str(run_value):
            run_value = Utils.replace_form_2_actual(run_value, global_val.val_list)
        self.input(run_value)

    def handle_return_action(self, run_value):
        """
        处理 'return' 操作
        """
        if 'page' in run_value:
            self.generate_page(run_value)

    def handle_dynamic_import(self, key):
        """
        处理动态导入的逻辑
        """
        module_method = key.split('.')
        try:
            module = importlib.import_module("token_helper")
        except Exception as e:
            pro_path = os.path.dirname(os.path.dirname(__file__))
            if platform.system() == 'Windows':
                project_package = pro_path.split("\\")[-1]
            else:
                project_package = pro_path.split("/")[-1]
            module = importlib.import_module(f"{project_package}.token_helper")

        r = getattr(module, module_method[1])()
        if isinstance(r, str):
            self.res = r
