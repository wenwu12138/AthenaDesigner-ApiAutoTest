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


case_id = ['get_ModelDefaultCustomProperties_001', 'businessDir_add_001', 'businessDir_add_param_001', 'businessDir_add_transaction_001', 'businessDir_queryList_001', 'resourceTree_queryListOfSource_001', 'template_all_001', 'task_monitorRule_getMonitorRuleTree_001', 'businessDir_queryIntegrationAutomationInfo_001', 'ai_calculateAILeftCount_001', 'modelDriverTarget_servicecode_queryList_001', 'task_monitorRule_getAllProducts_001', 'activityConfigs_getActivityListByPatternAndApplication_001', 'project_getRootProjects_001', 'pageDesignModel_QueryBindApiListConfig_001', 'process_findProcessList_001', 'modelDriver_queryModelByCode_001', 'businessDir_update_transaction_001', 'action_FindActionsV2_001', 'api_GetRelateApi_001', 'dataEntry_QueryRelateTable_001', 'api_GetFields_001', 'api_GetModelRelatePreviewInfo_001', 'api_add_001', 'tbb_checkBindRelation_001', 'businessDir_delete_001', 'modelDriver_queryBasicModel_001', 'tbb_checkBasicBindRelation_001', 'businessDir_cleanup_basic_001', 'modelDriver_queryParamModel_001', 'tbb_checkParamBindRelation_001', 'businessDir_cleanup_param_001', 'modelDriver_queryApiModelByCode_001', 'api_checkModelBindRelation_001', 'api_cleanup_model_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("2.0应用详情")
class TestBusinessObject:

    @allure.story("业务搭建-业务对象")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Business_object(self, in_data, case_skip):
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
    pytest.main(['test_test_Business_object.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
