#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 15:01
# @Author: 闻武
import json
import os
import shutil
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pytest
from utils.other_tools.models import NotificationType
from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.logging_tool.log_control import INFO
from utils.notify.wechat_send import WeChatSend
from utils.notify.ding_talk import DingTalkSendMsg
from utils.notify.send_mail import SendEmail
from utils.notify.lark import FeiShuTalkChatBot
from utils.other_tools.allure_data.error_case_excel import ErrorCaseExcel
from utils import config
from utils.other_tools.ReportServer import ReportServer
from common.setting import ensure_path_sep

# 执行模式默认值:
# 本地直接运行 DEFAULT_PARALLEL_MODE = False-> 串行   DEFAULT_PARALLEL_MODE = True 并行
# 参数运行 `python run.py --parallel` -> 并行
# 参数运行 `python run.py --serial` -> 串行
DEFAULT_PARALLEL_MODE = True


def parse_run_args():
    """保留原有单文件参数形式，新增 --parallel 开关。"""
    # 用法:
    # 本地直接运行: python run.py
    # 指定并行: python run.py --parallel
    # 指定串行: python run.py --serial
    # 指定目标并行: python run.py test_case/ai --parallel
    args = sys.argv[1:]
    parallel = DEFAULT_PARALLEL_MODE
    target = None

    for arg in args:
        if arg == '--parallel':
            parallel = True
        elif arg == '--serial':
            parallel = False
        elif target is None:
            target = arg
        else:
            raise ValueError(f"不支持的多余参数: {arg}")

    return target, parallel


def collect_parallel_test_files(target):
    """按文件粒度收集 test_xxx.py。"""
    project_root = Path(os.getcwd())

    if target:
        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = (project_root / target_path).resolve()
    else:
        target_path = project_root / "test_case"

    if target_path.is_file():
        return [target_path]

    return sorted(target_path.rglob("test_*.py"))


def build_parallel_result_dir(test_file):
    """每个测试文件独立写 allure 结果目录。"""
    project_root = Path(os.getcwd())
    relative_path = test_file.relative_to(project_root).with_suffix("")
    safe_name = "_".join(relative_path.parts)
    return project_root / "report" / "allure-results-parallel" / safe_name


def merge_parallel_allure_results():
    """并行执行后的 allure 结果合并回 report/allure-results。"""
    parallel_root = Path("./report/allure-results-parallel")
    final_root = Path("./report/allure-results")

    if final_root.exists():
        shutil.rmtree(final_root)
    final_root.mkdir(parents=True, exist_ok=True)

    if not parallel_root.exists():
        return

    for result_dir in sorted(parallel_root.iterdir()):
        if not result_dir.is_dir():
            continue
        for result_file in result_dir.iterdir():
            if not result_file.is_file():
                continue
            # Allure 结果文件会通过原始文件名互相引用，重命名后附件链接会失效。
            # 这里直接保留原始文件名合并；Allure 默认使用 UUID 命名，冲突概率极低。
            target_file = final_root / result_file.name
            shutil.copy2(result_file, target_file)


def run_pytest_for_single_file(test_file):
    """并行模式下单文件 pytest 执行。"""
    result_dir = build_parallel_result_dir(test_file)
    result_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-s",
        "-W", "ignore:Module already imported:pytest.PytestWarning",
        "--alluredir", str(result_dir),
        "--clean-alluredir",
        str(test_file)
    ]

    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{os.getcwd()}{os.pathsep}{current_pythonpath}"
        if current_pythonpath else os.getcwd()
    )

    INFO.logger.info(f"[并行模式] 开始执行测试文件: {test_file}")
    completed = subprocess.run(cmd, cwd=os.getcwd(), env=env)
    INFO.logger.info(f"[并行模式] 测试文件执行完成: {test_file} -> exit_code={completed.returncode}")
    return completed.returncode


def run_pytest_in_parallel(test_file=None):
    """按 test_xxx.py 文件粒度并行执行。"""
    test_files = collect_parallel_test_files(test_file)
    if not test_files:
        raise FileNotFoundError("未找到可执行的测试文件")

    parallel_root = Path("./report/allure-results-parallel")
    if parallel_root.exists():
        shutil.rmtree(parallel_root)
    parallel_root.mkdir(parents=True, exist_ok=True)

    worker_count = min(len(test_files), max(1, os.cpu_count() or 1))
    INFO.logger.info(f"[并行模式] 共收集到 {len(test_files)} 个测试文件，worker={worker_count}")

    exit_codes = []
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map = {
            executor.submit(run_pytest_for_single_file, test_path): test_path
            for test_path in test_files
        }
        for future in as_completed(future_map):
            test_path = future_map[future]
            exit_codes.append((test_path, future.result()))

    merge_parallel_allure_results()

    failed_files = [str(path) for path, code in exit_codes if code != 0]
    if failed_files:
        INFO.logger.error(f"[并行模式] 存在失败测试文件: {failed_files}")
        return 1
    return 0


def run():
    test_file, parallel_mode = parse_run_args()
    is_jenkins = os.getenv('JENKINS_URL', False)

    if test_file:
        INFO.logger.info(f"📄 【指定文件模式】执行测试文件：{test_file}")
        # 保留文件存在性检查
        if not os.path.exists(test_file):
            print(f"❌ 错误：路径 {test_file} 不存在！")
            print(f"📌 当前工作目录：{os.getcwd()}")
            print(f"📌 可用文件/目录：{os.listdir('.')}")
            sys.exit(1)
    else:
        INFO.logger.info("📄 【全量模式】执行所有测试文件")

    try:
        # 保留原有日志打印逻辑
        INFO.logger.info(
            """
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃             (◍●ᴗ●◍)  ʚ♡ɞ  (◍●ᴗ●◍)            ┃
                                  ┃                                            ┃
                                  ┃         ╭━━━━━━━━━━━━━━━━━━━━━━━━━╮          ┃
                                  ┃         ┃                         ┃          ┃
                                  ┃         ┃     (｡•̀ᴗ-)✧ 准备就绪！    ┃          ┃
                                  ┃         ┃                         ┃          ┃
                                  ┃         ╰━━━━━━━━━━━━━━━━━━━━━━━━━╯          ┃
                                  ┃                                            ┃
                                  ┃        ｡◕‿◕｡  ｡◕‿◕｡  ｡◕‿◕｡  ｡◕‿◕｡         ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃             「{}」项目启动啦！                ┃
                                  ┃                                            ┃
                                  ┃         ʕ•̀ω•́ʔ✧  冲鸭冲鸭～ 加油加油～  ʕ•̀ω•́ʔ✧      ┃
                                  ┃                                            ┃
                                  ┃         一定会顺顺利利，没有BUG的!！(*╹▽╹*)     ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃        (✧∇✧)  (✧∇✧)  (✧∇✧)  (✧∇✧)         ┃
                                  ┃                                            ┃
                                  ┃        ╭───╮  ╭───╮  ╭───╮  ╭───╮          ┃
                                  ┃        │♡♡│  │♡♡│  │♡♡│  │♡♡│          ┃
                                  ┃        ╰───╯  ╰───╯  ╰───╯  ╰───╯          ┃
                                  ┃                                            ┃
                                  ┃        (✧∇✧)  (✧∇✧)  (✧∇✧)  (✧∇✧)         ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃             启动流程开始～ (๑＞ڡ＜)☆            ┃
                                  ┃                                            ┃
                                  ┃         ʚ(◜𖥦◝ )ɞ  祝一切顺利哦～  ʚ(◜𖥦◝ )ɞ        ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                """.format(config.project_name)
        )

        # 保留原有pytest参数构建逻辑
        pytest_args = [
            '-s',
            '-W', 'ignore:Module already imported:pytest.PytestWarning',
            '--alluredir', './report/allure-results',
            "--clean-alluredir",
        ]


        if test_file:
            pytest_args.append(test_file)

        # 保留原有执行日志
        print(f"开始执行测试 执行命令为: pytest {' '.join(pytest_args)}")
        INFO.logger.info(f"[执行方式] {'并行' if parallel_mode else '串行'}")
        if parallel_mode:
            print("开始执行测试，执行模式为: pytest 按 test_xxx.py 文件粒度并行")
            exit_code = run_pytest_in_parallel(test_file)
        else:
            exit_code = pytest.main(pytest_args)

        # 1. 统一生成HTML报告到 report/html（删除环境判断）
        print("📊 生成Allure HTML报告到 report/html...")
        os.system(r"allure generate ./report/allure-results -o ./report/html --clean")

        # 2. Jenkins环境额外动作：复制原始结果到allure-results（供插件使用）
        if is_jenkins:
            os.makedirs("allure-results", exist_ok=True)
            for file in os.listdir("./report/allure-results"):
                src = os.path.join("./report/allure-results", file)
                dst = os.path.join("allure-results", file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
            print(f"✅ 已将Allure原始结果复制到 allure-results 目录")

        # ========== 保留原有功能：生成错误用例Excel ==========
        if config.excel_report:
            ErrorCaseExcel().write_case()

        # ========== 保留原有功能：本地发送通知 ==========
        if not is_jenkins and config.notification_type != NotificationType.DEFAULT.value:
            allure_data = AllureFileClean().get_case_count()
            notification_mapping = {
                NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
                NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
                NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
                NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
            }

            notify_type = config.notification_type.split(",")
            for i in notify_type:
                notify_key = i.lstrip("")
                if notify_key in notification_mapping:
                    try:
                        notification_mapping.get(notify_key)()
                    except Exception as e:
                        print(f"❌ 发送{notify_key}通知失败: {str(e)}")

        # ========== 保留原有功能：本地启动报告服务 ==========
        if not is_jenkins:
            server = ReportServer(report_path=ensure_path_sep("\\report\\html"), port=9999, host='0.0.0.0')
            server.start_server()
        else:
            print("✅ Jenkins环境下跳过本地报告服务启动")


        # 保留原有退出逻辑
        sys.exit(exit_code)

    except Exception:
        # 保留原有异常处理逻辑
        e = traceback.format_exc()
        print("==========自动化执行异常=========")
        print(e)
        send_email = SendEmail(AllureFileClean.get_case_count())
        send_email.error_mail(e)
        raise


if __name__ == '__main__':
    run()
