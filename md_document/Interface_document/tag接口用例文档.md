# tag接口用例文档

## 模块结论

- 本轮优先落地 `tag + tagDefinition`，归属 `ai_base_support.yaml`
- 采用 3 条稳定小闭环：
  - 公共标签闭环：创建公共标签 -> 模糊查询 -> 公共分类查询 -> 公共字段绑定 -> 绑定查询 -> 清理绑定 -> 删除标签
  - 私有标签闭环：查询稳定项目/任务种子 -> 建立 taskRelation -> 同步动作字段 -> 创建私有标签 -> 私有标签查询/分页 -> 私有字段绑定 -> 绑定查询 -> 删除动作 -> 删除标签
  - 标签定义闭环：创建 -> 查询 -> 删除
- 接口允许重复作为闭环支撑接口，但本轮目标是优先覆盖此前未覆盖的唯一 `method + url`

## A类稳定闭环

### 1. 公共标签闭环

- `POST /athena-designer/tag`
- `GET /athena-designer/tag`
- `GET /athena-designer/tag/public/all`
- `POST /athena-designer/tag/binding/public`
- `GET /athena-designer/tag/binding/public`
- `DELETE /athena-designer/tag/binding/public/{actionId}/{type}/{attr}`
- `DELETE /athena-designer/tag/id/{id}`

闭环说明：

- 先创建 `common=true` 的公共标签
- 绑定到现有稳定缓存 `tag_action_id + tag_action_attr`
- 用绑定查询确认公共标签已经挂到动作字段
- 清空绑定后再删除公共标签，避免残留污染

### 2. 私有标签闭环

- `POST /athena-designer/tag/taskRelation`
- `GET /athena-designer/tag/taskRelation`
- `POST /athena-designer/tag/taskAction/sync`
- `GET /athena-designer/tag/private`
- `POST /athena-designer/tag/queryPage`
- `POST /athena-designer/tag/binding/private/save`
- `POST /athena-designer/tag/binding/private`
- `POST /athena-designer/tag/binding/tag/extInfo`
- `POST /athena-designer/tag/queryOpenWindowAction`
- `POST /athena-designer/tag/taskAction/delete`
- `DELETE /athena-designer/tag/id/{id}`

闭环说明：

- 先用稳定项目与任务查询拿到 `projectCode / taskCode`
- 对真实任务建立最小 `taskRelation`
- 用 `syncTaskAction` 把动作字段补全
- 创建私有标签并绑定到动作字段
- 查询私有标签与分页结果确认标签生效
- `extInfo` 与 `queryOpenWindowAction` 只做稳定结构校验，不强依赖业务内容非空
- 最后删除 taskAction，再删除私有标签

### 3. 标签定义闭环

- `POST /athena-designer/tagDefinition`
- `GET /athena-designer/tagDefinition`
- `DELETE /athena-designer/tagDefinition/code/{code}`

闭环说明：

- `getAll` 已有历史覆盖，本轮仍以创建后的 `get` 校验为主
- `code` 必须唯一，删除放在闭环尾部清理残留

## B类稳定查询

- `GET /athena-designer/tag/category`

说明：

- 该接口无需前置实体，直接做稳定查询覆盖

## 不纳入本轮稳定集

- `DELETE /athena-designer/tag/git`
  - 后端直接抛业务异常，不适合稳定集

## 关键前置与缓存

- 复用已有缓存：
  - `tag_action_id`
  - `tag_action_attr`
- 本轮新增缓存：
  - `tag_private_ai_project_code`
  - `tag_private_ai_group_code`
  - `tag_private_ai_task_code`
  - `tag_public_ai_id`
  - `tag_public_ai_code`
  - `tag_private_ai_id`
  - `tag_private_ai_code`
  - `tag_definition_ai_code`

## YAML落地建议

- 文件：`D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_base_support.yaml`
- 新增接口时优先保证：
  - 所有删除动作放在闭环尾部
  - 不依赖列表首条随机种子，前置实体尽量由本闭环自行构造
  - 查询断言以 `code==0`、对象存在、关键字段匹配为主
  - 对环境差异大的接口避免断言非空业务数据
