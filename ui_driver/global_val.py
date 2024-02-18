# -*- coding:utf-8 -*-
# @Time     :2022/7/30 6:07 下午
# @Author   :CHNJX
# @File     :global_val.py
# @Desc     :储存全局变量

# 参数化驱动时 存放实际参数的地方
actual_list = {}
# 形参和形参的映射表
val_list = {}
# 存放执行后获取到的实际结果
save_list = {}


def clear_all_data():
    val_list.clear()
    save_list.clear()
    actual_list.clear()
