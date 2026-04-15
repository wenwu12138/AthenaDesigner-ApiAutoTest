# application接口用例文档

更新时间：2026-04-10

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 application 相关 Controller 源码整理，用于作为后续生成 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_application.yaml` 的中间设计文档。

本模块当前统一归属建议：

- 业务域：`ai_application.yaml`
- 文档来源：Controller 方法签名 + DTO/Domain 结构 + Service 实际逻辑 + 现有稳定 YAML

当前主要分析的后端入口包括：

- `com.digiwin.athena.controller.application.ApplicationParamController`
- `com.digiwin.athena.controller.application.AppInitDataController`
- `com.digiwin.athena.controller.application.ActivityVisibleConfigController`
- `com.digiwin.athena.controller.application.OpenWindowDefinitionController`
- `com.digiwin.athena.controller.application.TenantApplicationController`

## 2. 模块结论

### 2.1 当前最适合先补的小闭环

优先建议先做成 AI 稳定集的小闭环：

1. `applicationParam` 基础参数闭环
2. `guide/skipSet + guide/isSkip` 状态闭环

原因：

- `applicationParam` 具备明确的保存、查询、删除入口，且现有仓库已有真实请求样例可以复用。
- `guide` 接口已经在 `ai_application.yaml` 中稳定运行，适合保留为轻量可逆闭环。

### 2.2 当前更适合保留为稳定查询集的接口

适合保留为稳定查询，不强行串成创建链：

- `GET /athena-designer/application/all`
- `GET /athena-designer/application/appHomePage`
- `GET /athena-designer/application/tenant/queryApplications`
- `POST /athena-designer/application/queryByCodes`
- `POST /athena-designer/application/queryExperienceOverTime`
- `GET /athena-designer/application/queryApplicationHooks`
- `POST /athena-designer/application/query`
- `POST /athena-designer/application/querySolutionCards`
- `POST /athena-designer/application/querySolutionDesigner`
- `POST /athena-designer/application/queryRecentVisit`
- `POST /athena-designer/application/queryRecentCreate`
- `POST /athena-designer/application/queryApplicationLatestCompileInfo`
- `POST /athena-designer/application/queryCompileLog`
- `POST /athena-designer/application/compileLog`
- `GET /athena-designer/application/queryCompileDetail`
- `GET /athena-designer/application/getExampleApp`
- `POST /athena-designer/application/queryApplicationDetail`
- `GET /athena-designer/application/allAppInTenant`
- `GET /athena-designer/application/queryByEnv`
- `GET /athena-designer/application/appCompileData`
- `POST /athena-designer/work-bench/app/get`
- `POST /athena-designer/work-bench/app/custom-setting`
- `POST /athena-designer/work-bench/component/menu/queryComponents`
- `POST /athena-designer/work-bench/component/pageQuery`
- `GET /athena-designer/activityVisibleConfig/{application}`
- `GET /athena-designer/appInitData/getRedisIdByAppCode`

这些接口在当前环境更适合做“结果结构有效”验证，不适合依赖首条记录或环境种子串详情链。

### 2.3 当前建议暂缓进入稳定集的接口

以下接口更适合作为探测集，不建议默认开启：

- `GET /athena-designer/appInitData/getProcessByUuid`
- `POST /athena-designer/appInitData`
- `POST /athena-designer/appInitData/updateProcessByUuid`
- `POST /athena-designer/appInitData/deployPackage`
- `GET /athena-designer/individualCaseApp/getIndividualCaseAppSourceBusinessInfo`
- `GET /athena-designer/customConfig/querySysCustomConfigDetail`
- `GET /athena-designer/customConfig/queryRefAppInfo`
- `GET /athena-designer/customConfig/checkCustomConfigIsRelated`

原因：

- 依赖环境已有 uuid、个案应用、系统级自定义控件种子。
- 部分接口是下载流或初始化类接口，不适合作为 AI 稳定闭环的第一批。

## 3. 推荐闭环

### 3.1 applicationParam 基础参数小闭环

闭环目标：在当前应用下创建一个基础参数，通过 code 查询参数摘要与详情，最后删除该参数，恢复环境。

#### 3.1.1 保存参数

- 接口：`POST /athena-designer/applicationParam/saveParam`
- 作用：创建 `BASE + APPLICATION` 类型参数
- 前置：需要稳定应用 `appCode`
- 请求关键字段：
  - `appCode`
  - `paramCatg = BASE`
  - `sceneCatg = APPLICATION`
  - `value`
- `value` 中至少要包含：
  - `name`
  - `description`
  - `key`
  - `sequence`
  - `required`
  - `readOnly`
  - `displayType`

关键源码结论：

- `ApplicationParamServiceImpl.addParamNameAndCode` 会从 `value` 中提取 `name` 和 `key`，并自动回填为 `paramName`、`paramCode`。
- `saveAppParam` 会校验全局 `paramCode` 唯一。
- 对于 `BASE + APPLICATION` 参数，会联动创建 `GetMechanismVariableAction`。

建议缓存：

- `application_param_ai_code`
- `application_param_ai_name`

建议断言：

- `$.code == 0`

#### 3.1.2 按 code 批量查询参数摘要

- 接口：`POST /athena-designer/applicationParam/getApplicationParamByCodes`
- 作用：根据参数 code 查询显示类型与 options
- 前置来源：新建参数缓存 code

建议断言：

- `$.code == 0`
- `$.data != null`

#### 3.1.3 查询单个参数详情

- 接口：`POST /athena-designer/applicationParam/getParamByCode`
- 作用：查询单个参数详情配置
- 前置来源：新建参数缓存 code

建议断言：

- `$.code == 0`
- `$.data != null`

#### 3.1.4 删除参数

- 接口：`POST /athena-designer/applicationParam/deleteParam`
- 作用：删除当前新建参数并恢复环境
- 前置来源：新建参数缓存 code

关键源码结论：

- `deleteAppParam` 按 `appCode + paramCode` 查询并删除。
- 对于 `BASE + APPLICATION` 参数，会联动清理参数对应的机制变量 action。

建议断言：

- `$.code == 0`

#### 3.1.5 闭环结论

当前结论：

- 这是 `application` 模块最适合继续扩进 `ai_application.yaml` 的真实小闭环。
- 已有仓库样例可直接复用，避免 DTO 猜测。
- 删除接口具备恢复环境能力，符合稳定集要求。

当前默认落地建议：

- 先实现 `save -> getApplicationParamByCodes -> getParamByCode -> delete`
- `updateParam` 暂作为第二批扩展闭环，待首批链路稳定后再补

### 3.2 guide 状态小闭环

当前 YAML 已有稳定链路：

1. `POST /athena-designer/guide/skipSet`
2. `GET /athena-designer/guide/isSkip`

适合作为轻量闭环长期保留，但不再作为扩覆盖的主要方向。

## 4. 接口分类建议

### 4.1 A 类：优先生成并纳入稳定集

- `POST /athena-designer/applicationParam/saveParam`
- `POST /athena-designer/applicationParam/getApplicationParamByCodes`
- `POST /athena-designer/applicationParam/getParamByCode`
- `POST /athena-designer/applicationParam/deleteParam`
- `POST /athena-designer/guide/skipSet`
- `GET /athena-designer/guide/isSkip`

### 4.2 B 类：可保留稳定查询，但不强行串闭环

- `GET /athena-designer/application/all`
- `GET /athena-designer/application/appHomePage`
- `POST /athena-designer/application/queryByCodes`
- `GET /athena-designer/activityVisibleConfig/{application}`
- `GET /athena-designer/appInitData/getRedisIdByAppCode}`
- `POST /athena-designer/work-bench/app/get`
- `POST /athena-designer/work-bench/component/menu/queryComponents`

### 4.3 C 类：暂缓或仅探测

- `GET /athena-designer/appInitData/getProcessByUuid`
- `POST /athena-designer/appInitData`
- `POST /athena-designer/appInitData/updateProcessByUuid`
- `POST /athena-designer/appInitData/deployPackage`
- `GET /athena-designer/customConfig/querySysCustomConfigDetail`
- `GET /athena-designer/customConfig/queryRefAppInfo`
- `GET /athena-designer/customConfig/checkCustomConfigIsRelated`

## 5. YAML 落地建议

建议新增到：

- `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_application.yaml`

建议优先落地的 case 顺序：

1. `application_param_ai_save_001`
2. `application_param_ai_get_by_codes_001`
3. `application_param_ai_get_by_code_001`
4. `application_param_ai_delete_001`

生成要求：

- 使用唯一随机 `key` 作为参数 code
- 删除必须放在闭环末尾，避免污染环境
- 不依赖环境首条参数数据
- 不把空列表假设写成业务契约
