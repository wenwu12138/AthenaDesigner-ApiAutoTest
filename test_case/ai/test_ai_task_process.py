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


case_id = ['task_application_list_001', 'task_project_list_001', 'task_page_view_tree_001', 'task_task_tree_001', 'process_find_field_by_model_001', 'process_find_model_info_001', 'monitor_rule_get_all_products_001', 'monitor_rule_get_tree_001', 'page_design_query_by_application_001', 'page_design_query_by_code_001', 'page_design_query_data_sources_by_code_001', 'page_design_get_action_id_by_code_001', 'page_design_assign_name_check_001', 'page_design_esp_product_001', 'project_find_app_effect_adp_version_001', 'project_canvas_not_upgrade_exists_001', 'project_project_list_001', 'project_projects_simple_001', 'project_projects_by_execute_type_001', 'project_query_project_list_v2_001', 'project_get_project_detail_001', 'project_project_tree_001', 'process_find_process_count_by_trigger_type_001', 'process_find_process_pagination_001', 'process_find_process_by_id_001', 'project_get_solve_simple_projects_001', 'project_get_root_projects_001', 'process_find_approvals_button_by_condition_id_001', 'process_find_process_list_page_001', 'process_query_waiting_nodes_001', 'resource_tree_query_list_of_source_001', 'resource_tree_query_model_list_001', 'task_process_seed_project_001', 'task_process_seed_project_detail_001', 'process_version_query_list_001', 'task_get_task_list_001', 'tenant_task_get_task_list_001', 'task_get_data_list_001', 'tenant_task_get_data_list_001', 'task_get_dtd_canvas_001', 'tenant_task_get_dtd_canvas_001', 'task_get_task_detail_001', 'tenant_task_get_task_detail_001', 'task_get_task_and_data_state_001', 'task_get_dtd_canvas_tasks_001', 'task_get_data_list_by_code_001', 'task_get_main_line_001', 'group_history_get_data_group_history_001', 'group_history_query_list_001', 'task_get_task_by_codes_001', 'task_query_assist_task_flow_info_001', 'task_get_task_and_data_state_by_skill_code_001', 'pagedesign_ai_biz_add_001', 'pagedesign_ai_query_model_001', 'pagedesign_ai_generate_query_plan_001', 'pagedesign_ai_query_data_view_001', 'pagedesign_ai_generate_page_001', 'pagedesign_ai_query_by_code_001', 'pagedesign_ai_update_001', 'pagedesign_ai_query_by_code_after_update_001', 'pagedesign_ai_delete_001', 'pagedesign_ai_biz_delete_001', 'task_process_project_update_main_line_tasks_001', 'task_process_project_get_solve_simple_001', 'task_process_project_can_skip_config_001', 'task_process_tenant_get_process_in_combination_001', 'task_process_tenant_find_process_pagination_001', 'task_process_pagedesign_permission_by_code_001', 'task_process_pagedesign_form_publish_status_001', 'task_process_pagedesign_form_list_001', 'task_process_pagedesign_query_fields_001', 'task_process_pagedesign_query_fields_by_table_name_001', 'task_process_pagedesign_lcdp_data_entry_001', 'task_process_pagedesign_get_page_design_by_model_001', 'task_process_pagedesign_get_standards_permissions_001', 'task_process_mobile_page_query_by_workbench_code_001', 'task_process_mobile_page_query_by_code_001', 'task_process_mechanism_service_domains_001', 'task_process_mechanism_task_page_struct_001', 'task_process_mechanism_task_data_struct_001', 'task_process_mechanism_resolve_plan_001', 'task_process_mechanism_project_page_struct_001', 'task_process_mechanism_get_detail_001', 'task_process_mechanism_output_template_001', 'task_process_mechanism_group_and_items_001', 'task_process_mechanism_group_data_001', 'task_process_mechanism_data_struct_001', 'task_process_mechanism_all_data_description_001', 'task_process_data_description_and_state_001', 'task_process_data_find_decision_by_application_001', 'task_process_data_dd_and_ds_tree_001', 'task_process_data_tree_001', 'task_process_build_data_get_page_design_code_001', 'subpage_ai_add_first_001', 'subpage_ai_add_second_001', 'subpage_ai_query_list_001', 'subpage_ai_query_detail_001', 'subpage_ai_update_name_001', 'subpage_ai_update_001', 'subpage_ai_batch_update_001', 'subpage_ai_batch_sync_001', 'subpage_ai_delete_001', 'openwindow_ai_save_001', 'openwindow_ai_query_by_application_001', 'openwindow_ai_query_detail_001', 'openwindow_ai_update_001', 'openwindow_ai_delete_001', 'pagedesign_model_ai_query_fields_001', 'pagedesign_model_ai_query_fields_group_001', 'pagedesign_model_ai_query_fields_by_code_001', 'pagedesign_model_ai_query_fields_by_data_type_001', 'pagedesign_model_ai_query_fields_group_list_001', 'pagedesign_model_ai_generate_api_config_001', 'page_design_ext_query_by_page_001', 'page_design_ext_query_by_model_001', 'page_design_ext_query_navigate_model_001', 'page_design_ext_switch_to_low_code_001', 'page_design_ext_part_dsl_save_001', 'page_design_ext_generate_default_dsl_001', 'page_design_third_party_get_code_001', 'page_design_ext_get_action_id_by_code_001', 'page_design_third_party_get_auth_001', 'page_design_third_party_add_or_update_auth_001', 'page_design_third_party_delete_auth_001', 'page_design_third_party_delete_001', 'task_page_designer_task_definition_001', 'task_page_designer_redis_value_001', 'task_page_designer_metadata_001', 'task_page_designer_tag_001', 'task_page_designer_redis_data_001', 'task_page_designer_process_001', 'page_view_design_query_by_task_code_001', 'page_view_design_query_by_project_code_001', 'page_view_design_data_entry_task_page_view_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("AI闭环用例")
class TestAiTaskProcess:

    @allure.story("任务与流程闭环")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_ai_task_process(self, in_data, case_skip):
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
    pytest.main(['test_test_ai_task_process.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
