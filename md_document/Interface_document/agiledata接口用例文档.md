# agiledata接口用例文档

更新时间：2026-04-10

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 `agiledata` 相关 Controller 源码整理，用于作为后续生成 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai` 下 YAML 用例的中间设计文档。

本次不按单个接口去重，而按“大模块 + 多业务闭环”组织。  
同一个接口允许在不同闭环中重复出现，只要它在该闭环里承担了清晰职责，就保留。

当前建议归属：

- 业务域：建议新增或并入 `ai_base_support.yaml`
- 文档来源：Controller 方法签名 + 现有覆盖率提升方案 + 闭环生成经验

本次重点分析的后端入口包括：

- `com.digiwin.athena.agiledata.controller.BusinessTypeController`
- `com.digiwin.athena.agiledata.controller.ClassificationController`
- `com.digiwin.athena.agiledata.controller.StandardParamsController`
- `com.digiwin.athena.agiledata.controller.InstructionSetController`
- `com.digiwin.athena.agiledata.controller.DataFlowController`

## 2. 模块结论

### 2.1 适合一次性作为大模块推进

`agiledata` 虽然 controller 很多，但其中有一批接口天然符合自动化的小闭环模式：

1. 新增或保存
2. 分页查询或列表查询
3. 详情或关联查询
4. 删除
5. 删除后确认或结构复查

因此它适合不是按零散接口推进，而是一次性拆成多个可并行落地的子闭环，再统一归入一个大模块文档。

### 2.2 当前最适合优先落地的子闭环

优先建议按以下 5 条链路组织：

1. `businessType` 业务类型 CRUD 小闭环
2. `classification` 分类 CRUD 小闭环
3. `standardParams` 标准参数与映射闭环
4. `instruction` 指令集分组闭环
5. `dataFlow` 查询/详情/复制型闭环

其中前 4 条更适合直接进稳定集，第 5 条更适合作为大模块中的“复杂查询闭环”。

### 2.3 当前不适合作为首批闭环主链的接口

以下接口建议暂缓，或仅在专项场景下处理：

- `POST /standardParams/import`
- `POST /standardParams/download`
- `POST /instruction/importInstructionSet`
- `GET /instruction/exportInstructionSet`
- `POST /dataFlow/getSqlByQuerySchema`
- `POST /dataFlow/pullingParamsCheck`
- `POST /dataFlow/companyFieldsCheck`
- `POST /dataFlow/modelIdCheck`
- `POST /dataFlow/nodeCopyCheck`
- `GET /dataFlow/changeModelIds`
- `POST /classification/batchUpdateTriggerClassification`
- `GET /classification/getRelList`

原因：

- 文件导入导出、SQL、节点校验、批量关系刷新都更适合后续专项覆盖
- 很多接口依赖复杂业务实体或历史数据，不适合首批 AI 闭环

## 3. 推荐业务闭环

### 3.1 主闭环 A：businessType 业务类型 CRUD 闭环

闭环目标：在指定应用下创建业务类型，分页与列表查询命中，再删除并恢复环境。

推荐顺序：

1. `POST /businessType/createOrUpdate`
2. `POST /businessType/getBusinessTypesByPage`
3. `GET /businessType/getList`
4. `DELETE /businessType/delete/{id}`

关键规则：

- `createOrUpdate` 返回对象应缓存 `id/code`
- 分页查询和列表查询不要求首条记录完全一致，只要求能命中当前新建对象
- 删除必须消费当前闭环缓存的真实 `id`

建议缓存：

- `agiledata_business_type_id`
- `agiledata_business_type_code`

建议断言：

- `$.code == 0`
- 查询结果中对象存在

### 3.2 主闭环 B：classification 分类 CRUD 闭环

闭环目标：创建分类，分页与列表查询命中，删除恢复环境。

推荐顺序：

1. `POST /classification/createOrUpdate`
2. `POST /classification/getClassificationsByPage`
3. `GET /classification/getList`
4. `DELETE /classification/delete/{id}`

补充说明：

- `getRelList` 依赖真实触发器或关联对象，不建议首批强串进主闭环
- `refreshMissingRelForAll` 更适合作为工具型接口，不建议纳入稳定闭环

建议缓存：

- `agiledata_classification_id`
- `agiledata_classification_code`

建议断言：

- `$.code == 0`
- 列表中能命中当前分类

### 3.3 主闭环 C：standardParams 标准参数闭环

闭环目标：创建标准参数，完成分页查询、普通查询、删除，以及映射查询闭环。

推荐顺序：

1. `POST /standardParams/createOrUpdate`
2. `POST /standardParams/queryStandardParamsByPage`
3. `POST /standardParams/queryStandardParams`
4. `POST /standardParams/getStandardParams`
5. `GET /standardParams/delete`

可选扩展链：

1. `POST /standardParams/saveOrUpdateMapping`
2. `POST /standardParams/queryMapping`
3. `GET /standardParams/deleteMapping`

关键规则：

- 参数实体和参数映射最好拆成两段闭环，不要首批一次性把所有关系强串起来
- `initData` 是环境初始化动作，不建议放进日常稳定集
- `import/download` 单独归为文件专项

建议缓存：

- `agiledata_standard_param_id`
- `agiledata_standard_param_code`
- `agiledata_standard_mapping_id`

建议断言：

- `$.code == 0`
- 查询结果非空且能命中当前参数

### 3.4 主闭环 D：instruction 指令集分组闭环

闭环目标：创建指令集分组，分页查询、详情查询、重复校验、删除恢复环境。

推荐顺序：

1. `POST /instruction/addInstructionGroup`
2. `POST /instruction/queryInstructionSetByPage`
3. `GET /instruction/getInstructionSetDetail`
4. `GET /instruction/repeatCheck`
5. `GET /instruction/deleteInstructionGroup`

第二批扩展：

1. `POST /instruction/editInstructionSet`
2. `POST /instruction/updateSort`

原因：

- 指令集本身具备较清晰的增删改查形态
- 导入导出和迁移类接口不适合首批稳定集

建议缓存：

- `agiledata_instruction_code`

建议断言：

- `$.code == 0`
- 详情对象存在
- 重复校验结果对象存在

### 3.5 子闭环 E：dataFlow 查询与复制闭环

闭环目标：在已有数据流种子前提下，围绕分页、详情、复制、模板操作形成查询型闭环。

推荐顺序：

1. `POST /dataFlow/getDataFlowsByPage`
2. `GET /dataFlow/detail`
3. `GET /dataFlow/getPullingDataParams`
4. `GET /dataFlow/getLeafNodeDateParams`
5. `POST /dataFlow/copyDataFlow`
6. `POST /dataFlow/queryDataFlowTemplateList`
7. `POST /dataFlow/copyAsTemplate`

说明：

- `dataFlow/createOrUpdate` 理论上可用于主闭环，但 DTO 复杂度明显高于前 4 条主链
- 首批更适合“真实种子驱动的查询/复制闭环”
- 若后面确认存在稳定最小请求体，再单独升级成 CRUD 闭环

建议缓存：

- `agiledata_dataflow_code`
- `agiledata_dataflow_id`

建议断言：

- `$.code == 0`
- 详情对象存在
- 复制返回成功

## 4. 接口分级建议

### 4.1 A 类：优先进入稳定集

- `POST /businessType/createOrUpdate`
- `POST /businessType/getBusinessTypesByPage`
- `GET /businessType/getList`
- `DELETE /businessType/delete/{id}`
- `POST /classification/createOrUpdate`
- `POST /classification/getClassificationsByPage`
- `GET /classification/getList`
- `DELETE /classification/delete/{id}`
- `POST /standardParams/createOrUpdate`
- `POST /standardParams/queryStandardParamsByPage`
- `POST /standardParams/queryStandardParams`
- `POST /standardParams/getStandardParams`
- `GET /standardParams/delete`
- `POST /instruction/addInstructionGroup`
- `POST /instruction/queryInstructionSetByPage`
- `GET /instruction/getInstructionSetDetail`
- `GET /instruction/repeatCheck`
- `GET /instruction/deleteInstructionGroup`

### 4.2 B 类：适合作为补充查询或第二批闭环

- `POST /standardParams/saveOrUpdateMapping`
- `POST /standardParams/queryMapping`
- `GET /standardParams/deleteMapping`
- `POST /instruction/editInstructionSet`
- `POST /instruction/updateSort`
- `POST /dataFlow/getDataFlowsByPage`
- `GET /dataFlow/detail`
- `GET /dataFlow/getPullingDataParams`
- `GET /dataFlow/getLeafNodeDateParams`
- `POST /dataFlow/copyDataFlow`
- `POST /dataFlow/queryDataFlowTemplateList`
- `POST /dataFlow/copyAsTemplate`
- `GET /dataFlow/getProductLine`

### 4.3 C 类：暂缓或专项处理

- `POST /standardParams/import`
- `POST /standardParams/download`
- `GET /standardParams/initData`
- `POST /standardParams/queryRelateDataList`
- `POST /standardParams/getSuggestions`
- `POST /standardParams/getAiSuggestions`
- `POST /standardParams/createStandardParam`
- `POST /classification/batchUpdateTriggerClassification`
- `GET /classification/getRelList`
- `POST /classification/refreshMissingRelForAll`
- `POST /instruction/sceneIntentionsMigration`
- `GET /instruction/exportInstructionSet`
- `POST /instruction/importInstructionSet`
- `POST /dataFlow/createOrUpdate`
- `GET /dataFlow/delete`
- `POST /dataFlow/batchDelete`
- `POST /dataFlow/dealHistoryData`
- `GET /dataFlow/saveAll`
- `POST /dataFlow/getSqlByQuerySchema`
- `POST /dataFlow/pullingParamsCheck`
- `POST /dataFlow/companyFieldsCheck`
- `POST /dataFlow/modelIdCheck`
- `POST /dataFlow/nodeCopyCheck`
- `GET /dataFlow/changeModelIds`

## 5. YAML 落地建议

建议落地方式不是一次把整个 `agiledata` 全砸进一个链里，而是按一个大模块文档下的多子闭环分批实现。

建议优先顺序：

1. `businessType` 闭环
2. `classification` 闭环
3. `standardParams` 主闭环
4. `instruction` 主闭环
5. `dataFlow` 查询闭环

生成要求：

- 允许同一个查询接口在多个闭环里重复出现
- 不允许拿分页首条记录直接代替真实创建对象
- 删除接口必须依赖同一闭环真实缓存
- 文件导入导出、SQL 校验、迁移类接口暂不混入首批稳定集

## 6. 下一步建议

最合理的推进方式：

1. 先在 `ai_base_support.yaml` 或新建 `ai_agiledata.yaml` 里落 `businessType + classification`
2. 再补 `standardParams`
3. 最后视 DTO 复杂度决定是否把 `instruction` 和 `dataFlow` 一起推进

如果目标是一次做大一点，`agiledata` 最合适的方式不是一条超长链，而是“一个大模块文档下的 4 到 5 条稳定子闭环”。
