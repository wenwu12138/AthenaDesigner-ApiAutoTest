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


case_id = ['background_is_manager_001', 'background_query_application_by_page_001', 'background_query_application_total_001', 'background_query_model_by_page_001', 'background_query_model_total_001', 'background_query_data_card_001', 'background_query_date_driven_line_001', 'background_query_work_by_page_001', 'background_query_work_total_001', 'background_query_action_by_page_001', 'background_query_action_total_001', 'background_query_detection_by_page_001', 'background_query_detection_total_001', 'background_query_scheme_by_page_001', 'background_query_scheme_total_001', 'background_query_user_by_page_001', 'background_query_user_total_001', 'background_query_process_by_page_001', 'background_query_process_total_001', 'background_query_task_by_page_001', 'background_query_task_total_001', 'background_query_hooks_by_page_001', 'background_query_hooks_total_001', 'background_query_application_data_list_by_page_001', 'background_query_application_data_list_total_001', 'background_query_application_data_num_001', 'background_query_application_num_by_type_001', 'background_query_data_card2_001', 'background_query_all_data_card_001', 'background_all_tenant_application_data_list_by_page_001', 'background_all_tenant_application_data_list_total_001', 'background_all_tenant_application_data_num_001', 'background_all_tenant_application_num_by_type_001', 'background_all_tenant_data_card2_001', 'background_all_date_driven_line_001', 'base_info_business_type_list_001', 'base_info_business_type_get_one_001', 'base_info_product_list_001', 'classification_get_list_001', 'business_type_get_list_001', 'data_standard_business_type_query_by_page_001', 'dictionary_query_system_infos_001', 'dictionary_query_legacy_all_001', 'dictionary_query_legacy_by_key_001', 'dictionary_query_v2_all_001', 'dictionary_query_v2_by_enum_key_001', 'dictionary_query_v2_info_by_enum_key_001', 'dictionary_simple_legacy_001', 'dictionary_simple_v2_001', 'dictionary_get_dict_by_key_001', 'dictionary_v2_get_dict_by_key_001', 'button_select_001', 'dmc_query_token_001', 'file_get_dmc_token_001', 'duty_get_all_001', 'duty_get_one_001', 'eoc_get_department_list_001', 'button_init_001', 'button_init_project_001', 'button_query_project_init_data_001', 'button_query_manually_init_data_001', 'button_query_buttons_by_key_project_001', 'button_query_buttons_by_key_manual_001', 'preset_data_get_connection_objects_001', 'preset_data_get_project_field_init_001', 'preset_data_get_manually_init_button_001', 'preset_data_get_batch_objects_001', 'tag_public_actions_001', 'tag_task_action_001', 'tag_built_in_attrs_001', 'healthcheck_001', 'tag_definition_all_001', 'tag_definition_get_001', 'action_find_action_labels_001', 'action_find_actions_001', 'action_find_actions_no_paging_001', 'action_find_actions_by_fields_001', 'action_find_actions_by_fields_v2_001', 'action_find_actions_v2_001', 'action_find_actions_no_paging_v2_001', 'action_query_esp_action_request_fields_001', 'action_get_action_metadata_001', 'action_find_action_by_action_id_001', 'action_get_action_base_info_001', 'action_query_esp_action_fields_001', 'model_driver_server_source_query_001', 'model_driver_server_source_get_service_code_list_001', 'model_driver_server_source_get_backend_info_001', 'model_driver_server_source_validate_registry_001', 'model_driver_server_source_get_custom_backend_info_list_001', 'model_driver_server_source_get_save_service_log_001', 'model_driver_server_source_get_save_service_status_001', 'action_get_api_provider_001', 'esp_action_query_request_fields_001', 'esp_action_query_response_fields_001', 'agiledata_business_type_create_001', 'agiledata_business_type_page_001', 'agiledata_business_type_get_list_001', 'agiledata_business_type_delete_001', 'agiledata_classification_create_001', 'agiledata_classification_page_001', 'agiledata_classification_get_list_001', 'agiledata_classification_delete_001', 'agiledata_standard_params_create_or_update_001', 'agiledata_standard_params_query_by_page_001', 'agiledata_standard_params_query_001', 'agiledata_standard_params_get_standard_params_001', 'agiledata_standard_params_delete_001', 'agiledata_standard_params_save_or_update_mapping_001', 'agiledata_standard_params_query_mapping_001', 'agiledata_standard_params_delete_mapping_001', 'agiledata_instruction_add_group_001', 'agiledata_instruction_query_by_page_001', 'agiledata_instruction_get_detail_001', 'agiledata_instruction_repeat_check_001', 'agiledata_instruction_delete_group_001', 'agiledata_instruction_edit_001', 'agiledata_instruction_update_sort_001', 'agiledata_section_config_add_001', 'agiledata_section_config_page_001', 'agiledata_section_config_detail_001', 'agiledata_section_config_edit_001', 'agiledata_section_config_get_all_001', 'agiledata_section_config_copy_001', 'agiledata_section_config_delete_copy_001', 'agiledata_section_config_delete_origin_001', 'agiledata_business_variables_insert_001', 'agiledata_business_variables_get_page_001', 'agiledata_business_variables_get_list_001', 'agiledata_business_variables_update_001', 'agiledata_business_variables_add_sys_variables_001', 'agiledata_business_variables_delete_001', 'agiledata_board_info_insert_001', 'agiledata_board_info_get_page_001', 'agiledata_board_info_update_001', 'agiledata_board_info_copy_001', 'agiledata_board_info_get_page_copy_001', 'agiledata_board_info_delete_copy_001', 'agiledata_board_info_delete_origin_001', 'agiledata_node_template_insert_001', 'agiledata_node_template_page_001', 'agiledata_node_template_find_list_001', 'agiledata_node_template_update_001', 'agiledata_node_template_delete_001', 'agiledata_target_create_001', 'agiledata_target_page_001', 'agiledata_target_dict_001', 'agiledata_target_delete_001', 'agiledata_operate_query_by_user_001', 'agiledata_operate_update_001', 'agiledata_ai_log_day_on_day_001', 'agiledata_ai_log_day_count_001', 'agiledata_ai_log_user_count_001', 'agiledata_application_get_model_list_001', 'agiledata_ai_dataflow_permission_001', 'agiledata_auto_switch_page_list_001', 'agiledata_auto_switch_lasted_version_001', 'tag_private_seed_project_001', 'tag_private_seed_project_detail_001', 'tag_private_seed_task_list_001', 'tag_public_ai_create_001', 'tag_public_ai_query_by_condition_001', 'tag_public_ai_query_public_all_001', 'tag_public_ai_bind_save_001', 'tag_public_ai_bind_get_001', 'tag_category_query_001', 'tag_private_relation_save_001', 'tag_private_relation_get_001', 'tag_private_action_sync_001', 'tag_private_ai_create_001', 'tag_private_query_001', 'tag_private_query_page_001', 'tag_private_bind_save_001', 'tag_private_bind_get_001', 'tag_private_bind_ext_info_001', 'tag_query_open_window_action_001', 'tag_private_action_delete_001', 'tag_public_ai_bind_clear_001', 'tag_private_ai_delete_001', 'tag_public_ai_delete_001', 'tag_definition_ai_create_001', 'tag_definition_ai_get_001', 'tag_definition_ai_delete_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("AI闭环用例")
class TestAiBaseSupport:

    @allure.story("基础支撑闭环")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_ai_base_support(self, in_data, case_skip):
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
    pytest.main(['test_test_ai_base_support.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
