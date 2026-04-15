# backendmanage接口用例文档

更新时间：2026-04-10

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 `backendmanage` 相关 Controller 源码整理，用于作为后续生成自动化 YAML 的中间设计文档。

`backendmanage` 的特点和其他业务模块不同，它不是典型 CRUD 模块，而是：

1. 后台运营统计查询
2. 各类报表或 Excel 导出

因此本模块的闭环设计不应强求“新增 -> 更新 -> 删除”，而应按“同口径统计闭环”和“导出专项闭环”来组织。

当前建议归属：

- 业务域：建议新增或并入 `ai_activity_message.yaml` / 新独立文件
- 文档来源：Controller 方法签名 + 后台统计语义

本次重点分析的后端入口包括：

- `com.digiwin.athena.backendmanage.controller.BackgroundTestController`
- `com.digiwin.athena.backendmanage.controller.ApplicationTestController`
- `com.digiwin.athena.backendmanage.controller.PageDesignTestController`
- `com.digiwin.athena.backendmanage.controller.PageViewTestController`
- `com.digiwin.athena.backendmanage.controller.UserTestController`

## 2. 模块结论

### 2.1 适合一次性作为后台管理大模块推进

`backendmanage` 很适合一次性补文档，因为它的结构非常整齐：

1. 一组后台统计查询接口
2. 一组导出接口

同一统计维度通常同时存在：

- `ByPage`
- `Total`
- `Num`
- `Card`
- `Line`

这意味着它非常适合按“统计口径闭环”来生成用例，而不是零散逐个接口生成。

### 2.2 当前最适合优先落地的闭环

优先建议按以下 4 条链路组织：

1. 管理员与应用统计闭环
2. 应用/模型/工作项后台分页统计闭环
3. 用户/流程/任务/Hook 后台分页统计闭环
4. 导出接口专项闭环

### 2.3 当前模块的核心约束

- 大多数接口是只读查询，不存在环境恢复问题
- 部分接口依赖管理员权限或后台可见数据范围
- 导出接口返回文件流，断言规则与普通 JSON 接口不同

## 3. 推荐业务闭环

### 3.1 主闭环 A：管理员与应用统计闭环

闭环目标：确认当前身份具备后台访问能力，并围绕应用统计形成列表、总数、卡片、类型分布的一组查询闭环。

推荐顺序：

1. `GET /backgroundManagement/isManager`
2. `GET /backgroundManagement/queryApplicationDataListByPage`
3. `GET /backgroundManagement/queryApplicationDataListTotal`
4. `GET /backgroundManagement/queryApplicationDataNum`
5. `GET /backgroundManagement/queryApplicationNumByType`
6. `GET /backgroundManagement/queryDataCard`
7. `GET /backgroundManagement/queryDataCard2`

关键规则：

- `isManager` 是整组后台接口的入口探针
- `ByPage` 和 `Total` 构成同口径闭环，不要求数量完全强相等，但要求都可正常返回
- `Num`、`NumByType`、`Card` 更适合作为补充统计节点

建议断言：

- `$.code == 0`
- 列表接口返回对象非空
- 统计对象非空

### 3.2 主闭环 B：全租户视角统计闭环

闭环目标：与主闭环 A 对应，补全全租户口径的应用统计查询。

推荐顺序：

1. `GET /backgroundManagement/allTenantApplicationDataListByPage`
2. `GET /backgroundManagement/allTenantApplicationDataListTotal`
3. `GET /backgroundManagement/allTenantApplicationDataNum`
4. `GET /backgroundManagement/allTenantApplicationNumByType`
5. `GET /backgroundManagement/allTenantDataCard2`
6. `GET /backgroundManagement/queryAllDataCard`

说明：

- 这条链不依赖主闭环 A 的缓存，但语义上是同口径的全租户对照链
- 可以和主闭环 A 同时落入一个模块文件中

### 3.3 主闭环 C：后台对象分页统计闭环

闭环目标：围绕后台对象维度形成分页与总数成对查询闭环。

推荐顺序：

1. `GET /backgroundManagement/queryApplicationByPage`
2. `GET /backgroundManagement/queryApplicationTotal`
3. `GET /backgroundManagement/queryModelByPage`
4. `GET /backgroundManagement/queryModelTotal`
5. `GET /backgroundManagement/queryWorkByPage`
6. `GET /backgroundManagement/queryWorkTotal`
7. `GET /backgroundManagement/queryActionByPage`
8. `GET /backgroundManagement/queryActionTotal`
9. `GET /backgroundManagement/queryDetectionByPage`
10. `GET /backgroundManagement/queryDetectionTotal`
11. `GET /backgroundManagement/querySchemeByPage`
12. `GET /backgroundManagement/querySchemeTotal`

关键规则：

- 每一对 `ByPage + Total` 都构成一个天然小闭环
- 可以统一使用相同筛选参数，比如 `name/tenantName`
- 不建议做“分页第一条数据必须满足某个固定业务字段”的强断言

建议断言：

- `$.code == 0`
- 列表对象存在
- 总数对象存在

### 3.4 主闭环 D：后台用户/流程/任务/Hook 统计闭环

闭环目标：补齐后台管理视角下的人员和流程类统计。

推荐顺序：

1. `GET /backgroundManagement/queryUserByPage`
2. `GET /backgroundManagement/queryUserTotal`
3. `GET /backgroundManagement/queryProcessByPage`
4. `GET /backgroundManagement/queryProcessTotal`
5. `GET /backgroundManagement/queryTaskByPage`
6. `GET /backgroundManagement/queryTaskTotal`
7. `GET /backgroundManagement/queryHooksByPage`
8. `GET /backgroundManagement/queryHooksTotal`

说明：

- 这类接口很适合做成统一模板化 YAML
- 重点是提高“唯一接口覆盖率”，不必在首批里追求复杂业务断言

### 3.5 专项闭环 E：时间趋势统计闭环

闭环目标：校验日期驱动统计曲线接口，同时验证正向日期范围。

推荐顺序：

1. `GET /backgroundManagement/queryDateDrivenLine`
2. `GET /backgroundManagement/AllDateDrivenLine`

关键规则：

- `startTime <= endTime` 是控制层显式校验规则
- 首批建议只做正向场景，不做负向日期失败用例

建议断言：

- `$.code == 0`
- 结果对象存在

### 3.6 导出专项 F：后台 Excel 导出接口闭环

闭环目标：覆盖后台导出能力，而不是 JSON 业务语义。

推荐顺序：

1. `GET /applicationTest6/exportApp`
2. `GET /pageDesignTest6/export`
3. `GET /pageDesignTest6/exportWithMonth`
4. `GET /pageViewTest6/export`
5. `GET /userTest6/exportUser`

建议断言：

- HTTP 状态码 `200`
- `content-type` 为文件流类型
- `content-disposition` 包含附件文件名

说明：

- 导出接口适合单独归类，不和 JSON 统计接口混写在同一条执行链里
- 若当前框架对文件流断言支持有限，可先作为 B 类或探测集

## 4. 接口分级建议

### 4.1 A 类：优先进入稳定查询集

- `GET /backgroundManagement/isManager`
- `GET /backgroundManagement/queryApplicationDataListByPage`
- `GET /backgroundManagement/queryApplicationDataListTotal`
- `GET /backgroundManagement/allTenantApplicationDataListByPage`
- `GET /backgroundManagement/allTenantApplicationDataListTotal`
- `GET /backgroundManagement/queryApplicationDataNum`
- `GET /backgroundManagement/allTenantApplicationDataNum`
- `GET /backgroundManagement/queryApplicationNumByType`
- `GET /backgroundManagement/allTenantApplicationNumByType`
- `GET /backgroundManagement/queryDataCard`
- `GET /backgroundManagement/queryAllDataCard`
- `GET /backgroundManagement/queryDataCard2`
- `GET /backgroundManagement/allTenantDataCard2`
- `GET /backgroundManagement/queryDateDrivenLine`
- `GET /backgroundManagement/AllDateDrivenLine`
- `GET /backgroundManagement/queryApplicationByPage`
- `GET /backgroundManagement/queryApplicationTotal`
- `GET /backgroundManagement/queryModelByPage`
- `GET /backgroundManagement/queryModelTotal`
- `GET /backgroundManagement/queryWorkByPage`
- `GET /backgroundManagement/queryWorkTotal`
- `GET /backgroundManagement/queryActionByPage`
- `GET /backgroundManagement/queryActionTotal`
- `GET /backgroundManagement/queryDetectionByPage`
- `GET /backgroundManagement/queryDetectionTotal`
- `GET /backgroundManagement/querySchemeByPage`
- `GET /backgroundManagement/querySchemeTotal`
- `GET /backgroundManagement/queryUserByPage`
- `GET /backgroundManagement/queryUserTotal`
- `GET /backgroundManagement/queryProcessByPage`
- `GET /backgroundManagement/queryProcessTotal`
- `GET /backgroundManagement/queryTaskByPage`
- `GET /backgroundManagement/queryTaskTotal`
- `GET /backgroundManagement/queryHooksByPage`
- `GET /backgroundManagement/queryHooksTotal`

### 4.2 B 类：导出专项或第二批

- `GET /applicationTest6/exportApp`
- `GET /pageDesignTest6/export`
- `GET /pageDesignTest6/exportWithMonth`
- `GET /pageViewTest6/export`
- `GET /userTest6/exportUser`

### 4.3 C 类：环境依赖或需要专项确认

- 暂无明显 C 类 JSON 接口
- 导出接口若当前自动化框架文件流断言能力不足，可临时降级为探测集

## 5. YAML 落地建议

建议后续落地时按“模板化批量生成”处理，而不是人工一条条手写。

最适合的顺序：

1. 先落 `backgroundManagement` 的 4 条主闭环
2. 再补导出专项

生成要求：

- 以分页/总数成对接口作为基本模板
- 相同筛选参数可复用，不需要为每条接口发明不同数据
- 不强行要求分页首条记录跨接口一致
- 导出接口单独分类，不混入普通 JSON 断言模板

## 6. 下一步建议

如果目标是“这次步子迈大一点”，`backendmanage` 非常适合做成一整批模板化 YAML，因为：

1. 接口多
2. 结构统一
3. 环境副作用低
4. 对覆盖率提升直接有效

后续真要落 YAML，可以先一口气把 `backgroundManagement` 的分页/总数接口全部补上，再决定是否把导出接口纳入稳定集。
