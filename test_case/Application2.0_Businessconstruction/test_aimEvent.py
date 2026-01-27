#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026-01-27 10:01:43


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


case_id = ['aimEvent_QueryList_001', 'aimEvent_QueryPlatformList_001', 'aimEvent_CreateEvent_001', 'aimEvent_GetDetail_001', 'aimScene_QueryByCondition_001', 'aimEvent_EditEvent_001', 'aimEvent_GetDetail_002', 'aimEvent_DeleteEvent_001', 'aimScene_QueryPlatformByCondition_001', 'aimScene_QueryApplicationByCondition_001', 'aimScene_CreateScene_001', 'aimScene_QueryApplicationByCondition_002', 'aimScene_GetDetail_001', 'aimScene_QueryChannels_001', 'eoc_GetUserList_001', 'eoc_GetDutyList_001', 'aimEvent_QueryPlatformAndAppEvents_001', 'aimScene_UpdateScene_001', 'aimScene_DeleteScene_001', 'aimScene_QueryApplicationByCondition_003']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("业务搭建")
class TestAimevent:

    @allure.story("消息管理")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_aimEvent(self, in_data, case_skip):
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
    pytest.main(['test_test_aimEvent.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
