# subpage + openWindow + pageDesignModel 接口用例文档

## 1. 文档目标

本批次以 `ai_task_process.yaml` 为唯一落地点，围绕现有 `pagedesign_ai_page_code` 与 `resource_tree_model_code` 两个稳定缓存，补三组小闭环：

1. `subpage` 子页面可逆闭环
2. `openWindow` 开窗定义可逆闭环
3. `pageDesignModel` 模型字段稳定查询闭环

设计目标：

- 以稳定优先，不依赖环境首条数据
- 使用新增接口制造前置实体
- 使用删除接口回收残留
- 单文件内一次提升一批唯一 `method + url`

## 2. 闭环拆分

### 2.1 subpage 子页面闭环

前置依赖：

- 复用 `ai_task_process.yaml` 现有主闭环已生成的 `pagedesign_ai_page_code`

闭环顺序：

1. `POST /subpage/subpageAdd`
2. `POST /subpage/subpageAdd`
3. `POST /subpage/subpageQueryList`
4. `POST /subpage/subpageQueryDetail`
5. `GET /subpage/updateNameByCode`
6. `POST /subpage/subpageUpdate`
7. `POST /subpage/subpageBatchUpdate`
8. `POST /subpage/subpageBatchSync`
9. `POST /subpage/subpageDelete`

设计说明：

- 先创建两个子页面，给批量同步提供真实目标页
- `subpageUpdate` 与 `subpageBatchUpdate` 只传最小稳定字段，不强依赖复杂 DSL
- `subpageDelete` 使用同一闭环产生的两个真实 code 清理残留

### 2.2 openWindow 开窗定义闭环

前置依赖：

- 复用现有应用编码 `${{app2_code()}}`

闭环顺序：

1. `POST /openWindow/save`
2. `GET /openWindow/{application}`
3. `GET /openWindow/ow/{code}`
4. `POST /openWindow/update`
5. `DELETE /openWindow/{code}`

设计说明：

- 请求体走 `ApplicationParam`，只保留 `key/title/category/selectedFirstRow/column`
- `save` 后缓存 `key`
- `update` 仅修改标题，避免引入 `allAction` 等高依赖字段

### 2.3 pageDesignModel 模型字段查询闭环

前置依赖：

- 复用现有缓存 `resource_tree_model_code`
- 复用 `${{serviceCode()}}`

闭环顺序：

1. `GET /pageDesignModel/queryFields`
2. `GET /pageDesignModel/queryFieldsGroup`
3. `GET /pageDesignModel/queryFieldsByCode`
4. `GET /pageDesignModel/queryFieldsByDataType`
5. `POST /pageDesignModel/queryFieldsGroupList`
6. `POST /pageDesignModel/generateApiConfig`

设计说明：

- 这组以稳定查询为主，不新增业务数据
- `generateApiConfig` 最小请求体只传 `modelCode + serviceCode`
- 不再重复引入 `queryBindApiListConfig`，避免和已有覆盖重叠

## 3. 归类与落地

归属文件：

- `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_task_process.yaml`

接口分类：

- A 类：`subpage` 全闭环、`openWindow` 全闭环、`pageDesignModel` 查询闭环
- B 类：无
- C 类：无

预期收益：

- 本批次预计新增 `19` 个左右唯一接口
- 在稳定前提下，有机会带来约 `+1%` 左右正式覆盖率提升
