import json
import requests
from utils.logging_tool.log_control import INFO, ERROR
import time
from utils.read_files_tools.regular_control import regular
from utils.read_files_tools.get_yaml_data_analysis import GetTestCase
from utils.requests_tool.request_control import RequestControl
import ast



class AsynchronousAssert:
    def __init__(self, in_data, in_data_res):
        self.in_data = in_data
        self.in_data_res = in_data_res


    def deployer_assert(self):
        # 轮询查询发版进度
        result = True
        if "addDeployPlan" in self.in_data["url"]:
            try:
                i = 0
                while i < 100:
                 # 查询发版进度
                    # 组装查询数据
                    deployprocess_indata = GetTestCase.case_data(['query_DeployProcess_001'])
                    #根据实际请求的发版/切板数据组装
                    deployprocess_indata[0]['data']['application'] = self.in_data['data']['applicationDataList'][0]['application']
                    deployprocess_indata[0]['data']['deployNo'] = json.loads(self.in_data_res.response_data)['data']
                    deployprocess_indata[0]['detail'] = self.in_data['detail'] + '~~发版进度查询'
                    deployprocess_indata[0]['is_run'] = True   # 只有进行异步断言的时候才要执行查询

                    # 缓存替换后转字典才能进入请求入参接口
                    deployprocess_indata = regular(str(deployprocess_indata))
                    deployprocess_indata = eval(deployprocess_indata)[0]  # 字符串执行转列表

                    # 查询发版进度
                    deployprocess_res =  RequestControl(deployprocess_indata).http_request()


                 # 查询发版详情
                 # 组装查询数据
                    deploydetail_indata = GetTestCase.case_data(['query_DeployDetail_001'])
                    # 根据实际请求的发版/切板数据组装
                    deploydetail_indata[0]['data']['application'] = self.in_data['data']['applicationDataList'][0]['application']
                    deploydetail_indata[0]['data']['deployNo'] = json.loads(self.in_data_res.response_data)['data']
                    deploydetail_indata[0]['detail'] = self.in_data['detail'] + '~~发版详情查询'
                    deploydetail_indata[0]['is_run'] = True   # 只有进行异步断言的时候才要执行查询

                    # 缓存替换后转字典才能进入请求入参接口
                    deploydetail_indata = regular(str(deploydetail_indata))
                    deploydetail_indata = eval(deploydetail_indata)[0]  # 字符串执行转列表

                    # 查询进度详情
                    deploydetail_res = RequestControl(deploydetail_indata).http_request()

                    if json.loads(deployprocess_res.response_data)["data"] == 1 or any("finish" in obj["result"] for obj in json.loads(deploydetail_res.response_data)['data']):
                        result = True
                        INFO.logger.info("\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                         "发版成功\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                        return result
                    elif json.loads(deployprocess_res.response_data)["data"] == -1 or json.loads(deploydetail_res.response_data)["data"][-1]["result"] == "fail":
                        result = False
                        INFO.logger.info("\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                         "发版失败\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                        return result
                    else:
                        i += 1
                        # 查询发版详情并打印
                        # INFO.logger.info(f"进行第{i}次查询操作，目前的进度为{json.loads(query_res.text)["data"]}")

                    # 等待三秒后执行下一次查询
                        time.sleep(15)
            except Exception as e:
                INFO.logger.error(f"循环中发生异常: {str(e)}", exc_info=True)  # 打印完整堆
        elif "addSwitchPlan" in self.in_data["url"]:
            try:
                result = False
                i = 0
                while i < 100:
                    # 查询切板进度（使用指定的query_SwitchProcess_001）
                    # 组装查询数据
                    switchprocess_indata = GetTestCase.case_data(['query_SwitchProcess_001'])
                    # 根据实际请求的切板数据组装
                    switchprocess_indata[0]['data']['application'] = self.in_data['data']['applicationDataList'][0]['application']
                    # 切板的deployNo从响应数据的data.id获取
                    switchprocess_indata[0]['data']['deployNo'] = json.loads(self.in_data_res.response_data)['data']['id']
                    switchprocess_indata[0]['detail'] = self.in_data['detail'] + '~~切板进度查询'
                    switchprocess_indata[0]['is_run'] = True   # 只有进行异步断言的时候才要执行查询

                    # 缓存替换后转字典才能进入请求入参接口
                    switchprocess_indata = regular(str(switchprocess_indata))
                    switchprocess_indata = eval(switchprocess_indata)[0]  # 字符串执行转列表

                    # 查询切板进度
                    switchprocess_res = RequestControl(switchprocess_indata).http_request()

                    # 查询切板详情（使用与发版相同的详情查询ID）
                    # 组装查询数据
                    switchdetail_indata = GetTestCase.case_data(['query_DeployDetail_001'])
                    # 根据实际请求的切板数据组装
                    switchdetail_indata[0]['data']['application'] = self.in_data['data']['applicationDataList'][0]['application']
                    switchdetail_indata[0]['data']['deployNo'] = json.loads(self.in_data_res.response_data)['data']['id']
                    switchdetail_indata[0]['detail'] = self.in_data['detail'] + '~~切板详情查询'
                    switchdetail_indata[0]['is_run'] = True   # 只有进行异步断言的时候才要执行查询

                    # 缓存替换后转字典才能进入请求入参接口
                    switchdetail_indata = regular(str(switchdetail_indata))
                    switchdetail_indata = eval(switchdetail_indata)[0]  # 字符串执行转列表

                    # 查询切板详情
                    switchdetail_res = RequestControl(switchdetail_indata).http_request()

                    # 断言切板进度不为失败状态


                    # 切板成功条件判断
                    if json.loads(switchprocess_res.response_data)["data"] == 1 or any("finish" in obj["result"] for obj in json.loads(switchdetail_res.response_data)['data']):
                        result = True
                        INFO.logger.info("\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                         "切板成功\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                        return result
                        break
                    elif json.loads(switchprocess_res.response_data)["data"] == -1 or json.loads(switchdetail_res.response_data)["data"][-1]["result"] == "fail":
                        result = False
                        INFO.logger.info("\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                         "切板失败\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                        return result
                        break
                    else:
                        i += 1
                        # 等待三秒后执行下一次查询
                        time.sleep(15)
            except Exception as e:
                INFO.logger.error(f"切板循环中发生异常: {str(e)}", exc_info=True)  # 打印完整堆栈
        elif "createNewBranch" in self.in_data["url"]:
            try:
                result = False
                i = 0
                while i < 100:
                    # 分支异步断言
                    # 拿到实际用例数据
                    getBranchInfo_indata = GetTestCase.case_data(['query_BranchInfo_001'])

                    # 组装请求参数
                    getBranchInfo_indata = regular(str(getBranchInfo_indata))

                    # 缓存替换后转字典才能进入请求入参接口
                    getBranchInfo_indata = regular(str(getBranchInfo_indata))
                    getBranchInfo_indata = eval(getBranchInfo_indata)[0]  # 字符串执行转列表

                    # 查询分支创建进度
                    getBranchInfo_res = RequestControl(getBranchInfo_indata).http_request()

                    # 断言切板进度不为失败状态
                    for b in json.loads(getBranchInfo_res.response_data)["data"]:
                        if b.get('status') == '创建失败':
                            result = False
                            INFO.logger.info("\n"
                                             "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                             "分支创建失败\n"
                                             "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                            return result

                    # 分支创建成功条件判断
                    if all(i.get("status") in ('已创建', None) for i in json.loads(getBranchInfo_res.response_data)["data"]):
                        result = True
                        INFO.logger.info("\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                         "分支创建成功\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                        return result
                    else:
                        i += 1
                        # 等待三秒后执行下一次查询
                        time.sleep(15)
            except Exception as e:
                INFO.logger.error(f"分支创建循环中发生异常: {str(e)}", exc_info=True)  # 打印完整堆栈
        elif "/application/delete/v2/" in self.in_data["url"]:  # 新增删除应用处理
            try:
                result = False
                i = 0
                while i < 100:
                    # 查询删除应用进度（使用指定的query_DeleteProcess_001用例）
                    deleteprocess_indata = GetTestCase.case_data(['basis_QueryDeleteProgress_001'])

                    # 组装查询参数（从删除接口响应中获取应用标识）
                    deleteprocess_indata[0]['data']['applicationCode'] = self.in_data['url'].split('/')[-1]
                    deleteprocess_indata[0]['data']['deleteNo'] = json.loads(self.in_data_res.response_data)['data']
                    deleteprocess_indata[0]['is_run'] = True

                    # 缓存替换与格式转换
                    deleteprocess_indata = regular(str(deleteprocess_indata))
                    deleteprocess_indata = eval(deleteprocess_indata)[0]

                    # 执行查询请求
                    deleteprocess_res = RequestControl(deleteprocess_indata).http_request()

                    # 查询删除详情
                    deletedetail_indata = GetTestCase.case_data(['basis_QueryDeleteLog_001'])
                    deletedetail_indata[0]['data']['applicationCode'] = self.in_data['url'].split('/')[-1]
                    deletedetail_indata[0]['data']['deleteNo'] = json.loads(self.in_data_res.response_data)['data']
                    deletedetail_indata[0]['is_run'] = True

                    # 缓存替换与格式转换
                    deletedetail_indata = regular(str(deletedetail_indata))
                    deletedetail_indata = eval(deletedetail_indata)[0]

                    # 执行详情查询
                    deletedetail_res = RequestControl(deletedetail_indata).http_request()



                    # 判断删除成功条件（进度为1或详情包含完成标识）
                    if json.loads(deleteprocess_res.response_data).get("data") == 1 or any(
                            "finish" in obj["result"] for obj in json.loads(deletedetail_res.response_data)['data']):
                        result = True
                        INFO.logger.info("\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                         "删除应用成功\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                        return result
                    elif json.loads(deleteprocess_res.response_data).get("data") == "-1":
                        result = False
                        INFO.logger.info("\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                         "删除应用失败\n"
                                         "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                        return result
                    else:
                        i += 1
                        time.sleep(15)  # 间隔15秒轮询一次
            except Exception as e:
                INFO.logger.error(f"删除应用循环中发生异常: {str(e)}", exc_info=True)
        return result






"""
        处理异步接口断言
        判断用例是否为发版切板用例
        如果是的话循环调用查询接口，设定超时次数为100次 100次以内没满足条件抛异常
"""
# 发版异步断言

"""
记录修改 查询 进度的参数 适配多环境运行  时  是否会影响 发版 切板用例中本身查询动作

结论： 不会  

这里说一下依赖的运行逻辑是写在request方法里面的 如果判断存在依赖 就调用依赖相关方案  执行依赖运行 设定依赖缓存 


在异步断言的时候 要区分和单独执行用例区别  异步断言 不需要依赖数据  因为他依赖的本身就是当前发版动作的编号
"""