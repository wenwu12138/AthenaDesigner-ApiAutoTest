#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2026/1/27 11:48  
# @Author: wenwu        
# @Desc:      
# @File: InterfaceCoverage.py       
# @Software: PyCharm

import json
import os
import yaml
# 注意：确保你的 utils 和 common 模块能正常导入
from utils.read_files_tools.get_all_files_path import get_all_files
from common.setting import ensure_path_sep


class InterfaceCoverage:
    """接口覆盖率统计类（适配字典嵌套YAML格式）"""

    def __init__(self, swagger_json_path):
        """
        初始化
        :param swagger_json_path: 本地Swagger JSON契约文件路径
        """
        self.swagger_json_path = swagger_json_path
        self.all_swagger_interfaces = {}  # {完整路径: {methods: [], tags: []}}
        self.covered_interfaces = set()  # {"完整路径:方法", ...}
        self.base_path = ""  # 基础路径（如/athena-designer）
        # 新增：分类统计相关存储
        self.all_interfaces_by_category = {}  # {分类名: [所有接口标识(路径:方法)]}
        self.uncovered_interfaces_by_category = {}  # {分类名: [未覆盖接口标识(路径:方法)]}

    def load_swagger_from_local_json(self):
        """加载本地OpenAPI 3.0.1 JSON文件"""
        try:
            with open(self.swagger_json_path, "r", encoding="utf-8") as f:
                swagger_data = json.load(f)
            print(f"✅ 成功加载本地Swagger JSON文件: {self.swagger_json_path}")
            return swagger_data
        except FileNotFoundError:
            raise Exception(f"本地Swagger JSON文件不存在：{self.swagger_json_path}")
        except json.JSONDecodeError:
            raise Exception(f"本地Swagger JSON文件格式错误：{self.swagger_json_path}")
        except Exception as e:
            raise Exception(f"加载本地Swagger JSON文件失败：{str(e)}")

    def parse_openapi3_interfaces(self):
        """解析OpenAPI 3.0.1接口，标准化路径（解决路径对比不一致问题）"""
        swagger_data = self.load_swagger_from_local_json()

        # 1. 提取并标准化基础路径（去除末尾斜杠，避免拼接错误）
        servers = swagger_data.get("servers", [])
        if servers:
            self.base_path = servers[0].get("url", "").rstrip("/")
        print(f"🔍 接口基础路径: {self.base_path if self.base_path else '无'}")

        # 2. 解析所有接口路径和方法，标准化格式
        paths = swagger_data.get("paths", {})
        for path, methods in paths.items():
            # 过滤监控接口
            if "/actuator" in path:
                continue

            # 标准化接口路径：去除首尾斜杠 + 拼接基础路径
            raw_path = path.strip("/")
            full_path = f"{self.base_path}/{raw_path}" if self.base_path and raw_path else self.base_path
            # 再次标准化（避免重复斜杠）
            full_path = full_path.replace("//", "/").rstrip("/")

            # 提取有效HTTP方法（GET/POST/PUT/DELETE）
            valid_methods = [m.upper() for m in methods.keys()
                             if m.lower() in ["get", "post", "put", "delete", "patch"]]

            if valid_methods:
                self.all_swagger_interfaces[full_path] = {
                    "methods": valid_methods,
                    "tags": methods.get(list(methods.keys())[0], {}).get("tags", [])
                }

                # 新增：解析接口时，按分类整理所有接口（为后续分类统计做准备）
                category = self._extract_interface_category(full_path)
                # 生成该路径下所有接口标识（路径:方法）
                interface_keys = [f"{full_path}:{method}" for method in valid_methods]
                # 更新分类字典
                if category not in self.all_interfaces_by_category:
                    self.all_interfaces_by_category[category] = []
                self.all_interfaces_by_category[category].extend(interface_keys)

        # 统计总接口数
        total_count = sum(len(v["methods"]) for v in self.all_swagger_interfaces.values())
        print(f"✅ 解析出 {len(self.all_swagger_interfaces)} 个接口路径，{total_count} 个接口（路径+方法）")
        return self.all_swagger_interfaces

    def _extract_interface_category(self, full_path):
        """
        辅助方法：从完整接口路径中提取分类名（核心逻辑）
        规则：去除基础路径后，提取二级目录作为分类（如/athena-designer/event/eventSubscribe -> event）
        异常处理：路径格式不规范时，归类为"其他"
        """
        # 1. 去除基础路径（避免基础路径干扰分类提取）
        if self.base_path and full_path.startswith(self.base_path):
            path_without_base = full_path[len(self.base_path):].strip("/")
        else:
            path_without_base = full_path.strip("/")

        # 2. 分割路径，提取二级目录作为分类
        path_segments = path_without_base.split("/")
        if len(path_segments) >= 1:
            # 情况1：路径如 event/eventSubscribe -> 取第一个片段（event）作为分类
            # 情况2：路径如 event -> 直接取该片段作为分类
            return path_segments[0]
        else:
            # 路径格式不规范（空路径等），归类为"其他"
            return "其他"

    def get_covered_interfaces_from_yaml(self):
        """
        核心修复：适配字典嵌套格式的YAML用例
        处理逻辑：跳过case_common，解析用例ID节点下的url和method
        """
        yaml_files = get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True)
        print(f"\n🔍 扫描/data目录，共找到 {len(yaml_files)} 个YAML用例文件")

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    case_data = yaml.safe_load(f) or {}

                # ========== 适配你的YAML核心逻辑 ==========
                # 遍历YAML字典，跳过case_common，解析所有用例ID节点
                for case_id, case_detail in case_data.items():
                    # 跳过公共配置节点
                    if case_id == "case_common":
                        continue
                    # 确保用例详情是字典格式
                    if not isinstance(case_detail, dict):
                        continue

                    # 提取用例中的url和method（你的YAML格式字段名）
                    yaml_url = case_detail.get("url", "").strip()
                    yaml_method = case_detail.get("method", "").strip().upper()

                    # 过滤空值
                    if not yaml_url or not yaml_method:
                        print(f"⚠️ 用例 {case_id}（文件：{yaml_file}）缺少url或method，跳过")
                        continue

                    # ========== 路径标准化（解决对比异常的关键） ==========
                    # 1. 去除url首尾斜杠
                    yaml_url = yaml_url.strip("/")
                    # 2. 拼接基础路径（如果需要）
                    if self.base_path and not yaml_url.startswith(self.base_path.lstrip("/")):
                        full_covered_path = f"{self.base_path}/{yaml_url}".replace("//", "/")
                    else:
                        full_covered_path = f"/{yaml_url}" if not yaml_url.startswith("/") else yaml_url

                    # 3. 生成对比标识（格式："完整路径:方法"）
                    covered_key = f"{full_covered_path}:{yaml_method}"
                    self.covered_interfaces.add(covered_key)
                    # 注释掉高频打印，避免输出冗余（如需调试可开启）
                    # print(f"✅ 识别用例：{case_id} -> {covered_key}")

            except Exception as e:
                print(f"❌ 解析文件 {yaml_file} 失败：{str(e)}")
                continue

        print(f"\n✅ 总计识别到 {len(self.covered_interfaces)} 个已覆盖的接口（路径+方法）")
        return self.covered_interfaces

    def get_uncovered_interfaces(self):
        """获取未覆盖的接口列表，同时按分类整理未覆盖接口"""
        uncovered = []
        for path, info in self.all_swagger_interfaces.items():
            for method in info["methods"]:
                key = f"{path}:{method}"
                if key not in self.covered_interfaces:
                    uncovered.append(key)

                    # 新增：按分类整理未覆盖接口
                    category = self._extract_interface_category(path)
                    if category not in self.uncovered_interfaces_by_category:
                        self.uncovered_interfaces_by_category[category] = []
                    self.uncovered_interfaces_by_category[category].append(key)

        return uncovered

    def _calculate_category_coverage(self):
        """
        辅助方法：计算每个分类的覆盖率统计数据
        返回：{分类名: {total: 总接口数, uncovered: 未覆盖数, category_rate: 分类内未覆盖占比, global_rate: 全局未覆盖占比}}
        """
        category_stats = {}
        total_global_interfaces = sum(len(v) for v in self.all_interfaces_by_category.values())

        for category, all_interfaces in self.all_interfaces_by_category.items():
            # 该分类总接口数
            total_category = len(all_interfaces)
            # 该分类未覆盖接口数（无未覆盖则为0）
            uncovered_category = len(self.uncovered_interfaces_by_category.get(category, []))

            # 计算百分比（避免除零错误）
            category_uncovered_rate = round((uncovered_category / total_category * 100),
                                            2) if total_category > 0 else 0.0
            global_uncovered_rate = round((uncovered_category / total_global_interfaces * 100),
                                          2) if total_global_interfaces > 0 else 0.0

            category_stats[category] = {
                "total": total_category,
                "uncovered": uncovered_category,
                "category_rate": category_uncovered_rate,
                "global_rate": global_uncovered_rate
            }

        return category_stats

    def print_coverage_report(self, result):
        """打印可视化覆盖率报告（新增分类统计展示）"""
        print("\n" + "=" * 80)
        print("📊 接口自动化覆盖率统计报告（适配你的YAML格式 + 分类统计）")
        print("=" * 80)

        # 第一步：打印全局汇总数据
        print("\n【一、全局汇总】")
        print("-" * 40)
        print(f"📈 总接口数（路径+方法）：{result['total_interface_count']}")
        print(f"✅ 已覆盖接口数：{result['covered_count']}")
        print(f"❌ 未覆盖接口数：{result['uncovered_count']}")
        print(f"📊 全局接口覆盖率：{result['coverage_rate']}%")

        # 第二步：打印分类详细统计（核心新增）
        print("\n【二、分类详细统计（未覆盖接口）】")
        print("-" * 80)
        category_stats = self._calculate_category_coverage()

        # 按分类未覆盖数降序排序（更直观）
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]["uncovered"], reverse=True)

        for category, stats in sorted_categories:
            print(f"\n🔖 分类：{category}")
            print(f"   ├─ 分类总接口数：{stats['total']}")
            print(f"   ├─ 分类未覆盖接口数：{stats['uncovered']}")
            print(f"   ├─ 分类内未覆盖占比：{stats['category_rate']}%（{stats['uncovered']}/{stats['total']}）")
            print(
                f"   └─ 全局未覆盖占比：{stats['global_rate']}%（{stats['uncovered']}/{result['total_interface_count']}）")

            # 打印该分类下具体的未覆盖接口列表
            uncovered_interfaces = self.uncovered_interfaces_by_category.get(category, [])
            if uncovered_interfaces:
                print(f"   📋 该分类未覆盖接口详情：")
                for idx, interface in enumerate(uncovered_interfaces, 1):
                    print(f"      {idx}. {interface}")
            else:
                print(f"   🎉 该分类所有接口均已覆盖！")

        # 第三步：打印全局未覆盖接口汇总（保留原有功能，兼容习惯）
        print("\n【三、全局未覆盖接口汇总（完整列表）】")
        print("-" * 80)
        if result["uncovered_interfaces"]:
            for idx, interface in enumerate(result["uncovered_interfaces"], 1):
                print(f"  {idx}. {interface}")
        else:
            print("🎉 所有接口均已覆盖！")

        print("=" * 80)

    def calculate_coverage(self):
        """计算覆盖率，生成统计报告"""
        # 解析Swagger接口（含分类整理所有接口）
        self.parse_openapi3_interfaces()
        # 解析YAML用例覆盖的接口
        self.get_covered_interfaces_from_yaml()

        # 统计核心数据
        total_interface_count = sum(len(v["methods"]) for v in self.all_swagger_interfaces.values())
        covered_count = len(self.covered_interfaces)
        uncovered_interfaces = self.get_uncovered_interfaces()  # 同时整理分类未覆盖接口
        coverage_rate = round((covered_count / total_interface_count * 100), 2) if total_interface_count > 0 else 0

        # 生成统计结果
        result = {
            "total_interface_count": total_interface_count,
            "covered_count": covered_count,
            "uncovered_count": len(uncovered_interfaces),
            "coverage_rate": coverage_rate,
            "uncovered_interfaces": uncovered_interfaces
        }

        # 打印可视化报告
        self.print_coverage_report(result)
        return result

    def save_coverage_report(self, result, report_path=None):
        """保存覆盖率报告到文件"""
        if not report_path:
            report_path = ensure_path_sep("\\report\\interface_coverage_report.json")

        report_dir = os.path.dirname(report_path)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        # 新增：将分类统计数据加入保存结果（可选，增强报告完整性）
        category_stats = self._calculate_category_coverage()
        result_with_category = {
            **result,
            "category_stats": category_stats,
            "uncovered_interfaces_by_category": self.uncovered_interfaces_by_category
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(result_with_category, f, ensure_ascii=False, indent=2)

        print(f"\n📄 覆盖率报告已保存至：{report_path}")


# ---------------------- 用法示例 ----------------------
if __name__ == "__main__":
    # 替换为你的本地Swagger JSON文件路径
    swagger_json_path = ensure_path_sep("\\data\\ServerApi.json")

    # 初始化并计算覆盖率
    coverage = InterfaceCoverage(swagger_json_path)
    coverage_result = coverage.calculate_coverage()

    # 保存报告（可选，已包含分类统计数据）
    coverage.save_coverage_report(coverage_result)