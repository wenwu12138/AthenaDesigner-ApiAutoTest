# agiledatainquiry 接口用例文档

更新时间：2026-04-09

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 `com.digiwin.athena.agiledatainquiry.controller` 模块源码整理，用于作为后续生成 `AthenaDesigner-ApiAutoTest` 自动化 YAML 的中间设计文档。

本模块统一归属建议：

- 业务域：`ai_inquiry.yaml`
- 文档来源：Controller 方法签名 + DTO 结构 + Service 实际逻辑

本模块共 5 个 Controller，31 个接口：

- `KnowledgeBaseController`：5
- `DatasetController`：10
- `DataSourceController`：6
- `ImplicitAssociationController`：4
- `CommonController`：6

## 2. 模块结论

### 2.1 推荐优先落地的接口

优先建议先转成自动化 YAML 的接口：

- `POST /athena-designer/inquiry/knowledge/getPageList`
- `POST /athena-designer/inquiry/knowledge/getList`
- `POST /athena-designer/inquiry/knowledge/createOrUpdate`
- `POST /athena-designer/inquiry/knowledge/batchDelete`
- `POST /athena-designer/inquiry/dataset/getPageList`
- `GET /athena-designer/inquiry/dataset/allDatasets`
- `GET /athena-designer/inquiry/common/authModules`

说明：

- `knowledge` 模块结构清晰，适合先做“小闭环”
- `dataset` 查询接口适合作为稳定查询集
- `common/authModules` 适合单点查询用例，但依赖外部授权服务，建议先做定点探测再纳入稳定集

### 2.2 建议暂缓的接口

当前不建议进入首批通用稳定集的接口：

- `POST /athena-designer/inquiry/dataset/parseExcel`
- `POST /athena-designer/inquiry/dataset/addFromExcel`
- `POST /athena-designer/inquiry/common/import`
- `GET /athena-designer/inquiry/common/downTemplate`
- `GET /athena-designer/inquiry/common/exportV2`
- `GET /athena-designer/inquiry/common/downloadError`
- `POST /athena-designer/inquiry/common/mcpLogin`

原因：

- 文件上传、文件流下载、异步导入、外部文件中心依赖明显
- `mcpLogin` 属于特殊登录辅助接口，不适合作为业务稳定集

### 2.3 本模块推荐闭环

闭环 A：知识库 CRUD 闭环

1. `createOrUpdate`
2. `getList`
3. `getPageList`
4. `batchDelete`
5. 删除后再查

闭环 B：数据集查询闭环

1. `getPageList`
2. `allDatasets`
3. `detail`

闭环 C：数据源查询闭环

1. `getDataSourceTypes`
2. `getList`
3. `getModels`
4. `getModelDetail` 或 `getTableDetail`

## 3. 通用规则

### 3.1 认证要求

本模块大多数接口默认需要登录态。

已知例外：

- `POST /athena-designer/inquiry/common/mcpLogin`
  - 在安全白名单中，可视为无需登录态的特殊登录接口

默认请求头建议：

```yaml
headers:
  digi-middleware-auth-user: $cache{token}
  token: $cache{token}
  locale: zh_CN
  content-type: application/json
```

### 3.2 DTO 继承说明

以下请求对象继承 `BaseDto`，默认带分页字段：

- `KnowledgeBaseReq`
- `DataSetReq`
- `DataSourceListReq`

即生成 YAML 时可考虑公共字段：

- `pageNum`
- `pageSize`

### 3.3 业务域归属

本模块全部接口默认归入：

- `data/ai/ai_inquiry.yaml`

## 4. Controller 级分析

### 4.1 KnowledgeBaseController

类映射：

- `/inquiry/knowledge`

适合度结论：

- 该 Controller 是本模块最适合首批做闭环自动化的部分
- 查询、新增、删除链路清晰
- 风险主要集中在 `type/effectiveScope` 必填约束和“习惯知识最多 5 条”业务限制

#### 4.1.1 `POST /athena-designer/inquiry/knowledge/createOrUpdate`

- 方法名：`createOrUpdate`
- 请求体：`KnowledgeBase`
- Body 关键字段：
  - `application`
  - `code`
  - `name`
  - `type`
  - `businessDefine`
  - `explanation`
  - `synonym`
  - `effectiveScope`
  - `effectiveSets`
- 返回包装：`ResultBean`
- 主要返回路径：`$.code`
- 用例分级：`A`
- 用例类型：`create / update / chain`
- 建议优先级：`P1`
- 建议归属 YAML：`ai_inquiry.yaml`
- 是否依赖真实实体：
  - 新增场景：否
  - 更新场景：是，需要已有 `code`
- 推荐闭环：
  - 知识库 CRUD 闭环
- 建议缓存字段：
  - 请求 `code`
  - 请求 `application`
  - 请求 `type`
- 缓存来源：
  - 优先 `request`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 后续 `getList` 结果中存在该 `code`
  - 若是 `noun`，校验 `businessDefine` 或 `explanation` 可查到
- 后置校验：
  - 写后查
- 是否可逆：
  - 是，可通过 `batchDelete` 或 `delete` 恢复
- 风险：
  - `type` 必须是 `noun` 或 `habit`
  - `effectiveScope` 必须是 `all` 或 `part`
  - `part` 时必须传 `effectiveSets`
  - `habit` 在同应用下数量上限 5
  - `noun` 有重复性校验，不能随便复用固定文案

#### 4.1.2 `POST /athena-designer/inquiry/knowledge/getPageList`

- 方法名：`getPageList`
- 请求体：`KnowledgeBaseReq`
- Body 关键字段：
  - `type`
  - `application`
  - `keyWord`
  - `pageNum`
  - `pageSize`
- 返回包装：`ResultBean`
- 主要返回路径：`$.data.list`
- 用例分级：`A`
- 用例类型：`query`
- 建议优先级：`P1`
- 是否依赖真实实体：否
- 推荐闭环：
  - 知识库查询闭环
  - 知识库 CRUD 闭环中的写后查
- 建议缓存字段：
  - 首条 `code`
  - 首条 `objectId`
- 缓存来源：
  - `response`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - `$.data.list` 非空
  - 首条记录 `type` 与请求一致
- 风险：
  - `type` 为空会直接抛业务异常

#### 4.1.3 `POST /athena-designer/inquiry/knowledge/getList`

- 方法名：`getList`
- 请求体：`KnowledgeBaseReq`
- Body 关键字段：
  - `type`
  - `application`
- 返回包装：`ResultBean`
- 主要返回路径：`$.data`
- 用例分级：`A`
- 用例类型：`query`
- 建议优先级：`P1`
- 是否依赖真实实体：否
- 推荐闭环：
  - 知识库 CRUD 闭环中的回查
- 建议缓存字段：
  - 首条 `code`
  - 首条 `objectId`
- 缓存来源：
  - `response`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 返回列表非空
  - 列表元素 `application` 与请求一致
- 风险：
  - `type` 不能为空
  - service 中要求 `application` 参与查询，若缺失可能查空

#### 4.1.4 `POST /athena-designer/inquiry/knowledge/batchDelete`

- 方法名：`batchDelete`
- 请求体：`KnowledgeBaseReq`
- Body 关键字段：
  - `codeList`
- 返回包装：`ResultBean`
- 主要返回路径：`$.data`
- 用例分级：`A`
- 用例类型：`delete / chain`
- 建议优先级：`P1`
- 是否依赖真实实体：是
- 前置来源：
  - `create_in_chain` 或 `query_existing`
- 推荐闭环：
  - 知识库 CRUD 闭环
- 建议缓存字段：
  - 前置新增时使用的 `code`
- 缓存来源：
  - `request` 或前置 `response`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 删除后 `getList` 查不到该 `code`
- 风险：
  - `codeList` 不能为空

#### 4.1.5 `DELETE /athena-designer/inquiry/knowledge/delete/{id}`

- 方法名：`delete`
- Path 参数：
  - `id`
- 返回包装：`ResultBean`
- 主要返回路径：`$.code`
- 用例分级：`B`
- 用例类型：`delete / chain`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - `query_existing`
  - `create_in_chain` 后再查出 `objectId`
- 推荐闭环：
  - 知识库 CRUD 闭环的补充删除方式
- 建议缓存字段：
  - `objectId`
- 缓存来源：
  - `response`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 删除后分页查询为空或不含目标记录
- 风险：
  - 删除参数是 Mongo `objectId`，不能直接用随机值伪造

### 4.2 DatasetController

类映射：

- `/inquiry/dataset`

适合度结论：

- 查询接口相对容易落地
- 新增、编辑、状态修改接口可做，但请求体复杂度明显高于知识库
- Excel 相关接口当前不建议放入首批稳定集

#### 4.2.1 `POST /athena-designer/inquiry/dataset/add`

- 方法名：`addDataSet`
- 请求体：`DataSet`
- Body 关键字段：
  - `application`
  - `code`
  - `name`
  - `description`
  - `queryMode`
  - `dataSourceId`
  - `dataSourceName`
  - `modelId`
  - `modelCode`
  - `dimensions`
  - `measures`
- 返回包装：`ResultBean`
- 主要返回路径：`$.code`
- 用例分级：`B`
- 用例类型：`create / chain`
- 建议优先级：`P1`
- 是否依赖真实实体：部分依赖
- 前置来源：
  - 通常需要真实模型、数据源信息
- 推荐闭环：
  - 数据集主闭环
- 建议缓存字段：
  - `code`
  - `name`
  - `application`
- 缓存来源：
  - 优先 `request`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - `detail` 查出的 `code/name` 与请求一致
- 风险：
  - `name`、`description` 有校验
  - 依赖 `dimensions/measures/modelId`
  - service 会调 `businessTypeUtil` 和数据源能力，不适合盲生成

#### 4.2.2 `POST /athena-designer/inquiry/dataset/edit`

- 方法名：`editDataSet`
- 请求体：`DataSet`
- Body 关键字段：
  - `code`
  - `application`
  - `name`
  - `description`
  - `dimensions`
  - `measures`
  - `attributesHash`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`update / chain`
- 建议优先级：`P1`
- 是否依赖真实实体：是
- 前置来源：
  - `create_in_chain`
- 推荐闭环：
  - 数据集主闭环
- 建议缓存字段：
  - `code`
  - 更新前 `name`
  - 更新后 `name`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 更新后 `detail.name` 或分页结果名称已变化
- 风险：
  - 必须是已存在数据集
  - 若 `attributesHash` 变化，会触发额外业务计算

#### 4.2.3 `GET /athena-designer/inquiry/dataset/detail`

- 方法名：`getDetail`
- Query 参数：
  - `code`
- 返回包装：`ResultBean`
- 主要返回路径：`$.data`
- 用例分级：`B`
- 用例类型：`query / detail`
- 建议优先级：`P1`
- 是否依赖真实实体：是
- 前置来源：
  - `create_in_chain` 或 `query_existing`
- 推荐闭环：
  - 数据集查询闭环
- 建议缓存字段：
  - `modelId`
  - `code`
  - `name`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - `$.data.code` 与请求一致
  - `$.data.tableFields` 存在
- 风险：
  - service 内部还会调用 `dataSourceService.getModelDetail`
  - 真实模型缺失时可能失败

#### 4.2.4 `POST /athena-designer/inquiry/dataset/getPageList`

- 方法名：`getPageList`
- 请求体：`DataSetReq`
- Body 关键字段：
  - `application`
  - `keyword`
  - `needFilter`
  - `pageNum`
  - `pageSize`
- 返回包装：`ResultBean`
- 主要返回路径：`$.data.list`
- 用例分级：`A`
- 用例类型：`query`
- 建议优先级：`P1`
- 是否依赖真实实体：否
- 推荐闭环：
  - 数据集查询闭环
- 建议缓存字段：
  - 首条 `code`
  - 首条 `name`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 当传有效 `application` 时返回结构正确
  - 若列表非空，首条包含 `code/name/status`
- 风险：
  - `application` 为空时 service 会直接返回空分页，不适合做非空断言

#### 4.2.5 `GET /athena-designer/inquiry/dataset/allDatasets`

- 方法名：`allDatasets`
- Query 参数：
  - `application`
- 返回包装：`ResultBean`
- 主要返回路径：`$.data`
- 用例分级：`A`
- 用例类型：`query`
- 建议优先级：`P1`
- 是否依赖真实实体：否
- 推荐闭环：
  - 数据集查询闭环
- 建议缓存字段：
  - 首条 `code`
  - 首条 `name`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 列表元素包含 `code/name`
- 风险：
  - `application` 为空时返回空列表

#### 4.2.6 `POST /athena-designer/inquiry/dataset/delete`

- 方法名：`deleteDataSet`
- 请求体：`DataSetDeleteReq`
- Body 关键字段：
  - `application`
  - `codes`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`delete / chain`
- 建议优先级：`P1`
- 是否依赖真实实体：是
- 前置来源：
  - `create_in_chain`
- 推荐闭环：
  - 数据集主闭环
- 建议缓存字段：
  - `code`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 删除后分页查询不再出现该 `code`
- 风险：
  - 被知识库引用或存在隐式关联时会删除失败

#### 4.2.7 `POST /athena-designer/inquiry/dataset/updateStatus`

- 方法名：`updateStatus`
- 请求体：`UpdateStatusDto`
- Body 关键字段：
  - `code`
  - `status`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`update / chain`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - `create_in_chain` 或 `query_existing`
- 推荐闭环：
  - 数据集状态切换闭环
- 建议缓存字段：
  - `code`
  - 原始 `status`
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 修改后分页查询里的 `status` 同步变化
- 风险：
  - 停用时会做关联校验，可能被引用后无法停用

#### 4.2.8 `POST /athena-designer/inquiry/dataset/parseExcel`

- 方法名：`parseExcel`
- 请求体：`MultipartFile file`
- 返回包装：`ResultBean`
- 用例分级：`C`
- 用例类型：`import`
- 建议优先级：`P3`
- 是否依赖真实实体：是
- 前置来源：
  - 真实上传文件
- 暂不生成原因：
  - 文件上传 + 大量 Excel/CSV 解析逻辑 + 环境文件约束
- 风险：
  - 文件大小限制
  - sheet 数限制
  - 文件内容为空直接失败

#### 4.2.9 `POST /athena-designer/inquiry/dataset/addFromExcel`

- 方法名：`addFromExcel`
- 请求体：`ExcelParseInfo`
- Body 关键字段：
  - `fileId`
  - `fileType`
  - `dataSourceId`
  - `dataSourceName`
  - `application`
  - `details`
- 返回包装：`ResultBean`
- 用例分级：`C`
- 用例类型：`import / chain`
- 建议优先级：`P3`
- 是否依赖真实实体：是
- 前置来源：
  - `parseExcel`
  - 文件中心
  - 真实数据源
- 暂不生成原因：
  - 异步导入、多线程、文件中心、建表等依赖过强

#### 4.2.10 `POST /athena-designer/inquiry/dataset/queryProcess`

- 方法名：`queryProcess`
- 请求体：`QueryProcessRequest`
- Body 关键字段：
  - `application`
  - `codeList`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`query / async-check`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - `addFromExcel` 异步链路
- 推荐闭环：
  - Excel 导入闭环的进度查询节点
- 暂不生成原因：
  - 如果不做 Excel 导入链路，单独执行业务价值有限

### 4.3 DataSourceController

类映射：

- `/inquiry/datasource`

适合度结论：

- 该 Controller 以查询为主
- 但强依赖外部数据源平台接口：`dmpApiHelper` / `dcdpApiHelper`
- 适合做第二批或专项环境验证后的稳定集

#### 4.3.1 `POST /athena-designer/inquiry/datasource/getList`

- 方法名：`getList`
- 请求体：`DataSourceListReq`
- Body 关键字段：
  - `dataSourceTypeList`
  - `dataSourceName`
  - `dataSourceId`
  - `businessType`
  - `pageNum`
  - `pageSize`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`query`
- 建议优先级：`P2`
- 是否依赖真实实体：否，但依赖真实外部服务
- 推荐闭环：
  - 数据源查询闭环
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 返回结构中存在 `totalList`
  - 列表元素包含 `dataSourceId/name/type`
- 风险：
  - 强依赖环境中的数据源服务

#### 4.3.2 `POST /athena-designer/inquiry/datasource/getModels`

- 方法名：`getModels`
- 请求体：`DataSourceListReq`
- Body 关键字段：
  - `dataSourceId`
  - `pageNum`
  - `pageSize`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`query`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - `getList` 返回的 `dataSourceId`
- 推荐闭环：
  - 数据源查询闭环
- 建议缓存字段：
  - `dataSourceId`
  - 首条 `id`
- 风险：
  - 没有稳定数据源时无法保证非空

#### 4.3.3 `GET /athena-designer/inquiry/datasource/getModelDetail`

- 方法名：`getModelDetail`
- Query 参数：
  - `id`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`detail`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - `getModels` 首条 `id`
- 建议缓存字段：
  - `id`
  - `modelCode`
- 风险：
  - 强依赖外部元数据服务

#### 4.3.4 `GET /athena-designer/inquiry/datasource/getDataSourceTypes`

- 方法名：`getDataSourceTypes`
- 请求参数：无
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`query`
- 建议优先级：`P2`
- 是否依赖真实实体：否，但依赖真实外部服务
- 推荐闭环：
  - 数据源查询闭环起点
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 返回集合存在或至少结构正确

#### 4.3.5 `POST /athena-designer/inquiry/datasource/getTables`

- 方法名：`getTables`
- 请求体：`DataSourceListReq`
- Body 关键字段：
  - `dataSourceId`
  - `pageNum`
  - `pageSize`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`query`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - `getList` 返回的 `dataSourceId`
- 推荐闭环：
  - 数据源查询闭环

#### 4.3.6 `GET /athena-designer/inquiry/datasource/getTableDetail`

- 方法名：`getTableDetail`
- Query 参数：
  - `id`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`detail`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - `getTables` 首条 `id`
- 风险：
  - 表 id 必须来自真实环境

### 4.4 ImplicitAssociationController

类映射：

- `/inquiry/association`

适合度结论：

- `query` 可做查询型接口
- `save` 和 `delete` 都强依赖真实应用及数据集关系
- 更适合在“数据集已稳定存在”的条件下补链路

#### 4.4.1 `POST /athena-designer/inquiry/association/save`

- 方法名：`saveAssociation`
- 请求体：`ImplicitAssociation`
- Body 关键字段：
  - `application`
  - `graphData`
  - `relations`
- 返回包装：`ResultBean`
- 用例分级：`C`
- 用例类型：`create / update / chain`
- 建议优先级：`P3`
- 是否依赖真实实体：是
- 前置来源：
  - 真实数据集编码、字段、关联关系
- 暂不生成原因：
  - `relations/on/conditions` 结构复杂，不能只猜字段形状

#### 4.4.2 `GET /athena-designer/inquiry/association/query`

- 方法名：`queryImplicitAssociation`
- Query 参数：
  - `application`
- 返回包装：`ResultBean`
- 用例分级：`A`
- 用例类型：`query`
- 建议优先级：`P1`
- 是否依赖真实实体：否
- 推荐闭环：
  - 隐式关联查询闭环
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 返回结构存在，允许为空对象
- 风险：
  - 若环境未配置关联，适合做结构断言，不适合做非空断言

#### 4.4.3 `POST /athena-designer/inquiry/association/fieldCheck`

- 方法名：`fieldCheck`
- 请求体：`FieldCheckDto`
- Body 关键字段：
  - `application`
  - `code`
  - `fields`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`query / validation`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - 已存在数据集编码和字段
- 风险：
  - 需要真实 `code.field` 才能体现业务意义

#### 4.4.4 `GET /athena-designer/inquiry/association/delete`

- 方法名：`delete`
- Query 参数：
  - `application`
- 返回包装：`ResultBean`
- 用例分级：`B`
- 用例类型：`delete / chain`
- 建议优先级：`P2`
- 是否依赖真实实体：是
- 前置来源：
  - 先 `saveAssociation`
- 风险：
  - 单独执行删除容易成为空删，建议只放在完整链路里

### 4.5 CommonController

类映射：

- `/inquiry/common`

适合度结论：

- 包含下载、导入、鉴权模块查询、登录辅助接口
- 类型混杂，不适合整体打包进首批稳定集

#### 4.5.1 `GET /athena-designer/inquiry/common/downTemplate`

- 方法名：`downTemplate`
- Query 参数：
  - `type`
- 返回类型：文件流
- 用例分级：`C`
- 用例类型：`export / download`
- 建议优先级：`P3`
- 暂不生成原因：
  - 下载类接口适合单独模板处理，不放进首批通用 JSON 断言集

#### 4.5.2 `GET /athena-designer/inquiry/common/exportV2`

- 方法名：`exportV2`
- Query 参数：
  - `type`
  - `application`
- 返回类型：文件流
- 用例分级：`C`
- 用例类型：`export / download`
- 建议优先级：`P3`
- 暂不生成原因：
  - 文件流下载 + 真实业务数据依赖

#### 4.5.3 `POST /athena-designer/inquiry/common/import`

- 方法名：`importV2`
- 请求类型：
  - `List<MultipartFile> files`
  - `application`
  - `type`
- 返回包装：`ResultBean`
- 用例分级：`C`
- 用例类型：`import`
- 建议优先级：`P3`
- 暂不生成原因：
  - 多文件上传 + 业务导入 + 错误文件处理

#### 4.5.4 `GET /athena-designer/inquiry/common/downloadError`

- 方法名：`downloadError`
- Query 参数：
  - `fileId`
- 返回类型：文件流
- 用例分级：`C`
- 用例类型：`download`
- 建议优先级：`P3`
- 暂不生成原因：
  - 依赖文件中心中的真实错误文件

#### 4.5.5 `GET /athena-designer/inquiry/common/authModules`

- 方法名：`authModules`
- Query 参数：
  - `appType`
  - `appSystem` 可选
- 返回包装：
  - `ResultDto<JSONArray>`
- 主要返回路径：
  - `$.code`
  - `$.data`
- 用例分级：`B`
- 用例类型：`query`
- 建议优先级：`P1`
- 是否依赖真实实体：否，但依赖 CAC 授权服务
- 推荐闭环：
  - 模块授权查询单点用例
- 基础断言：
  - `$.code == 0`
- 业务断言建议：
  - 返回项包含 `id/name`
- 风险：
  - 返回包装不是 `ResultBean`，后续生成 YAML 时要注意断言路径
  - `appType/appSystem` 组合影响结果

#### 4.5.6 `POST /athena-designer/inquiry/common/mcpLogin`

- 方法名：`mcpLogin`
- 请求体：
  - `JSONObject`
- Body 关键字段：
  - `userId`
  - `password`
  - `deviceId`
- 返回包装：
  - `ResultDto<String>`
- 用例分级：`C`
- 用例类型：`login / helper`
- 建议优先级：`P3`
- 是否需要认证：
  - 否，白名单接口
- 暂不生成原因：
  - 依赖真实账号密码，不适合进入通用自动化稳定集

## 5. 推荐机读字段映射

如果后续要为本模块同时生成 JSON 结构化清单，建议最少覆盖这些字段：

- `module`
- `controller`
- `method_name`
- `http_method`
- `url`
- `summary`
- `body_class`
- `body_fields`
- `query_params`
- `auth_required`
- `case_level`
- `case_type`
- `business_domain`
- `priority`
- `requires_existing_entity`
- `precondition_source`
- `recommended_chain`
- `cache_fields`
- `base_assertions`
- `business_assertions`
- `skip_reason`

## 6. 本模块后续生成顺序建议

建议后续从本模块生成 YAML 时按以下顺序推进：

1. `knowledge/getPageList`
2. `knowledge/getList`
3. `knowledge/createOrUpdate`
4. `knowledge/batchDelete`
5. `dataset/getPageList`
6. `dataset/allDatasets`
7. `dataset/detail`
8. `common/authModules`
9. `datasource/getDataSourceTypes`
10. `datasource/getList`

说明：

- 先做 `knowledge`，最容易形成闭环
- 再做 `dataset` 查询，风险可控
- `datasource` 和 `authModules` 放在环境验证后补
- 文件与导入导出接口最后处理

## 7. 当前结论

`agiledatainquiry` 适合作为“后端接口 -> 接口用例文档 -> YAML”链路的首个试点模块。

其中：

- 最优先的稳定闭环是 `knowledge`
- 最优先的稳定查询是 `dataset`
- 次优先的是 `authModules` 和 `datasource`
- 暂缓的是导入导出、文件流、Excel、多线程异步相关接口
