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


case_id = ['businessFlow_CreateProcess_001', 'businessFlow_QueryProcess_001', 'businessDir_QueryList_001', 'activityConfigs_GetActivityListByPatternAndApplication_001', 'process_UpsertGeneralTriggerVerify_001', 'processVersion_QueryList_001', 'process_FindProcessById_001', 'resourceTree_QueryListOfSourceRefresh_001', 'businessDir_PartRefresh_001', 'modelDriver_ModelAssignQueryList_001', 'activity_GetActivityList_001', 'businessDir_QueryList_002', 'modelDriver_QueryModelByCodes_001', 'process_UpdateGeneralTriggerProcess_001', 'resourceTree_QueryListOfSourceRefresh_002', 'businessDir_PartRefresh_002', 'processVersion_EffectProcessVersion_001', 'processVersion_QueryVersionList_001', 'resourceTree_QueryListForRefresh_001', 'businessDir_RefreshPart_001', 'modulePublish_PublishSingleModel_001', 'activityConfigs_GetActivityListByPattern_001', 'businessDir_QueryList_003', 'modelDriver_QueryModelByCodes_002', 'processVersion_CreateVersion_001', 'resourceTree_QueryListForRefresh_002', 'businessDir_RefreshPart_002', 'process_FindProcessById_002', 'processVersion_QueryVersionList_002', 'modelDriver_QueryModelAssignList_001', 'processVersion_UpdateRemark_001', 'processVersion_QueryListByCreateDate_001', 'processVersion_RemoveVersion_001', 'processVersion_QueryListNoTimeType_001', 'debug_GetDebugTestData_001', 'debug_DebugProcess_001', 'debug_GetDebugProgress_001', 'debug_GetDebugVariables_001', 'debug_GetDebugResult_001', 'businessFlow_CleanupProcess_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("业务搭建")
class TestProcess:

    @allure.story("业务流")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Process(self, in_data, case_skip):
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
    pytest.main(['test_test_Process.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
