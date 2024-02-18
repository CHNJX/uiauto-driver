# -*- coding:utf-8 -*-
# @Time     :2023/2/2 10:41 下午
# @Author   :CHNJX
# @File     :project_generator.py
# @Desc     :项目创造器

import sys
from os import listdir
from os.path import dirname, exists, join

sys.path.append(dirname(sys.path[0]))

from ui_driver.template import Template
from ui_driver import ui_utils


class ProjectGenerator:
    def project_generate(self, project_name, project_type):
        """
        创建项目
        :param project_name: 项目名称
        :param project_type: 项目类型
        :return: None
        """
        if exists(project_name):
            print(f'project {project_name} is already existed')
            return 1
        ui_utils.create_folder(project_name)
        ui_utils.create_folder(join(project_name, 'testcase'))
        ui_utils.create_folder(join(project_name, 'pages'))
        ui_utils.create_folder(join(project_name, 'utils'))
        ui_utils.create_folder(join(project_name, 'resource'))
        for dir_name in listdir(project_name):
            if dir_name == 'resource':
                continue
            cur_dir = join(project_name + '/' + dir_name, '__init__.py')
            ui_utils.write("", cur_dir)
        self.__generate_base_need(project_name, project_type)

    def __generate_base_need(self, project_name, project_type):
        template = Template()
        page_dir = join(project_name, 'page')
        utils_dir = join(project_name, 'utils')
        if project_type == 'airtest':
            ui_utils.write(template.get_content('airtest_base_page.tpl'), join(page_dir, 'airtest_base_page.py'))
            ui_utils.write(template.get_content('common.tpl'), join(utils_dir, 'common.py'))


if __name__ == '__main__':
    template = Template()
    page_dir = join('demo', 'page')
    ui_utils.write(template.get_content('ui_driver/templates/airtest_base_page.tpl'), join(page_dir,
                                                                                           'airtest_base_page.py'))
