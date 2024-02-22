# @Time     :2022/7/30 5:22 下午
# @Author   :CHNJX
# @File     :page_generate.py
# @Desc     :将yaml转换成页面
import importlib
import logging
import os
import time

import yaml
from ui_driver.utils.utils import Utils

from ui_driver import global_val
from ui_driver.utils import utils


# 动态加载BasePage
def load_base_page():
    with open('label.txt', 'r') as label:
        content = label.read().strip()
        if content in ['airtest', 'appium']:
            module_path = f"ui_driver.{content}_base_page"
            module = importlib.import_module(module_path)
            return getattr(module, 'BasePage')
        else:
            raise ImportError(f"Unsupported framework '{content}' in label.txt")


BasePage = load_base_page()


class PageGenerateSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PageGenerate()
        return cls._instance


class PageGenerate(BasePage):
    page_list = {}
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
            self.logger.error('当前页面不存在' + action_name + '方法')
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
                'click_image': lambda: self.click_image(page_image_dir + run_value),
                'click': self.click,
                'text': lambda: setattr(self, '_result', self.get_ele_text()),
                'save': lambda: global_val.save_list.update({run_value: self._result}),
                'sleep': lambda: time.sleep(run_value),
                'is_image_exist': lambda: self.is_image_exist(page_image_dir + run_value),
                'find_image': lambda: self.find_image(page_image_dir + run_value),
                'input': lambda: self.handle_input_action(run_value),
                'return': lambda: self.handle_return_action(run_value),
                'find': lambda: self.handle_find_action(run_value),
                'if': lambda: self.handle_if_action(key, run_value, page_name),
                'screen': lambda: self.get_current_screen(run_value),
                'compare': lambda: self.compare_image(page_name, *run_value)
            }

            for (key, value) in step.items():
                key: str
                run_value = value
                if 'if' in key:
                    action_mapping['if']()
                elif key in action_mapping:
                    action_mapping[key]()
                elif key.startswith("$(") and key.endswith(")"):
                    self.logger.info(key)
                    self.handle_custom_method(key, run_value)

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

    def handle_custom_method(self, reference, run_value):
        """
        解析并执行YAML中引用的自定义方法
        :param reference: 使用${}包裹的方法引用字符串
        :param run_value: 入参
        """
        # 移除${}并分割模块名和方法名
        method_name = reference.strip("$()")
        self.logger.info(f'method_name:{method_name}')
        try:
            # 自定义方法都存放在 custom_methods 模块中
            custom_methods_module = importlib.import_module("custom_methods")
            cls = getattr(custom_methods_module, 'CustomMethods')
            instance = cls()
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)
                # 如果需要传递参数，可以在这里处理参数的传递
                if isinstance(run_value, list) and len(run_value) != 0:
                    run_value = tuple(run_value)
                    result = method(instance, *run_value)
                else:
                    result = method()
                return result
            else:
                logging.error(f"未找到自定义方法: {method_name}")
        except ImportError as e:
            logging.error(f"导入 custom_methods 模块失败: {e}")
        except TypeError as e:
            logging.error(f"参数类型或数量错误: {e}")
        except ValueError as e:
            logging.error(f"参数值错误: {e}")
        except Exception as e:
            logging.error(f"执行自定义方法时发生未知错误: {e}")
