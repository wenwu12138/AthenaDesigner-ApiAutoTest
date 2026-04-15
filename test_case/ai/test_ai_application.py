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


case_id = ['application_all_001', 'application_all_solution_plan_template_001', 'application_all_solution_plan_template_app_type_001', 'application_auth_app_info_001', 'application_exist_001', 'application_app_home_page_001', 'application_tenant_query_applications_001', 'application_query_workbench_001', 'workbench_app_get_001', 'workbench_app_custom_setting_001', 'workbench_component_menu_query_001', 'workbench_component_page_query_001', 'workbench_datasource_count_job_apps_001', 'application_query_by_codes_001', 'application_query_experience_over_time_001', 'application_query_hooks_001', 'application_query_resource_summary_001', 'application_query_solution_cards_001', 'application_query_solution_designer_001', 'application_query_recent_visit_001', 'application_query_recent_create_001', 'application_query_latest_compile_info_001', 'application_get_auths_applications_001', 'application_query_compile_log_001', 'application_query_compile_log_page_001', 'application_get_by_gitlab_001', 'application_verify_solution_permission_001', 'application_query_compile_data_001', 'application_query_compile_data_4_agile_001', 'application_param_query_base_001', 'application_param_exist_app_001', 'application_param_exist_mechanism_001', 'custom_config_query_sys_list_001', 'custom_config_query_sys_share_001', 'custom_config_query_sys_detail_001', 'custom_config_query_ref_app_info_001', 'custom_config_check_is_related_001', 'custom_config_query_app_list_001', 'custom_config_query_app_share_001', 'guide_skip_set_false_prepare_001', 'guide_is_skip_false_001', 'guide_skip_set_true_001', 'guide_is_skip_true_001', 'guide_skip_set_false_restore_001', 'guide_is_skip_false_restore_001', 'individual_case_query_env_param_001', 'individual_case_query_all_use_tenant_infos_001', 'individual_case_query_tenants_by_area_001', 'individual_case_query_app_status_001', 'individual_case_query_app_log_001', 'individual_case_individual_all_jobs_001', 'individual_case_business_info_001', 'user_get_me_001', 'user_get_tenant_team_id_001', 'user_query_expiration_reminder_001', 'application_query_navigation_bar_001', 'application_access_record_001', 'application_query_compile_detail_001', 'application_get_example_app_001', 'application_get_page_by_get_001', 'application_get_page_by_post_001', 'application_query_application_detail_001', 'application_all_in_tenant_001', 'application_query_solution_authorize_timeout_reminder_001', 'custom_config_query_components_001', 'custom_config_get_control_list_001', 'application_query_by_env_publish_001', 'application_app_compile_data_001', 'application_param_get_config_001', 'application_param_get_all_001', 'application_param_get_table_config_001', 'application_param_get_by_codes_001', 'application_param_get_by_code_001', 'application_param_ai_save_001', 'application_param_ai_get_by_codes_001', 'application_param_ai_get_by_code_001', 'application_param_ai_delete_001', 'custom_config_check_tenant_exists_001', 'activity_visible_config_query_by_application_001', 'individual_case_auth_001', 'individual_case_bak_business_info_001', 'individual_case_source_business_info_001', 'app_init_get_redis_id_by_app_code_001', 'app_init_get_process_by_uuid_001', 'individual_case_all_jobs_branch_001', 'individual_case_get_standard_projects_info_001', 'custom_config_get_control_type_related_info_001', 'custom_config_get_sys_control_type_related_info_001', 'custom_config_query_relate_activity_button_001', 'workbench_app_custom_setting_save_001', 'workbench_app_custom_setting_after_save_001', 'workbench_app_custom_setting_delete_001', 'workbench_datasource_query_app_list_001', 'workbench_datasource_query_app_job_list_001', 'workbench_datasource_page_query_app_job_list_001', 'workbench_datasource_page_query_001', 'workbench_component_query_components_001', 'workbench_datasource_count_query_config_list_001', 'workbench_datasource_save_001', 'workbench_datasource_delete_001', 'workbench_component_page_query_v2_001', 'workbench_component_detail_001', 'workbench_component_save_001', 'workbench_component_batch_delete_001', 'workbench_portal_get_detail_001', 'workbench_portal_published_001', 'workbench_portal_as_draft_001', 'workbench_portal_confirm_draft_001', 'workbench_portal_copy_001', 'workbench_portal_batch_delete_001', 'workbench_common_update_published_001', 'workbench_add_001', 'workbench_query_by_application_001', 'workbench_portal_save_001', 'workbench_sso_valid_app_code_001', 'workbench_sso_save_001', 'workbench_sso_query_all_001', 'workbench_sso_detail_001', 'workbench_sso_delete_001', 'workbench_portal_page_query_001', 'workbench_portal_valid_menu_name_001', 'workbench_portal_related_app_work_list_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("AI闭环用例")
class TestAiApplication:

    @allure.story("应用与用户闭环")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_ai_application(self, in_data, case_skip):
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
    pytest.main(['test_test_ai_application.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
