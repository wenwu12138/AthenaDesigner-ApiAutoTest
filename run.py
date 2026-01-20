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
    # 读取命令行传入的测试文件参数（支持指定单个测试文件执行）
    test_file = sys.argv[1] if len(sys.argv) > 1 else None

    # 打印执行模式日志，方便调试
    if test_file:
        INFO.logger.info(f"📄 【指定文件模式】执行测试文件：{test_file}")
    else:
        INFO.logger.info("📄 【全量执行模式】未指定测试文件，执行所有测试用例")


    # 从配置文件中获取项目名称
    try:
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
                                  ┃         一定会顺顺利利，没有BUG的！(*╹▽╹*)     ┃
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

        # 判断现有的测试用例，如果未生成测试代码，则自动生成
        # TestCaseAutomaticGeneration().get_case_automatic()

        # 构建pytest执行参数
        pytest_args = [
            '-s',
            '-W', 'ignore:Module already imported:pytest.PytestWarning',
            '--alluredir', './report/tmp',
            "--clean-alluredir"
        ]

        """
        --reruns: 失败重跑次数
        --count: 重复执行次数
        -v: 显示错误位置以及错误的详细信息
        -s: 等价于 pytest --capture=no 可以捕获print函数的输出
        -q: 简化输出信息
        -m: 运行指定标签的测试用例
        -x: 一旦错误，则停止运行
        --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
        "--reruns=3", "--reruns-delay=2"
        """

        if test_file:
            pytest_args.append(test_file)

        # 执行pytest测试
        pytest.main(pytest_args)


        # 生成allure文件
        os.system(r"allure generate ./report/tmp -o ./report/html --clean")


        # 目前暂时只让云端发报告了 本地就注释掉 放在jenkinsfiles里面
        allure_data = AllureFileClean().get_case_count()
        notification_mapping = {
            NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
            NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
            NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
            NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
        }

        # if config.notification_type != NotificationType.DEFAULT.value:
        #     notify_type = config.notification_type.split(",")
        #     for i in notify_type:
        #         notification_mapping.get(i.lstrip(""))()


        if config.excel_report:
            ErrorCaseExcel().write_case()

        # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
        # os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p 9999")

        #启动本地服务供内网查看报告
        server = ReportServer(report_path=ensure_path_sep("\\report\\html"), port=9999, host='0.0.0.0')
        server.start_server()

    except Exception:
        # 如有异常，相关异常发送邮件z
        e = traceback.format_exc()
        print("==========自动化执行异常=========")
        print(e)
        send_email = SendEmail(AllureFileClean.get_case_count())
        send_email.error_mail(e)
        raise


if __name__ == '__main__':
    run()
