# -*- coding:utf-8 -*-
# @Time     :2022/7/31 3:10 下午
# @Author   :CHNJX
# @File     :ui_testcase_object.py
# @Desc     :测试用例的实体类
import numpy

from ui_driver import global_val
from ui_driver.page_generate import PageGenerate, PageGenerateSingleton
from ui_driver.utils.logger import Logger
from ui_driver.utils.utils import Utils


class Testcase:

    def __init__(self):
        self.setup_class = []
        self.setup = []
        self.ids = []
        self.steps_list = []
        self.data = {}
        self.teardown = []
        self.teardown_class = []
        self.logger = Logger().get_logger()
        self.pg = None  # 初始化时不再创建实例

    def get_pg(self):
        """延迟加载 PageGenerate 实例"""
        if self.pg is None:
            self.pg = PageGenerateSingleton.get_instance()
        return self.pg

    # def run(self, test_steps):
    #     """执行用例"""
    #     if self.setup:
    #         for set_up_step in self.setup:
    #             self.run_steps(set_up_step)
    #     self.run_steps(test_steps)
    #     if self.teardown:
    #         for teardown_step in self.teardown:
    #             self.run_steps(teardown_step)

    def run(self, test_steps):
        self.execute_steps(self.setup)
        self.execute_steps(test_steps)
        self.execute_steps(self.teardown)

    def execute_steps(self, steps: list[dict]):
        if not steps:
            return
        for step in steps:
            self.run_step(step)

    def run_step(self, steps: dict):
        """
        执行测试步骤
        :param steps: 步骤
        """
        for action, value in steps.items():
            try:
                if action == 'print':
                    print(value)
                elif '.' in action:
                    self.handle_page_action(action, value)
                elif 'validate' in action:
                    self.handle_validation(action, value)
            except Exception as e:
                self.logger.error(f"Error executing step {action}: {e}")
                raise
        # for step in steps:
        #     for (k, v) in step.items():
        #         k: str
        #         if k == 'print':
        #             print(v)
        #         elif '.' in k:
        #             page_method = k.split('.')
        #             if v:
        #                 run_value = Utils.resolve_dict(v, global_val.actual_list)
        #                 global_val.val_list.update(run_value)
        #             self.get_pg().run_action(page_method[0], page_method[1])
        #         elif 'validate' in k:
        #             # 进行断言处理
        #             for assert_content in v:
        #                 for (assert_method, assert_value) in assert_content.items():
        #                     assert_method: str
        #                     if len(assert_value) == 1:
        #                         run_value = assert_value[0]
        #                         if isinstance(run_value, str) and '$' in run_value:
        #                             run_value = Utils.replace_form_2_actual(run_value, global_val.save_list)
        #                         expect_value = ''
        #                         self.logger.info(f'进行断言 断言方式：{assert_method} 实际值：{run_value}')
        #                     else:
        #                         expect_value = assert_value[0]
        #                         run_value = assert_value[1]
        #                         if isinstance(run_value, str) and '$' in run_value:
        #                             run_value = Utils.replace_form_2_actual(run_value, global_val.save_list)
        #                         if isinstance(expect_value, str) and '$' in expect_value:
        #                             expect_value = Utils.replace_form_2_actual(expect_value, global_val.actual_list)
        #                         self.logger.info(f'进行断言 断言方式：{assert_method} 预期值：{expect_value} 实际值：{run_value}')
        #                     try:
        #                         if assert_method.startswith('in'):
        #                             if assert_method.endswith('each') and type(run_value) is list:
        #                                 for rv in run_value:
        #                                     assert expect_value in rv
        #                             else:
        #                                 assert expect_value in run_value
        #                         elif assert_method == 'equals':
        #                             assert expect_value == run_value
        #                         elif assert_method == 'true':
        #                             self.logger.info(type(run_value))
        #                             if isinstance(run_value, numpy.bool_):
        #                                 assert run_value
        #                             else:
        #                                 assert run_value and '${' not in run_value
        #                     except Exception as e:
        #                         self.logger.error(f'断言失败 断言方式：{assert_method} 预期值：{expect_value} 实际值：{run_value}')
        #                         raise e

    def handle_page_action(self, action, value):
        page_method = action.split('.')
        if value:
            run_value = Utils.resolve_dict(value, global_val.actual_list)
            global_val.val_list.update(run_value)
        self.get_pg().run_action(page_method[0], page_method[1])

    def handle_validation(self, action, values):
        for assert_content in values:
            for assert_method, assert_value in assert_content.items():
                self.perform_assertion(assert_method, assert_value)

    def perform_assertion(self, assert_method: str, assert_value):
        if len(assert_value) == 1:
            run_value = assert_value[0]
            if isinstance(run_value, str) and '$' in run_value:
                run_value = Utils.replace_form_2_actual(run_value, global_val.save_list)
            expect_value = ''
            self.logger.info(f'进行断言 断言方式：{assert_method} 实际值：{run_value}')
        else:
            expect_value = assert_value[0]
            run_value = assert_value[1]
            if isinstance(run_value, str) and '$' in run_value:
                run_value = Utils.replace_form_2_actual(run_value, global_val.save_list)
            if isinstance(expect_value, str) and '$' in expect_value:
                expect_value = Utils.replace_form_2_actual(expect_value, global_val.actual_list)
            self.logger.info(f'进行断言 断言方式：{assert_method} 预期值：{expect_value} 实际值：{run_value}')
        try:
            if assert_method.startswith('in'):
                if assert_method.endswith('each') and type(run_value) is list:
                    for rv in run_value:
                        assert expect_value in rv
                else:
                    assert expect_value in run_value
            elif assert_method == 'equals':
                assert expect_value == run_value
            elif assert_method == 'true':
                self.logger.info(type(run_value))
                if isinstance(run_value, numpy.bool_):
                    assert run_value
                else:
                    assert run_value and '${' not in run_value
        except Exception as e:
            self.logger.error(f'断言失败 断言方式：{assert_method} 预期值：{expect_value} 实际值：{run_value}')
            raise e

    def run_setup_class(self):
        """
        执行 setup_class
        :return:
        """
        if self.setup_class:
            for setup_class_step in self.setup_class:
                self.run_step(setup_class_step)

    def run_teardown_class(self):
        """
        执行 teardown_class
        """
        if self.teardown_class:
            for teardown_class_step in self.teardown_class:
                self.run_step(teardown_class_step)
