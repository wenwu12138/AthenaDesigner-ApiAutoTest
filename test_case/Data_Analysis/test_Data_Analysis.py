#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026-01-20 09:01:21


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


case_id = ['report_GetActivityListByPattern_001', 'report_AddActivityByPattern_001', 'report_GetActivityDetail_001', 'report_GetResidByCode_001', 'button_QueryReportButtons_001', 'customConfig_GetControlList_001', 'task_GetPageViewList_001', 'report_UpsertActivityConfig_001', 'tenant_QueryCustomerTenants_001', 'module_PublishActivity_001', 'operation_GetRecord_001', 'report_DeleteActivityByCode_001', 'statement_CreateDetailTable_001', 'statement_QueryTableList_001', 'statement_GetLangResource_001', 'statement_QueryActionButtons_001', 'statement_GetTableDetail_001', 'statement_GetCustomControls_001', 'statement_GetPageViews_001', 'statement_UpdateTableConfig_001', 'statement_QueryPublishTenants_001', 'statement_PublishDetailTable_001', 'statement_DeleteDetailTable_001', 'tbb_CreateDataAnalysisTable_001', 'tbb_QueryAnalysisTables_001', 'tbb_PublishAnalysisTable_001', 'tbb_DeleteAnalysisTable_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("数据分析")
class TestDataAnalysis:

    @allure.story("报表")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Data_Analysis(self, in_data, case_skip):
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
    pytest.main(['test_test_Data_Analysis.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
