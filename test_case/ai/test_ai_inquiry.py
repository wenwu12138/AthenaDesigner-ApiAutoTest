#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026-04-16 10:48:48


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


case_id = ['knowledge_create_noun_001', 'knowledge_get_list_by_code_001', 'knowledge_get_page_by_keyword_001', 'knowledge_update_noun_001', 'knowledge_get_page_after_update_001', 'knowledge_batch_delete_001', 'knowledge_get_page_after_batch_delete_001', 'knowledge_create_habit_001', 'knowledge_get_habit_page_and_cache_id_001', 'knowledge_delete_by_id_001', 'knowledge_get_page_after_delete_by_id_001', 'dataset_add_001', 'dataset_get_page_list_001', 'dataset_all_datasets_001', 'dataset_update_status_disable_001', 'dataset_update_status_enable_001', 'dataset_query_process_001', 'dataset_delete_001', 'entity_type_get_list_001', 'entity_type_get_page_001', 'word_dictionary_foreign_query_by_page_001', 'word_dictionary_query_by_data_name_001', 'word_dictionary_check_exist_001', 'favourite_query_template_public_001', 'favourite_query_template_grouped_001', 'favourite_query_template_detail_001', 'favourite_query_activity_public_001', 'favourite_query_activity_grouped_001', 'favourite_query_activity_detail_001', 'favourite_query_activity_v2_public_001', 'favourite_get_dtd_list_001', 'favourite_get_dtd_graph_relation_001', 'common_auth_modules_001', 'word_ai_category_save_001', 'word_ai_category_query_001', 'word_ai_feature_save_001', 'word_ai_feature_query_001', 'word_ai_word_save_001', 'word_ai_word_query_001', 'word_ai_observer_save_001', 'word_ai_observer_query_001', 'word_ai_entity_type_insert_001', 'word_ai_entity_type_get_page_001', 'word_ai_entity_type_get_list_001', 'word_ai_synonym_create_001', 'word_ai_synonym_get_list_001', 'word_ai_synonym_check_001', 'word_ai_synonym_delete_001', 'word_ai_entity_type_delete_001', 'word_ai_observer_delete_001', 'word_ai_word_delete_001', 'word_ai_feature_delete_001', 'word_ai_category_delete_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("AI闭环用例")
class TestAiInquiry:

    @allure.story("洞察与知识闭环")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_ai_inquiry(self, in_data, case_skip):
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
    pytest.main(['test_test_ai_inquiry.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
