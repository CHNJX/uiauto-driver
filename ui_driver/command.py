# -*- coding:utf-8 -*-
# @Time     :2024/2/18 12:38
# @Author   :CHNJX
# @File     :command.py
# @Desc     :命令工具
import os
import subprocess
import sys
from os.path import dirname, exists
import click as click

from ui_driver.udf import setup_run

sys.path.append(dirname(sys.path[0]))

from ui_driver.project_generator import ProjectGenerator

group = click.Group()


@click.command('start_project')
@click.option('-n', '--project-name', required=True, help='project name')
@click.option('-t', '--project-type', required=True, help='project type:airtest、appium、nvr')
def start_project(project_name, project_type):
    """
    创建项目
    :param project_name: 项目名称
    """
    ProjectGenerator().project_generate(project_name, project_type)


@click.command('run')
@click.option('-c', '--testcase',
              required=True, help='testcase')
@click.option('-t', '--tag',
              required=False, help='testcase')
@click.option('-r', '--reset', help='auto clear report', required=False, default='false',
              type=click.Choice(['true', 'false']))
@click.option('-th', '--threads', help='run with multiple threads', required=False)
def run(testcase, tag, reset, threads):
    """
    运行用例并集成allure报告
    :param threads: 运行的线程数
    :param testcase: 用例路径
    :param tag: 用例标签
    :param reset: 是否重置allure报告
    """
    testcase = setup_run(testcase)
    command = f'pytest -W ignore::DeprecationWarning -v -s {testcase}'
    if reset == 'true':
        if 'win' in sys.platform:
            subprocess.call(f'rmdir /Q /S allure-results', shell=True)
        else:
            subprocess.call(f'rmdir -rf allure-results', shell=True)
    if threads:
        command += f' -n {threads}'
    if tag:
        command += f' -m {tag}'

    subprocess.call(command + ' --alluredir=./allure-results', shell=True)


group.add_command(start_project)
group.add_command(run)


def cmd():
    group.main()

