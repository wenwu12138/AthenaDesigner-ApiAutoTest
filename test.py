#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/17 15:00  
# @Author  : wenwu        
# @Desc    :      
# @File    : test.py       
# @Software: PyCharm

"""
配置管理模块 - 支持环境隔离的动态配置平铺
"""
import os
import yaml
from typing import Dict, Any
from utils.read_files_tools.yaml_control import GetYamlData
from common.setting import ensure_path_sep
from utils.other_tools.models import Config


class City():
    def __init__(self,age):
        self.age = age

    def get_age(self):
        return self.age



if __name__ == '__main__':
    test_age1 = 18
    city = City(age=test_age1)
    test_age1 =19
    print(city.get_age());
