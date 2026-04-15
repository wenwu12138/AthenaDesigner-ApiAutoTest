#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
发送飞书通知
"""

import datetime
import json
import logging
import os
from typing import List

import requests
import urllib3

from utils import config
from utils.other_tools.ReportServer import ReportServer
from utils.other_tools.allure_data.allure_report_data import TestMetrics

urllib3.disable_warnings()


def is_not_null_and_blank_str(content: str) -> bool:
    """判断字符串非空且非纯空白。"""
    return bool(content and content.strip())


class FeiShuTalkChatBot:
    """飞书机器人通知。"""

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

    @staticmethod
    def _get_report_url() -> str:
        """优先使用外部传入的报告地址，其次回退到本地报告服务地址。"""
        report_url = os.getenv("REPORT_URL")
        if is_not_null_and_blank_str(report_url):
            return report_url.strip()
        host = ReportServer.get_local_ip()
        if not is_not_null_and_blank_str(host) or "无法获取" in host:
            host = "localhost"
        return f"http://{host}:9999"

    @staticmethod
    def _get_notify_flag() -> str:
        return f"【{config.project_name}接口自动化通知】"

    def _build_rows(self) -> List[List[dict]]:
        report_url = self._get_report_url()
        now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = "通过" if self.metrics.failed == 0 and self.metrics.broken == 0 else "存在失败"

        rows = [
            [
                {
                    "tag": "text",
                    "text": f"{self._get_notify_flag()} {summary}"
                }
            ],
            [
                {"tag": "text", "text": "测试环境："},
                {"tag": "text", "text": str(config.env)}
            ],
            [
                {"tag": "text", "text": "测试负责人："},
                {"tag": "text", "text": str(config.tester_name)}
            ],
            [
                {"tag": "text", "text": "执行结果："},
                {"tag": "text", "text": f"成功率 {self.metrics.pass_rate}%"}
            ],
            [
                {"tag": "text", "text": "用例总数："},
                {"tag": "text", "text": str(self.metrics.total)}
            ],
            [
                {"tag": "text", "text": "成功用例："},
                {"tag": "text", "text": str(self.metrics.passed)}
            ],
            [
                {"tag": "text", "text": "失败用例："},
                {"tag": "text", "text": str(self.metrics.failed)}
            ],
            [
                {"tag": "text", "text": "异常用例："},
                {"tag": "text", "text": str(self.metrics.broken)}
            ],
            [
                {"tag": "text", "text": "跳过用例："},
                {"tag": "text", "text": str(self.metrics.skipped)}
            ],
            [
                {"tag": "text", "text": "执行时长："},
                {"tag": "text", "text": f"{self.metrics.time} s"}
            ],
            [
                {"tag": "text", "text": "通知时间："},
                {"tag": "text", "text": now_date}
            ],
            [
                {"tag": "text", "text": "测试报告："},
                {"tag": "a", "text": "点击查看报告", "href": report_url}
            ],
        ]

        image_key = os.getenv("LARK_IMAGE_KEY", "").strip()
        if image_key:
            rows.append([{"tag": "img", "image_key": image_key}])

        return rows

    def _build_post_payload(self) -> dict:
        return {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": self._get_notify_flag(),
                        "content": self._build_rows()
                    }
                }
            }
        }

    def send_text(self, msg: str):
        """发送文本消息。"""
        if not is_not_null_and_blank_str(msg):
            raise ValueError("text 类型消息内容不能为空")

        payload = {"msg_type": "text", "content": {"text": msg}}
        return self._request(payload)

    def _request(self, payload: dict) -> dict:
        response = requests.post(
            config.lark.webhook,
            headers=self.headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            verify=False,
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("code", 0) != 0:
            error_msg = result.get("msg", "未知异常")
            logging.error("飞书通知发送失败: %s", error_msg)
            raise ValueError(f"飞书通知发送失败: {error_msg}")

        return result

    def post(self):
        """发送飞书富文本通知。"""
        return self._request(self._build_post_payload())
