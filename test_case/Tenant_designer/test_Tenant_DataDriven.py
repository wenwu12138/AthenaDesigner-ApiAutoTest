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


case_id = ['project_FindAppEffectAdpVersion_004', 'tenant_projectAddProjectData_001', 'tenant_codeGenerateDataOrgProjectCode_001', 'tenant_projectSaveProject_001', 'tenant_codeGenerateTrackableProjectCode_001', 'tenant_projectSaveTrackableProject_001', 'tenant_codeGenerateSubProjectCode_001', 'tenant_projectSaveSubProject_001', 'tenant_processUpsertSingleProject_001', 'tenant_basis_Compile_002', 'tenant_basis_PublishTest_002', 'tenant_basis_PublishHuaweiProd_002', 'tenant_basisPublishAzureProd_002', 'tenant_basis_QueryTenantPipeline_local001', 'tenant_basis_PublishTest_local001', 'tenant_project_QueryCombinationProjectList_001', 'add_AddTenantSingleDtd_001', 'tenant_project_QuerySinglePageTriggerProjectList_001', 'publish_PublishTenantProcessModule_001', 'tenant_WithdrawTenantSingleDtd_001', 'tenant_AddTenantDtd_001', 'tenant_QueryCombinationProject_001', 'tenant_PublishCombinationProject_001', 'tenant_WithdrawTenantDtd_001', 'tenant_RemoveTenantDtd_001', 'tenant_RemoveTenantSingleDtd_001', 'tenant_projectDeleteProjectData_001', 'tenant_projectDeleteSubProject_001', 'tenant_projectDeleteParentProject_001', 'tenant_projectDeleteTrackableProject_001', 'tenant_process_RemoveProcess_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("租户设计器")
class TestTenantDatadriven:

    @allure.story("租户级项目任务")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Tenant_DataDriven(self, in_data, case_skip):
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
    pytest.main(['test_test_Tenant_DataDriven.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
