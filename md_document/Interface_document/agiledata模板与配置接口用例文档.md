# agiledata模板与配置接口用例文档

更新时间：2026-04-14

## 1. 目标

本轮继续沿用“稳定优先、单文件推进、大步提升覆盖率”的策略，目标文件为：

- `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_base_support.yaml`

本轮不再补零散 probe，而是集中落 4 组稳定接口：

1. `nodeTemplate` 自定义节点模板闭环
2. `target` 目标数据闭环
3. `operate` 操作偏好小闭环
4. `aiLog + application + permission + autoSwitch` 稳定查询组

本轮目标是一次性补齐 `18` 个当前 YAML 中尚未纳入的新接口。

## 2. 模块结论

### 2.1 nodeTemplate

这是最标准的一组闭环，接口形态清晰，最小请求体简单，适合直接稳定落地：

- `POST /athena-designer/agile/nodeTemplate/insert`
- `POST /athena-designer/agile/nodeTemplate/findListPage`
- `GET /athena-designer/agile/nodeTemplate/findList`
- `POST /athena-designer/agile/nodeTemplate/update`
- `POST /athena-designer/agile/nodeTemplate/delete`

闭环建议：

- 新增节点模板
- 分页查询回查 `templateId`
- 列表查询确认模板已归入对应节点类型
- 更新模板名称/描述
- 删除模板恢复环境

关键约束：

- `templateSource` 必须为 `custom`
- `templateNodeType` 必须为系统允许值，如 `INPUT`
- `appCode` 不能为空

### 2.2 target

目标数据适合做“新增 -> 分页 -> 字典查询 -> 删除”的最小闭环：

- `POST /athena-designer/agile/target/createOrUpdate`
- `POST /athena-designer/agile/target/getTargetDataPageList`
- `GET /athena-designer/agile/target/getDictByKey`
- `GET /athena-designer/agile/target/delete`

关键约束：

- 新增时必须补 `lang`
- `key` 需传 `target_data`
- 删除前不能被场景或指标引用，因此本轮仅删除当前闭环自己创建的数据

### 2.3 operate

操作偏好没有删除接口，但可以形成稳定的小闭环：

- `GET /athena-designer/agile/operate/queryByUser`
- `POST /athena-designer/agile/operate/update`

闭环建议：

- 固定 `userId` 查询，若不存在由后端自动生成默认偏好
- 缓存返回 `code`
- 更新同一配置，验证可稳定执行

### 2.4 稳定查询组

这组不做新增删除，但属于当前适合直接纳入稳定集的只读接口：

- `POST /athena-designer/agile/aiLogInfoController/dayOnDay`
- `POST /athena-designer/agile/aiLogInfoController/dayCount`
- `POST /athena-designer/agile/aiLogInfoController/userCount`
- `GET /athena-designer/agile/application/getModelListByApp`
- `GET /athena-designer/agile/aiDataFlowGenerateController/permission`
- `POST /athena-designer/agile/autoSwitch/pageList`
- `GET /athena-designer/agile/autoSwitch/getLastedPublishedVersion`

处理原则：

- 只做成功码和结果结构断言
- 不依赖外部创建实体
- 不把空列表当失败

## 3. YAML落地建议

建议落地顺序：

1. `nodeTemplate` 闭环
2. `target` 闭环
3. `operate` 小闭环
4. 稳定查询组

建议缓存：

- `agiledata_node_template_name`
- `agiledata_node_template_id`
- `agiledata_target_code`
- `agiledata_target_value`
- `agiledata_target_id`
- `agiledata_operate_code`

建议断言：

- 创建/更新/删除接口：`$.code == 0`
- 分页/列表接口：`$.code == 0` 且列表字段存在
- 详情/字典查询：`$.code == 0`

## 4. 本轮正式新增接口目标

本轮按唯一 `method + url` 统计，目标新增 `18` 个接口：

1. `POST /athena-designer/agile/nodeTemplate/insert`
2. `POST /athena-designer/agile/nodeTemplate/findListPage`
3. `GET /athena-designer/agile/nodeTemplate/findList`
4. `POST /athena-designer/agile/nodeTemplate/update`
5. `POST /athena-designer/agile/nodeTemplate/delete`
6. `POST /athena-designer/agile/target/createOrUpdate`
7. `POST /athena-designer/agile/target/getTargetDataPageList`
8. `GET /athena-designer/agile/target/getDictByKey`
9. `GET /athena-designer/agile/target/delete`
10. `GET /athena-designer/agile/operate/queryByUser`
11. `POST /athena-designer/agile/operate/update`
12. `POST /athena-designer/agile/aiLogInfoController/dayOnDay`
13. `POST /athena-designer/agile/aiLogInfoController/dayCount`
14. `POST /athena-designer/agile/aiLogInfoController/userCount`
15. `GET /athena-designer/agile/application/getModelListByApp`
16. `GET /athena-designer/agile/aiDataFlowGenerateController/permission`
17. `POST /athena-designer/agile/autoSwitch/pageList`
18. `GET /athena-designer/agile/autoSwitch/getLastedPublishedVersion`
