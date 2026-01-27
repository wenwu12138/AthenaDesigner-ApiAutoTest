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


case_id = ['project_FindAppEffectAdpVersion_001', 'project_AddProjectData_001', 'project_CanvasNotUpgradeExists_001', 'project_QueryProjectList_001', 'project_QueryCombinationProjectList_001', 'project_QuerySinglePageTriggerProjectList_001', 'project_GetDataList_001', 'code_GenerateDataOrgProjectCode_001', 'project_SaveProject_001', 'code_GenerateTrackableProjectCode_001', 'project_SaveTrackableProject_001', 'groupHistory_GetDataGroupHistory_001', 'project_GetProject_001', 'guide_IsSkip_002', 'task_GetTaskList_001', 'task_GetDataList_001', 'project_ProjectTree_001', 'task_GetDtdCanvas_001', 'data_DataGroupListByApplication_001', 'data_FindDataStatesByApplication_001', 'task_GetTaskListByState_001', 'code_GenerateSubProjectCode_001', 'project_SaveSubProject_001', 'task_GetTaskListByDataState_001', 'project_DeleteProjectData_001', 'project_DeleteSubProject_001', 'project_DeleteParentProject_001', 'project_DeleteTrackableProject_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("驱动执行")
class TestProject:

    @allure.story("项目")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Project(self, in_data, case_skip):
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
    pytest.main(['test_test_Project.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
