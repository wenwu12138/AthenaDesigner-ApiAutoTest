# agiledata扩展接口用例文档

更新时间：2026-04-14

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 `agiledata` 相关源码整理，作为本轮新增稳定闭环 YAML 的中间设计文档。

本轮目标不是继续补零散查询，而是一次性推进一批可回收、可清理、可稳定执行的小闭环，集中落到：

- `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_base_support.yaml`

本轮采用的推进原则：

- 以稳定为第一优先级
- 单文件集中落地
- 优先使用“新增 -> 查询/详情 -> 更新 -> 删除”的小闭环
- 删除接口必须消费同一闭环内的真实缓存
- 不使用首条环境数据作为伪种子

## 2. 本轮模块结论

本轮最适合一次性推进的 `agiledata` 扩展闭环有三组：

1. `sectionConfig` 板块配置闭环
2. `businessVariables` 业务变量闭环
3. `boardInfo` 收藏夹草稿闭环

其中：

- `sectionConfig` 是最标准的 CRUD + copy 结构，适合作为主闭环
- `businessVariables` 适合做新增、分页、列表、更新、删除，并补一个无副作用的 `addSysVariables` 空列表调用覆盖
- `boardInfo` 如果使用 `status = 0` 草稿态，可以绕过场景校验，形成稳定闭环

按唯一接口统计，本轮目标接口数为 `18`：

- `sectionConfig`：7 个
- `businessVariables`：6 个
- `boardInfo`：5 个

## 3. 推荐业务闭环

### 3.1 主闭环 A：sectionConfig 板块配置闭环

推荐顺序：

1. `POST /athena-designer/sectionConfig/add`
2. `POST /athena-designer/sectionConfig/getListByPage`
3. `GET /athena-designer/sectionConfig/detail`
4. `POST /athena-designer/sectionConfig/edit`
5. `GET /athena-designer/sectionConfig/getAll`
6. `POST /athena-designer/sectionConfig/copy`
7. `GET /athena-designer/sectionConfig/delete`

关键约束：

- `add` 请求体必须带 `showConfig.showType`，否则分页结果转换时容易触发空指针
- `status` 必须置为 `1`，否则 `getAll` 不会返回
- `copy` 依赖新增实体本身的 `lang.name`，新增时必须补上 `lang`
- 删除时先删副本，再删原对象，保证环境可逆

建议缓存：

- `agiledata_section_config_code`
- `agiledata_section_config_name`
- `agiledata_section_config_copy_code`

### 3.2 主闭环 B：businessVariables 业务变量闭环

推荐顺序：

1. `POST /athena-designer/agile/businessVariablesController/insert`
2. `POST /athena-designer/agile/businessVariablesController/getPage`
3. `POST /athena-designer/agile/businessVariablesController/getList`
4. `POST /athena-designer/agile/businessVariablesController/update`
5. `POST /athena-designer/agile/businessVariablesController/addSysVariables`
6. `POST /athena-designer/agile/businessVariablesController/delete`

关键约束：

- `insert` 返回体不直接给对象，需要通过 `getPage` 反查 `id`
- `code` 实际由后端规则生成：`appCode + "_" + data_name`
- `delete` 至少要传真实 `id/appCode/code`，否则引用校验无法通过
- `addSysVariables` 只做空列表安全调用，用于覆盖唯一接口，不纳入主缓存链

建议缓存：

- `agiledata_business_var_id`
- `agiledata_business_var_code`
- `agiledata_business_var_data_name`
- `agiledata_business_var_name`

### 3.3 主闭环 C：boardInfo 收藏夹草稿闭环

推荐顺序：

1. `POST /athena-designer/agile/boardInfo/insert`
2. `POST /athena-designer/agile/boardInfo/getPage`
3. `POST /athena-designer/agile/boardInfo/update`
4. `POST /athena-designer/agile/boardInfo/copy`
5. `GET /athena-designer/agile/boardInfo/delete`

关键约束：

- 使用 `status = 0` 草稿态，绕过场景与问题项校验
- `delete` 实际删除的是 `groupId`
- `copy` 要显式传新的 `groupValue`，否则复制后难以精准定位副本
- 删除顺序仍然是先删副本，再删原对象

建议缓存：

- `agiledata_board_group_value`
- `agiledata_board_group_id`
- `agiledata_board_id`
- `agiledata_board_copy_group_value`
- `agiledata_board_copy_group_id`

## 4. 接口分级建议

### 4.1 A 类：本轮直接进入稳定集

- `POST /athena-designer/sectionConfig/add`
- `POST /athena-designer/sectionConfig/getListByPage`
- `GET /athena-designer/sectionConfig/detail`
- `POST /athena-designer/sectionConfig/edit`
- `GET /athena-designer/sectionConfig/getAll`
- `POST /athena-designer/sectionConfig/copy`
- `GET /athena-designer/sectionConfig/delete`
- `POST /athena-designer/agile/businessVariablesController/insert`
- `POST /athena-designer/agile/businessVariablesController/getPage`
- `POST /athena-designer/agile/businessVariablesController/getList`
- `POST /athena-designer/agile/businessVariablesController/update`
- `POST /athena-designer/agile/businessVariablesController/addSysVariables`
- `POST /athena-designer/agile/businessVariablesController/delete`
- `POST /athena-designer/agile/boardInfo/insert`
- `POST /athena-designer/agile/boardInfo/getPage`
- `POST /athena-designer/agile/boardInfo/update`
- `POST /athena-designer/agile/boardInfo/copy`
- `GET /athena-designer/agile/boardInfo/delete`

### 4.2 B 类：后续补充

- `POST /athena-designer/agile/businessVariablesController/dealHistoryData`

原因：

- 该接口会批量改写历史数据，风险高于本轮其它闭环
- 不适合在稳定集里为了凑覆盖率硬接入

### 4.3 C 类：本轮暂缓

- 强依赖大屏、场景、数据流真实关系的接口
- 需要外部引用校验才能完成删除的复杂业务链

## 5. YAML 落地建议

建议本轮一次性写入 `ai_base_support.yaml`，但按三组小闭环顺序组织，不混成单条超长链：

1. `sectionConfig` 闭环
2. `businessVariables` 闭环
3. `boardInfo` 草稿闭环

断言策略建议：

- 创建/更新/删除接口：优先校验 `$.code == 0`
- 分页/列表接口：校验列表长度大于 0，并命中当前闭环唯一标识
- 详情接口：校验关键字段等于当前缓存

## 6. 下一步建议

如果本轮通过并确认正式有效覆盖提升达到预期，下一轮继续从 `agiledata` 内部补第二批：

- `instruction` 真闭环
- `dataFlow` 查询/复制闭环

前提是仍然坚持“稳定优先”，不为了接口数牺牲可回归性。
