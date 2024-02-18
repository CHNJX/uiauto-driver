import logging
import os
from os.path import join

from ui_driver import ui_utils
from ui_driver.template import Template


def setup_run(testcase: str):
    if testcase.endswith('yaml') or testcase.endswith('yml'):
        # 先判断目录下是否存在相同名称的py用例
        testcase = testcase.split('.')[0] + '.py'
        if not os.path.exists(testcase):
            # 创建对应的py文件
            template = Template()
            ui_utils.write(template.get_content('testcase.tpl'), testcase)
    return testcase


class UIDriver:

    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)

