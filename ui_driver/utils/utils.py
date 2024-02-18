# -*- coding:utf-8 -*-
# @Time     :2022/7/31 6:04 下午
# @Author   :CHNJX
# @File     :utils.py
# @Desc     :方法模块

import os
import random
import time

from jsonpath import jsonpath

from ui_driver.utils.service_logger import Logger


class Utils:
    workdir = os.path.split(os.path.realpath(__file__))[0]
    PLACEHOLDER_PREFIX = '${'
    PLACEHOLDER_SUFFIX = '}'
    logger = Logger().get_logger()
    conn = ''
    cursor = ''

    @classmethod
    def jsonpath(cls, json_object, expr):
        return jsonpath(json_object, expr)

    @classmethod
    def replace_form_2_actual(cls, text: str, parameter: dict):
        """
        转换字符串中携带的占位符
        """
        if parameter is None or len(parameter) == 0 or text is None or text == '':
            return text
        # 计算占位符的起始位置
        start_index = text.find(cls.PLACEHOLDER_PREFIX)
        while start_index != -1:
            # 获取占位符最后的索引
            end_index = text.find(cls.PLACEHOLDER_SUFFIX, start_index + len(cls.PLACEHOLDER_PREFIX))
            if end_index != -1:
                # 取出要替换的变量名
                formal = text[start_index + len(cls.PLACEHOLDER_PREFIX):end_index]
                # 获取占位符后的索引  一遍往后遍历 替换所有占位符
                next_index = end_index + len(cls.PLACEHOLDER_SUFFIX)
                try:
                    actual = parameter[formal]
                    if actual is not None and actual != '':
                        if type(actual) is str:
                            # 替换占位符
                            text = text.replace('${' + formal + '}', actual)
                            next_index = start_index + len(actual)
                            # 替换一次后 查看后续位置是否存在占位符  继续替换
                            start_index = text.find(cls.PLACEHOLDER_PREFIX, next_index)
                        else:
                            text = actual
                            start_index = -1
                    else:
                        cls.logger.error("Could not resolve placeholder '" + formal + "' in [" + text + "] ")
                        start_index = -1
                except Exception as e:
                    cls.logger.error(
                        "Could not resolve placeholder '" + formal + "' in [" + text + "]: " + e.__str__())
                    start_index = -1

            else:
                start_index = -1
        return text

    @classmethod
    def resolve_dict(cls, dic: dict, parameter: dict):
        """替换字典中值的占位符"""
        if parameter is None or len(parameter) == 0 or dic is None or len(dic) == 0:
            return dic
        res = {}
        for key, value in dic.items():
            if cls.PLACEHOLDER_PREFIX in value:
                res[key] = cls.replace_form_2_actual(value, parameter)
        return res

    @classmethod
    def search_file(cls, dirPath, fileName):
        """
        遍历目录找到目标文件
        :param dirPath: 文件路径
        :param fileName: 目标文件名称
        :return: 文件绝对路径
        """
        dirs = os.listdir(dirPath)  # 查找该层文件夹下所有的文件及文件夹，返回列表
        for currentFile in dirs:  # 遍历列表
            file_path = dirPath + '/' + currentFile
            if os.path.isdir(file_path):  # 如果是目录则递归，继续查找该目录下的文件
                cls.search_file(file_path, fileName)
            elif currentFile == fileName:
                return file_path

    @classmethod
    def get_random(cls, num1, num2):
        """
        获取随机数
        :param num1: 随机数左边界
        :param num2: 随机数右边界
        :return: 随机数
        """
        return random.Random().randint(num1, num2)

    @classmethod
    def get_time_stamp(cls):
        """
        获取当前时间戳
        :return: 时间戳
        """
        return int(time.time())

    @classmethod
    def get_random_num(cls, formal_str):
        """
        获取随机数占位符的范围
        """
        if "random" not in formal_str:
            cls.logger.info('没有找到占位符')
            return 0

        # 匹配上 random中的范围
        try:
            random_range = re.match(r'.*{random\((.*?)\)}', formal_str, flags=0).group(1)
            min_max = random_range.split(',')
            min_range = int(min_max[0])
            max_range = int(min_max[1])
            return [min_range, max_range]
        except Exception as e:
            cls.logger.error('随机数占位符格式错误')
            return

    # def create_conn(self):
    #     if not self.conn:
    #         self.conn = pymysql.connect(charset='utf8', **database_config)
    #         self.cursor = self.conn.cursor()
    #
    # def close_conn(self):
    #     if self.conn:
    #         self.conn.close()
    #
    # def excuse_sql(self, sql_str, params=None):
    #     self.create_conn()
    #     self.conn.ping(reconnect=True)
    #     self.cursor.execute(sql_str, params)
    #     # 判断是否为查询语句
    #     if 'select' in sql_str:
    #         return self.cursor.fetchone()
    #     else:
    #         self.conn.commit()
    #         return self.cursor.fetchone()