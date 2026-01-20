#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026-01-20 09:01:20


import allure
import pytest
from utils.read_files_tools.get_yaml_data_analysis import GetTestCase
from utils.assertion.assert_control import Assert
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.regular_control import regular
from utils.requests_tool.teardown_control import TearDownHandler
from utils.assertion.asynchronous_assert import AsynchronousAssert
from utils.cache_process.cache_control import CacheHandler
import datetime
import json


case_id = ['extendConfig_GetCompiledPath_001', 'extendConfig_CreateMongoDataMap_001', 'extendConfig_CreateMongoFieldMap_001', 'extendConfig_QueryAllConfigs_001', 'extendConfig_SaveExtendField_001', 'extendConfig_UpdateExtendField_001', 'extendConfig_DeleteExtendField_001', 'extendConfig_DeleteTableDataConfig_001', 'extendConfig_DeleteFieldConfig_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("2.0应用详情")
class TestExtendconfig:

    @allure.story("业务搭建-扩展信息")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_ExtendConfig(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl(in_data).http_request()
        """
                        处理异步接口断言
                        判断用例是否为发版切板用例
                        如果是的话循环调用查询接口，设定超时次数为100次 100次以内没满足条件抛异常
        """
        TearDownHandler(res).teardown_handle()
        Assert(assert_data=in_data['assert_data'],
               sql_data=res.sql_data,
               request_data=res.body,
               response_data=res.response_data,
               status_code=res.status_code).assert_type_handle()
        # 异步断言
        assert AsynchronousAssert(in_data=in_data, in_data_res=res).deployer_assert() == True


if __name__ == '__main__':
    pytest.main(['test_test_ExtendConfig.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
