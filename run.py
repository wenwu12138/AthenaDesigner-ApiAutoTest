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


def run():
    test_file = sys.argv[1] if len(sys.argv) > 1 else None
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
                                  ┃         ┃     (｡•̀ᴗ-)✧ 准备就绪！！    ┃          ┃
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

        # ========== 保留原有功能：本地启动报告服务 ==========
        if not is_jenkins:
            server = ReportServer(report_path=ensure_path_sep("\\report\\html"), port=9999, host='0.0.0.0')
            server.start_server()
        else:
            print("✅ Jenkins环境下跳过本地报告服务启动")

        # ========== 保留原有功能：本地发送通知 ==========if not is_jenkins and config.notification_type != NotificationType.DEFAULT.value:
        #         #     allure_data = AllureFileClean().get_case_count()
        #         #     notification_mapping = {
        #         #         NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
        #         #         NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
        #         #         NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
        #         #         NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
        #         #     }
        #         #
        #         #     notify_type = config.notification_type.split(",")
        #         #     for i in notify_type:
        #         #         notify_key = i.lstrip("")
        #         #         if notify_key in notification_mapping:
        #         #             try:
        #         #                 notification_mapping.get(notify_key)()
        #         #             except Exception as e:
        #         #                 print(f"❌ 发送{notify_key}通知失败: {str(e)}")
        # if not is_jenkins and config.notification_type != NotificationType.DEFAULT.value:
        #     allure_data = AllureFileClean().get_case_count()
        #     notification_mapping = {
        #         NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
        #         NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
        #         NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
        #         NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
        #     }
        #
        #     notify_type = config.notification_type.split(",")
        #     for i in notify_type:
        #         notify_key = i.lstrip("")
        #         if notify_key in notification_mapping:
        #             try:
        #                 notification_mapping.get(notify_key)()
        #             except Exception as e:
        #                 print(f"❌ 发送{notify_key}通知失败: {str(e)}")

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