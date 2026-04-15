#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2026-04-15 11:10:46


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


case_id = ['activity_configs_get_by_code_001', 'activity_configs_get_basic_info_001', 'activity_configs_get_list_by_application_001', 'activity_config_seed_list_001', 'activity_config_get_config_by_code_001', 'activity_config_get_data_entry_by_application_001', 'activity_config_get_data_entry_user_table_name_001', 'activity_config_get_sign_metadata_001', 'activity_config_get_custom_id_001', 'activity_config_validate_exist_001', 'activity_config_post_get_activity_list_001', 'activity_config_get_activity_list_by_pattern_001', 'activity_types_001', 'activity_query_configs_by_page_001', 'activity_check_res_id_used_001', 'activity_query_favourite_public_001', 'aim_scene_query_channels_001', 'aim_event_query_platform_list_001', 'aim_event_query_platform_and_app_001', 'aim_scene_query_all_open_001', 'aim_scene_insert_for_event_closure_001', 'aim_event_query_all_scene_by_event_id_001', 'aim_scene_query_event_body_explain_001', 'aim_scene_detail_for_event_closure_001', 'aim_scene_delete_for_event_closure_001', 'activity_process_seed_list_001', 'activity_process_get_by_code_001', 'activity_get_abi_inner_token_001', 'activity_get_tbb_inner_token_001', 'message_notification_query_all_001', 'message_notification_query_by_user_001', 'message_notification_query_valid_001', 'message_notification_query_topic_001', 'upgrade_notification_query_history_001', 'upgrade_notification_query_all_001', 'upgrade_notification_query_valid_001', 'aim_event_detail_001', 'aim_event_query_list_001', 'aim_scene_query_by_condition_001', 'message_notification_query_product_news_001', 'aim_scene_application_query_by_condition_001', 'aim_scene_platform_query_by_condition_001', 'backendmanage_is_manager_001', 'backendmanage_query_application_data_list_by_page_001', 'backendmanage_query_application_data_list_total_001', 'backendmanage_all_tenant_application_data_list_by_page_001', 'backendmanage_all_tenant_application_data_list_total_001', 'backendmanage_query_application_data_num_001', 'backendmanage_all_tenant_application_data_num_001', 'backendmanage_query_application_num_by_type_001', 'backendmanage_all_tenant_application_num_by_type_001', 'backendmanage_query_data_card_001', 'backendmanage_query_all_data_card_001', 'backendmanage_query_data_card2_001', 'backendmanage_all_tenant_data_card2_001', 'backendmanage_query_date_driven_line_001', 'backendmanage_all_date_driven_line_001', 'backendmanage_query_application_by_page_001', 'backendmanage_query_application_total_001', 'backendmanage_query_model_by_page_001', 'backendmanage_query_model_total_001', 'backendmanage_query_work_by_page_001', 'backendmanage_query_work_total_001', 'backendmanage_query_action_by_page_001', 'backendmanage_query_action_total_001', 'backendmanage_query_detection_by_page_001', 'backendmanage_query_detection_total_001', 'backendmanage_query_scheme_by_page_001', 'backendmanage_query_scheme_total_001', 'backendmanage_query_user_by_page_001', 'backendmanage_query_user_total_001', 'backendmanage_query_process_by_page_001', 'backendmanage_query_process_total_001', 'backendmanage_query_task_by_page_001', 'backendmanage_query_task_total_001', 'backendmanage_query_hooks_by_page_001', 'backendmanage_query_hooks_total_001', 'activity_message_visible_config_query_by_application_001', 'activity_visible_config_query_avc_by_code_001', 'activity_configs_query_full_by_code_001', 'activity_configs_recovery_tbb_report_001', 'activity_configs_query_config_by_code_path_001', 'action_query_esp_action_fields_in_model_001', 'action_esp_sync_progress_001', 'action_esp_sync_meta_data_001', 'assistant_query_scene_list_001', 'assistant_query_home_page_001', 'assistant_scene_query_all_001', 'assistant_skill_template_auth_001', 'abi_query_sys_data_001', 'abi_query_data_view_param_fields_001', 'abi_query_action_data_view_fields_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("AI闭环用例")
class TestAiActivityMessage:

    @allure.story("活动与消息闭环")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_ai_activity_message(self, in_data, case_skip):
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
    pytest.main(['test_test_ai_activity_message.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
