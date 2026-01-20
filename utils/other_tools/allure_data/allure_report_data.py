#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 15:44
# @Author : 闻武
描述: 收集 allure 报告
"""

import json
import os  # 新增：路径判断
from typing import List, Text
from common.setting import ensure_path_sep
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.other_tools.models import TestMetrics


class AllureFileClean:
    """allure 报告数据清洗，提取业务需要得数据"""

    @classmethod
    def get_testcases(cls) -> List:
        """ 获取所有 allure 报告中执行用例的情况"""
        files = []
        # 新增：捕获目录不存在异常，不影响原有功能
        try:
            for i in get_all_files(ensure_path_sep("\\report\\html\\data\\test-cases")):
                with open(i, 'r', encoding='utf-8') as file:
                    date = json.load(file)
                    files.append(date)
        except FileNotFoundError:
            print("⚠️ 未找到test-cases目录，返回空列表")
        return files

    def get_failed_case(self) -> List:
        """ 获取到所有失败的用例标题和用例代码路径"""
        error_case = []
        for i in self.get_testcases():
            # 用get()避免key不存在，保留原有功能
            if i.get('status') in ['failed', 'broken']:
                error_case.append((i.get('name', '未知用例'), i.get('fullName', '未知路径')))
        return error_case

    def get_failed_cases_detail(self) -> Text:
        """ 返回所有失败的测试用例相关内容 """
        # 完全保留原有逻辑
        date = self.get_failed_case()
        values = ""
        if len(date) >= 1:
            values = "失败用例:\n"
            values += "        **********************************\n"
            for i in date:
                values += "        " + i[0] + ":" + i[1] + "\n"
        return values

    @classmethod
    def get_case_count(cls) -> "TestMetrics":
        """ 统计用例数量 """
        file_name = ensure_path_sep("\\report\\html\\widgets\\summary.json")

        # 新增：文件不存在时返回默认数据，不抛错
        if not os.path.exists(file_name):
            print(f"⚠️ 未找到{file_name}，返回默认数据")
            return TestMetrics(
                passed=0, failed=0, broken=0, skipped=0, total=0,
                pass_rate=0.0, time=0.0
            )

        try:
            # 完全保留原有统计逻辑
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
            _case_count = data['statistic']
            _time = data['time']
            keep_keys = {"passed", "failed", "broken", "skipped", "total"}
            run_case_data = {k: v for k, v in data['statistic'].items() if k in keep_keys}

            if _case_count["total"] > 0:
                run_case_data["pass_rate"] = round(
                    (_case_count["passed"] + _case_count["skipped"]) / _case_count["total"] * 100, 2
                )
            else:
                run_case_data["pass_rate"] = 0.0

            run_case_data['time'] = _time if run_case_data['total'] == 0 else round(_time['duration'] / 1000, 2)
            return TestMetrics(**run_case_data)
        except Exception as exc:
            print(f"⚠️ 读取报告失败: {str(exc)}")
            return TestMetrics(
                passed=0, failed=0, broken=0, skipped=0, total=0,
                pass_rate=0.0, time=0.0
            )


if __name__ == '__main__':
    AllureFileClean().get_case_count()