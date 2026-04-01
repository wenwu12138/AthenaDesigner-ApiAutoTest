#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/30 14:12
# @Author : 闻武
import pytest
import time
import allure
import requests
import ast
import os
import re
from pathlib import Path
from common.setting import ensure_path_sep
from utils.requests_tool.request_control import cache_regular
from utils.logging_tool.log_control import INFO, ERROR, WARNING
from utils.other_tools.models import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no
from utils.cache_process.cache_control import CacheHandler
from datetime import datetime
import json
from utils.read_files_tools.regular_control import regular
from utils import config

import pytest
from utils.logging_tool.log_control import INFO

# 全局变量存储进度信息
_test_progress = {'total': 0, 'current': 0}


# 橙色（使用亮黄色93）
ORANGE = '\033[93m'
RESET = '\033[0m'


def _find_local_cached_token():
    """优先从环境变量或本地历史执行产物中复用 token。"""
    env_token = os.getenv("ATHENA_FIXED_TOKEN")
    if env_token:
        return env_token.strip()

    report_dir = Path(ensure_path_sep("\\report\\allure-results"))
    if not report_dir.exists():
        return None

    patterns = [
        re.compile(r"'token': '([^']+)'"),
        re.compile(r'"token": "([^"]+)"')
    ]

    candidates = sorted(
        report_dir.glob("*attachment*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
    return None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """每个测试用例执行后打印进度"""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":  # 只统计测试执行阶段
        try:
            # 如果是第一个用例，获取总数
            if _test_progress['total'] == 0:
                _test_progress['total'] = len(item.session.items) if hasattr(item.session, 'items') else 1

            _test_progress['current'] += 1

            # 获取测试名称（简化显示）
            test_name = item.name if hasattr(item, 'name') else str(item)
            # 去掉参数化生成的冗余信息
            if '[' in test_name and ']' in test_name:
                test_name = test_name.split('[')[0]

            # 计算进度百分比
            current = _test_progress['current']
            total = _test_progress['total']
            progress = (current / total * 100) if total > 0 else 0

            # 简洁的进度显示
            INFO.logger.info(f"{ORANGE}📊 [{current}/{total}] ({progress:.1f}%) - {test_name}")

        except Exception:
            # 简化异常处理，不打印任何错误信息
            pass


@pytest.fixture(scope="session", autouse=False)
def clear_report():
    """如clean命名无法删除报告，这里手动删除"""
    del_file(ensure_path_sep("\\report"))


@pytest.fixture(scope="session", autouse=True)
def work_login_init():
    """
    获取登录的cookie
    :return:
    """

    url = "https://www.wanandroid.com/user/login"
    data = {
        "username": "wenwu",
        "password": 123456
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # 请求登录接口

    try:
        res = requests.post(url=url, data=data, verify=True, headers=headers, timeout=10)
        response_cookie = res.cookies
    except Exception as exc:
        WARNING.logger.warning(f"澶栭儴绀轰緥绔欑偣鐧诲綍澶辫触锛屽凡璺宠繃cookie鍒濆鍖? {exc}")
        CacheHandler.update_cache(cache_name='login_cookie', value='')
        return

    cookies = ''
    for k, v in response_cookie.items():
        _cookie = k + "=" + v + ";"
        # 拿到登录的cookie内容，cookie拿到的是字典类型，转换成对应的格式
        cookies += _cookie
        # 将登录接口中的cookie写入缓存中，其中login_cookie是缓存名称
    CacheHandler.update_cache(cache_name='login_cookie', value=cookies)

@pytest.fixture(scope="session", autouse=True)
def get_iam_token():
    """"
    调用iam接口获取token
    """
    url = "${{iam_host()}}/api/iam/v2/identity/login"

    data = {
    "userId": "wenwu@digiwin.com",
    "passwordHash": "IqYqscxpotURKHJGFrHI9w==",
    "clientEncryptPublicKey": "LV2MM445KGBAQbVxR7g14o8UZhvwQqeSJ3udnyfV3+JDraXkkYgregD9Gk10lmW3WaG55tShF2fEDBjfFDkeu2NgLfWuoYZwaBjZd5+yTCofvt3sb7gL+0IwXNx+jFvYdgFy/rKSPdDGHOEyLppTRyLtJHNCJFvIWYhqWQnteaTcnRiJDxLc+58w2FdWU7G+VG8QdgrKOHNRH3mFsQ2Oy6bqNjXuV0AldDMSI+kDTdRglglKftR7KFgd0ZNH8DKIR7J77/EmdRdfgTMaPNiLdiOFXK/mfYf8WnuXW2YlgkmQt5iiqv4RX4EUWPCT6HmSWWWG8k34Hx3aTZHSMgIClQ==",
    "excludeNonVisible": True,
    "tenantId":config.tenantId
}
    headers = {
        "Content-Type": "application/json",
        "digi-middleware-auth-app":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzczMjY2ODk0NjEsInNpZCI6NDA3MTI4ODI1NTM0NDY0MSwiaWQiOiJEaWdpd2luQ2xvdWQifQ.XGPl3brNeNTCivWN_bIYj8TfcxqlkQ0sFV2woPOr0TY"

    }

    #     #  双虎地端环境
    #     data = {
    #     "userId": "default",
    #     "passwordHash": "skv1PcefW8T6aX43rdbkhg==",
    #     "clientEncryptPublicKey": "a/j/W/AIcXb7nWL0pDAZ27h28IiZHa8A5R2cP+WbYNE9bFZwv330c5VX/cFj23Lg1xk0bECInHxQk0gSD8NWdIFRz9SVZUWjGfhDOkmK83yhThuzYTK4wtJlcX36RemJGXldAhtE2b2tgPGoBbT+DXFMJVUjbPmqo16Lgzwi82zi1jLTkkGt+m39M+bU3sFf/deUWwNZiYyMt1oxXvH4MRgdGCJGEqnjdz3xiiWJvAQTLDHW3ox9opbJ2hUQZMZ7SH2M6XAFOWXDCFmwWRA34jAr8d4oSGN2onfJHe7smquTl5yaHQ4Niwquo5kRMruJ3wu2NSZNSD41Ney1BC/hXw==",
    #     "excludeNonVisible": True
    # }
    #     headers = {
    #    'digi-middleware-auth-app': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzczMjY2ODk0NjEsInNpZCI6NDA3MTI4ODI1NTM0NDY0MSwiaWQiOiJEaWdpd2luQ2xvdWQifQ.XGPl3brNeNTCivWN_bIYj8TfcxqlkQ0sFV2woPOr0TY',
    #    'digi-middleware-device-id': 'bYdVWJHMnxMl/wj0DPeFlkpHNWO12g/RNg9oc+CtSxRkdmQUJVyFvAp5lBcJB8ytn5SeAhsp+YDfZk50ohrJU/Rw/AcHjlIoqE2wRByylk8=',
    #    'Content-Type': 'application/json'
    # }



    # 正式区就要用lcdp这个租户验证  只有这个租户能发微软正式
    # if '正式' in config.env:
    #     data['tenantId'] = 'lcdp'
    url = regular(str(url))
    token = None
    try:
        res = requests.post(url=url, json=data, headers=headers, verify=False, timeout=15)
        response_data = res.json()
        token = response_data.get("token")
    except Exception as exc:
        WARNING.logger.warning(f"IAM登录失败，准备回退本地token: {exc}")

    if not token:
        token = _find_local_cached_token()
        if token:
            WARNING.logger.warning("IAM不可达，已回退使用本地历史token")

    if not token:
        pytest.fail(
            "IAM登录失败，且未找到可复用的本地token。"
            "请检查当前网络/防火墙，或设置环境变量 ATHENA_FIXED_TOKEN。"
        )

    CacheHandler.update_cache(cache_name='token', value=token)



## 需要前置生成的测试数据
@pytest.fixture(scope="session", autouse=True)
def pretest_data():
    testdata = {
        "TestApp_code": "${{random_id()}}AT",
        "Data_Code": "${{random_hexcode()}}",
        "Project_Data_Code": "${{random_hexcode()}}",
        "LimitTestApp_code": "${{random_id()}}AT"
    }
    for k, v in testdata.items():
        k = regular(str(k))
        v = regular(str(v))
        testdata[k] = v
        # print(testdata)
        CacheHandler.update_cache(cache_name=k, value=v)
        # print(CacheHandler.get_cache(k))




def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

    # 期望用例顺序
    # print("收集到的测试用例:%s" % items)
    appoint_items = ["test_get_user_info", "test_collect_addtool", "test_Cart_List", "test_ADD", "test_Guest_ADD",
                     "test_Clear_Cart_Item"]

    # 指定运行顺序
    run_items = []
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)

    for i in run_items:
        run_index = run_items.index(i)
        items_index = items.index(i)

        if run_index != items_index:
            n_data = items[run_index]
            run_index = items.index(n_data)
            items[items_index], items[run_index] = items[run_index], items[items_index]


def pytest_configure(config):
    config.addinivalue_line("markers", 'smoke')
    config.addinivalue_line("markers", '回归测试')


@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    in_data = TestCase(**in_data)
    if isinstance(in_data.is_run, str):
        in_data.is_run = eval(in_data.is_run)
    #目前is_run有两种形式,如果是string 就当表达式执行一下
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"请求URL: {in_data.is_run}")
        allure_step_no(f"请求方式: {in_data.method}")
        allure_step("请求头: ", in_data.headers)
        allure_step("请求数据: ", in_data.data)
        allure_step("依赖数据: ", in_data.dependence_case_data)
        allure_step("预期数据: ", in_data.assert_data)
        pytest.skip()

def pytest_sessionstart(session):
    """测试会话开始时记录时间"""
    global _session_start_time
    _session_start_time = time.time()
    print(f"测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时记录时间"""
    global _session_start_time
    if _session_start_time:
        duration = time.time() - _session_start_time
        print(f"测试结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")


def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """
    session_start = terminalreporter._sessionstarttime
    session_start_timestamp = time.mktime(session_start.timetuple()) if isinstance(session_start, datetime) else 0
    #计算使用时间
    global _session_start_time

    if _session_start_time:
        duration = time.time() - _session_start_time
    else:
        duration = 0


    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - session_start_timestamp     # 不太对啊 先放着 不报错~
    INFO.logger.error(f"用例总数: {_TOTAL}")
    INFO.logger.error(f"异常用例数: {_ERROR}")
    ERROR.logger.error(f"失败用例数: {_FAILED}")
    WARNING.logger.warning(f"跳过用例数: {_SKIPPED}")
    INFO.logger.info(f"测试总时长: {duration:.2f}秒")

    try:
        _RATE = _PASSED / _TOTAL * 100
        INFO.logger.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        INFO.logger.info("用例成功率: 0.00 %")






