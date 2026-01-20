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


case_id = ['basis_QueryParadigm_001', 'basis_AccessRecord_001', 'basis_AuthAppInfo_001', 'basis_QueryAuthPolicy_001', 'basis_QueryAppAuthPolicy_001', 'basis_QueryDataStandardAuth_001', 'basis_GetPresetData_001', 'basis_QueryApplicationDetail_001', 'basis_QueryServiceCodeList_001', 'basis_UpdateApplicationV3_001', 'asset_QueryAllAssetList_001', 'asset_QueryDTDAssetList_001', 'asset_QueryAllExternalDependentAssets_001', 'asset_QueryDTDExternalDependentAssets_001', 'modelDriver_GetAppBackendInfo_001', 'customConfig_AddCustomConfig_001', 'customConfig_QueryCustomConfig_001', 'customConfig_QueryCustomConfigDetail_001', 'customConfig_UpdateCustomConfig_001', 'customConfig_QueryCustomConfigShare_001', 'customConfig_DeleteCustomConfig_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("2.0应用详情")
class TestApplicationOverview:

    @allure.story("应用总览")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Application_overview(self, in_data, case_skip):
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
    pytest.main(['test_test_Application_overview.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
