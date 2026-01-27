#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026-01-27 10:01:44


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


case_id = ['basis_AddBranch_002', 'basis_Compile_002', 'basis_PublishTest_002', 'basis_SwitchPlanTest_002', 'basis_PublishHuaweiProd_002', 'basis_SwitchPlanHuaweiProd_002', 'basis_PublishAzureProd_002', 'basis_SwitchPlanAzureProd_002', 'basis_QueryTenantPipeline_local001', 'basis_PublishTest_local001', 'basis_SwitchPlanTest_local001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("基础功能验证")
class TestBasisFunction002:

    @allure.story("基于已有数据验证基础功能z_2.0应用")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Basis_function002(self, in_data, case_skip):
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
    pytest.main(['test_test_Basis_function002.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
