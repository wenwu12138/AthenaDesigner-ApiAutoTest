# pagedesign接口用例文档

更新时间：2026-04-10

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 `pagedesign` 相关 Controller 源码整理，用于作为后续生成 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai` 下 YAML 用例的中间设计文档。

本次不按“接口去重”组织，而按“业务闭环”组织。  
同一个接口允许在多个闭环中重复出现，只要它在不同闭环里承担的业务职责不同，且有助于形成稳定回归链路，就应该保留。

当前建议归属：

- 业务域：`ai_task_process.yaml`
- 文档来源：Controller 方法签名 + 现有稳定业务 YAML + 当前已有闭环经验

本次重点分析的后端入口包括：

- `com.digiwin.athena.controller.pagedesign.BusinessSourceTreeController`
- `com.digiwin.athena.controller.pagedesign.DataViewController`
- `com.digiwin.athena.controller.pagedesign.DapPageDesignController`
- `com.digiwin.athena.controller.pagedesign.WorkBenchController`

## 2. 模块结论

### 2.1 适合按“大闭环”推进

`pagedesign` 是当前最适合按“大一点的业务模块”推进的模块之一，因为它天然不是单接口价值，而是完整设计链路价值：

1. 先有业务对象种子
2. 再围绕业务对象生成查询方案
3. 再基于查询方案生成页面
4. 再查询、更新、删除页面
5. 最后清理业务对象，恢复环境

这条链天然允许接口重复。例如：

- `queryByCode` 可以在“页面生成闭环”里作为生成后校验
- 同一个 `queryByCode` 也可以在“页面维护闭环”里作为更新后复核

这不是重复劳动，而是闭环语义不同。

### 2.2 当前最适合优先落地的闭环

优先建议按以下 3 条链路组织：

1. 业务对象 -> 查询方案 -> 页面生成主闭环
2. 已生成页面 -> 页面详情/数据源/动作标识查询闭环
3. 应用维度页面/工作台稳定查询闭环

其中第 1 条是主闭环，第 2 条依附第 1 条，第 3 条作为稳定补充查询集。

### 2.3 当前不适合作为主闭环起点的接口

以下接口更适合作为补充查询或探测集，不建议直接拿来充当大闭环第一跳：

- `GET /athena-designer/pageDesign/queryByApplication`
- `GET /athena-designer/pageDesign/assignNameCheck`
- `GET /athena-designer/pageDesign/espProduct/{application}`
- `GET /athena-designer/pageDesign/queryDataSourcesByCode`
- `GET /athena-designer/pageDesign/getActionIdByCode`
- `POST /athena-designer/resourceTree/queryListOfSource`
- `POST /athena-designer/resourceTree/queryListOfSourceRefresh`
- `GET /athena-designer/workbench/queryByApplication`

原因：

- 这些接口很多依赖“已有页面 code”或“当前应用下已有资源”
- 如果直接拿列表首条做种子，容易重新落回“环境首条数据依赖”
- 它们更适合作为主闭环成功后的消费节点，而不是起点

## 3. 推荐业务闭环

### 3.1 主闭环 A：业务对象 -> 查询方案 -> 页面生成 -> 页面维护 -> 环境恢复

闭环目标：创建一个专用于页面设计的测试业务对象，生成查询方案与页面，再完成更新与删除，最后删除业务对象，形成完整可逆链路。

推荐顺序：

1. `POST /athena-designer/businessDir/add`
2. `GET /athena-designer/modelDriver/queryModelByCode`
3. `POST /athena-designer/dataView/generateJustQueryPlan`
4. `POST /athena-designer/dataView/queryDataViewByModel`
5. `POST /athena-designer/pageDesign/generatePageDesignByQueryPlan`
6. `GET /athena-designer/pageDesign/queryByCode`
7. `POST /athena-designer/pageDesign/update`
8. `GET /athena-designer/pageDesign/queryByCode`
9. `GET /athena-designer/pageDesign/delete`
10. `POST /athena-designer/businessDir/delete`

#### 3.1.1 创建业务对象

- 接口：`POST /athena-designer/businessDir/add`
- 作用：生成页面设计测试专用业务对象
- 关键价值：为后续模型查询、查询方案生成、页面生成提供真实种子

建议缓存：

- `pagedesign_test_biz_code`

建议断言：

- `$.code == 0`

#### 3.1.2 查询模型信息

- 接口：`GET /athena-designer/modelDriver/queryModelByCode`
- 作用：基于业务对象 code 拉取模型信息
- 前置来源：`pagedesign_test_biz_code`

建议缓存：

- `pagedesign_business_code`
- `pagedesign_object_id`

建议断言：

- `$.code == 0`
- `$.data != null`

#### 3.1.3 生成仅查询方案

- 接口：`POST /athena-designer/dataView/generateJustQueryPlan`
- 作用：给当前模型生成一个数据视图查询方案
- 前置来源：业务对象和模型查询结果

关键规则：

- `modelId`、`businessCode` 必须消费前面真实缓存
- SQL 可以按已有稳定样例复用，不建议在 AI 首批里自由推断

建议断言：

- `$.code == 0`

#### 3.1.4 查询数据视图

- 接口：`POST /athena-designer/dataView/queryDataViewByModel`
- 作用：获取当前模型下的数据视图列表，并缓存刚生成的数据视图 code
- 前置来源：业务对象 code + businessCode

建议缓存：

- `pagedesign_data_view_code`

建议断言：

- `$.code == 0`
- `$.data != null`
- 命中列表非空

#### 3.1.5 基于查询方案生成页面

- 接口：`POST /athena-designer/pageDesign/generatePageDesignByQueryPlan`
- 作用：根据数据视图生成页面设计
- 前置来源：真实 `businessCode` + `modelId` + `dataViewCodes`

建议缓存：

- `pagedesign_page_code`

建议断言：

- `$.code == 0`
- `$.data.code` 非空

#### 3.1.6 查询页面详情

- 接口：`GET /athena-designer/pageDesign/queryByCode`
- 作用：消费刚生成的页面 code 拉详情
- 前置来源：`pagedesign_page_code`

关键规则：

- `queryByCode` 必须消费当前闭环生成的页面 code
- 不允许退化成“应用下列表首条页面 -> queryByCode”

建议断言：

- `$.code == 0`
- `$.data.code == $cache{pagedesign_page_code}`

#### 3.1.7 更新页面配置

- 接口：`POST /athena-designer/pageDesign/update`
- 作用：更新当前页面基础配置或 DSL
- 前置来源：`queryByCode` 返回的真实页面对象

关键规则：

- 更新请求体优先基于详情返回值最小改造
- 不建议在首批闭环里手写大段 DSL 猜结构

建议断言：

- `$.code == 0`

#### 3.1.8 更新后复查

- 接口：`GET /athena-designer/pageDesign/queryByCode`
- 作用：确认页面仍可被正常查询
- 前置来源：`pagedesign_page_code`

建议断言：

- `$.code == 0`
- `$.data != null`

#### 3.1.9 删除页面

- 接口：`GET /athena-designer/pageDesign/delete`
- 作用：删除当前页面并恢复环境
- 前置来源：`pagedesign_page_code`

建议断言：

- `$.code == 0`

#### 3.1.10 删除业务对象

- 接口：`POST /athena-designer/businessDir/delete`
- 作用：删除主闭环创建的业务对象
- 前置来源：`pagedesign_test_biz_code`

建议断言：

- `$.code == 0`

#### 3.1.11 主闭环结论

当前结论：

- 这是 `pagedesign` 最值得优先落地到 AI 稳定集的大闭环
- 现有仓库中已有真实业务样例，说明链路具备落地基础
- 删除页面 + 删除业务对象后可以恢复环境，满足稳定集要求

### 3.2 子闭环 B：已生成页面 -> 数据源/动作/命名校验查询闭环

闭环目标：在主闭环已经拿到稳定页面 code 的前提下，对页面的辅助查询能力做结构校验。

推荐顺序：

1. `GET /athena-designer/pageDesign/queryByCode`
2. `GET /athena-designer/pageDesign/queryDataSourcesByCode`
3. `GET /athena-designer/pageDesign/getActionIdByCode`
4. `GET /athena-designer/pageDesign/assignNameCheck`

#### 3.2.1 页面数据源查询

- 接口：`GET /athena-designer/pageDesign/queryDataSourcesByCode`
- 前置来源：`pagedesign_page_code`

建议断言：

- `$.code == 0`
- `$.data != null`

#### 3.2.2 页面动作标识查询

- 接口：`GET /athena-designer/pageDesign/getActionIdByCode`
- 前置来源：`pagedesign_page_code`

建议断言：

- `$.code == 0`

#### 3.2.3 页面名称占用检查

- 接口：`GET /athena-designer/pageDesign/assignNameCheck`
- 前置来源：`pagedesign_page_code`

说明：

- 这个接口更适合作为补充查询，不适合独立反向约束主闭环
- 可以只校验 `checkResult` 字段存在，不建议硬断言真假值

### 3.3 子闭环 C：应用维度页面/工作台稳定查询闭环

闭环目标：在固定应用下校验页面设计与工作台的基础查询能力，作为主闭环之外的稳定补充集。

推荐顺序：

1. `GET /athena-designer/pageDesign/queryByApplication`
2. `GET /athena-designer/workbench/queryByApplication`
3. `GET /athena-designer/workbench/queryByCode`

关键规则：

- `queryByApplication` 只校验结构有效，不把首条页面当作主种子
- `workbench/queryByCode` 只有在上一步明确拿到稳定 code 时才消费
- 不做“页面首条 == 工作台首条”的跨接口强绑定

建议断言：

- `$.code == 0`
- 列表接口只校验 `$.data != null`
- 详情接口只校验对象存在

## 4. 接口分级建议

### 4.1 A 类：优先进入稳定大闭环

- `POST /athena-designer/businessDir/add`
- `GET /athena-designer/modelDriver/queryModelByCode`
- `POST /athena-designer/dataView/generateJustQueryPlan`
- `POST /athena-designer/dataView/queryDataViewByModel`
- `POST /athena-designer/pageDesign/generatePageDesignByQueryPlan`
- `GET /athena-designer/pageDesign/queryByCode`
- `POST /athena-designer/pageDesign/update`
- `GET /athena-designer/pageDesign/delete`
- `POST /athena-designer/businessDir/delete`

### 4.2 B 类：适合依附主闭环补充查询

- `GET /athena-designer/pageDesign/queryDataSourcesByCode`
- `GET /athena-designer/pageDesign/getActionIdByCode`
- `GET /athena-designer/pageDesign/assignNameCheck`
- `GET /athena-designer/pageDesign/queryByApplication`
- `GET /athena-designer/workbench/queryByApplication`
- `GET /athena-designer/workbench/queryByCode`

### 4.3 C 类：暂缓或仅探测

- `POST /athena-designer/pageDesign/add`
- `POST /athena-designer/pageDesign/copy`
- `POST /athena-designer/pageDesign/modelDefaultFields`
- `POST /athena-designer/pageDesign/generateDefaultDslByCode`
- `POST /athena-designer/pageDesign/switchToLowCode`
- `POST /athena-designer/dataView/generateViewAndAssign`
- `POST /athena-designer/dataView/addDataView`
- `POST /athena-designer/dataView/saveDataView`
- `GET /athena-designer/dataView/getDataViewDetail`
- `GET /athena-designer/dataView/disassociation`
- `POST /athena-designer/dataView/queryPlanList`
- `POST /athena-designer/dataView/queryDataViewContent`
- `GET /athena-designer/dataView/queryDataViewListByAssignCode`
- `POST /athena-designer/dataView/queryDataViewFields`
- `POST /athena-designer/dataView/generateQueryPlan`
- `POST /athena-designer/dataView/query/queryplan/list`
- `POST /athena-designer/dataView/queryPlanListOfApplication`
- `GET /athena-designer/dataView/getPreviewQueryConfig`
- `POST /athena-designer/dataView/getPreviewResult`
- `POST /athena-designer/dataView/queryTableAndFields`
- `POST /athena-designer/dataView/executeSql`
- `POST /athena-designer/dataView/parseSqlToHeader`
- `POST /athena-designer/resourceTree/queryListOfSource`
- `POST /athena-designer/resourceTree/queryListOfSourceRefresh`

原因：

- DTO 复杂，首批 AI 生成容易靠猜
- 很多接口适合作为编辑器能力接口，不适合作为稳定闭环主链
- 有些接口更偏预览、SQL、资源树、历史刷新，适合后续专项补覆盖

## 5. YAML 落地建议

建议优先落地到：

- `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_task_process.yaml`

建议首批 case 顺序：

1. `pagedesign_biz_add_001`
2. `pagedesign_model_query_001`
3. `pagedesign_generate_query_plan_001`
4. `pagedesign_query_data_view_001`
5. `pagedesign_generate_page_001`
6. `pagedesign_query_by_code_001`
7. `pagedesign_update_001`
8. `pagedesign_query_by_code_after_update_001`
9. `pagedesign_query_data_sources_001`
10. `pagedesign_get_action_id_001`
11. `pagedesign_assign_name_check_001`
12. `pagedesign_delete_001`
13. `pagedesign_biz_delete_001`

生成要求：

- 接口允许重复出现在多个闭环中，不需要刻意去重
- 主闭环必须使用自己创建的业务对象和自己生成的页面 code
- 不允许用应用列表首条页面代替主闭环种子
- 删除动作必须放在闭环末尾
- 若更新接口请求体过重，首批只保留最小必需字段，避免大段 DSL 猜测

## 6. 下一步建议

最合理的后续动作：

1. 先按本文件把主闭环 A 落到 `ai_task_process.yaml`
2. 再把子闭环 B 作为补充查询接到主闭环后面
3. `queryByApplication` 和 `workbench` 仅保留为稳定查询集，不强行反向绑定详情

如果目标是“做一个大一点的模块保证系统稳定性”，`pagedesign` 就是当前最合适的模块，因为它既有真正的业务主链，也天然允许同一接口在不同闭环里重复复用。
