# workbench接口用例文档

更新时间：2026-04-10

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 `workbench` 相关 Controller 源码整理，用于作为后续生成 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai` 下 YAML 用例的中间设计文档。

本次目标不是补几个零散查询，而是一次性整理一个 `20+` 有效接口的大模块文档。  
`workbench` 模块适合这样做，因为它天然可以拆成多个并行闭环：

1. 应用与自定义配置闭环
2. 自定义组件闭环
3. 门户闭环
4. 数据源闭环
5. SSO 应用闭环
6. 公共发布与同步补充链

同一个查询接口允许在多个闭环中复用，不需要为了“去重”牺牲闭环稳定性。

当前建议归属：

- 业务域：`ai_application.yaml`
- 文档来源：`controller/workbench/*Controller.java`

本次重点分析的后端入口包括：

- `com.digiwin.athena.controller.workbench.WorkbenchAppController`
- `com.digiwin.athena.controller.workbench.WorkbenchComponentController`
- `com.digiwin.athena.controller.workbench.WorkbenchPortalController`
- `com.digiwin.athena.controller.workbench.WorkbenchDataSourceController`
- `com.digiwin.athena.controller.workbench.WorkbenchSSOApplicationController`
- `com.digiwin.athena.controller.workbench.WorkbenchCommonController`

## 2. 模块结论

### 2.1 本次有效接口目标

本模块当前可以一次性整理出 `29` 个适合优先进入自动化设计视野的接口，其中：

- A 类主闭环接口：`21`
- B 类补充查询/状态流转接口：`6`
- C 类探测或专项接口：`2`

这次明显比之前的小步推进更适合直接提升后续有效覆盖数。

### 2.2 当前最适合优先生成 YAML 的闭环

建议优先顺序：

1. `work-bench/app` 应用与自定义配置闭环
2. `work-bench/component` 自定义组件闭环
3. `work-bench/portal` 门户闭环
4. `workbench/sso` SSO 应用闭环
5. `workbench/datasource` 数据源闭环

`workbench/common` 当前更适合作为补充链，不建议首批直接作为主闭环起点。

## 3. 推荐业务闭环

### 3.1 主闭环 A：应用与自定义配置闭环

闭环目标：基于工作台应用查询能力，补一个“查询配置 -> 保存配置 -> 再查 -> 删除”的小闭环。

推荐顺序：

1. `POST /athena-designer/work-bench/app/get`
2. `POST /athena-designer/work-bench/app/custom-setting`
3. `POST /athena-designer/work-bench/app/custom-setting/save`
4. `POST /athena-designer/work-bench/app/custom-setting`
5. `DELETE /athena-designer/work-bench/app/custom-setting/delete/{id}`

关键规则：

- `app/get` 更适合作为应用种子查询，不适合拿首条记录反向约束所有后续接口
- `custom-setting/save` 应缓存返回的配置 id
- 删除必须消费同闭环返回的真实 id

建议缓存：

- `workbench_app_code`
- `workbench_custom_setting_id`

### 3.2 主闭环 B：自定义组件闭环

闭环目标：新增或更新一个工作台自定义组件，完成分页、详情、列表、菜单列表和删除。

推荐顺序：

1. `POST /athena-designer/work-bench/component/pageQuery`
2. `POST /athena-designer/work-bench/component/save`
3. `POST /athena-designer/work-bench/component/detail`
4. `POST /athena-designer/work-bench/component/queryComponents`
5. `POST /athena-designer/work-bench/component/menu/queryComponents`
6. `POST /athena-designer/work-bench/component/batchDelete`

可选补充：

7. `POST /athena-designer/work-bench/component/initialisePCPreComponent`
8. `POST /athena-designer/work-bench/component/initialiseMobilePreComponent`

关键规则：

- `save` 是新增和更新合并口，首批建议只做新增型最小请求体
- `detail` 和 `batchDelete` 必须消费同闭环真实 id
- 两个 initialise 接口不建议纳入稳定集，只作为工具专项

建议缓存：

- `workbench_component_id`
- `workbench_component_name`

### 3.3 主闭环 C：门户闭环

闭环目标：创建工作台门户，验证详情、菜单名校验、发布/草稿切换、复制、删除等完整流转。

推荐顺序：

1. `POST /athena-designer/work-bench/portal/pageQuery`
2. `POST /athena-designer/work-bench/portal/save`
3. `POST /athena-designer/work-bench/portal/getPortalDetail`
4. `POST /athena-designer/work-bench/portal/validMenuTempName`
5. `POST /athena-designer/work-bench/portal/published`
6. `POST /athena-designer/work-bench/portal/asDraft`
7. `POST /athena-designer/work-bench/portal/confirmDraft`
8. `POST /athena-designer/work-bench/portal/copyPortal`
9. `POST /athena-designer/work-bench/portal/batchDelete`

补充查询：

10. `POST /athena-designer/work-bench/portal/relatedApp/queryWorkList`

关键规则：

- 这是 `workbench` 最完整的一条业务状态闭环
- `published -> asDraft -> confirmDraft` 很适合作为状态流转链
- `copyPortal` 建议放在删除前，避免复制源被提前清理

建议缓存：

- `workbench_portal_id`
- `workbench_portal_name`

### 3.4 主闭环 D：SSO 应用闭环

闭环目标：校验 SSO 应用的重复校验、保存、列表、详情、删除。

推荐顺序：

1. `POST /athena-designer/workbench/sso/validAppCode`
2. `POST /athena-designer/workbench/sso/save`
3. `POST /athena-designer/workbench/sso/queryAll`
4. `POST /athena-designer/workbench/sso/detail`
5. `DELETE /athena-designer/workbench/sso/delete/{id}`

关键规则：

- `validAppCode` 适合作为保存前探针
- `save` 与 `delete` 共同构成稳定可逆闭环
- `detail` 应消费当前闭环对象，而不是任意 appCode

建议缓存：

- `workbench_sso_id`
- `workbench_sso_app_code`

### 3.5 主闭环 E：数据源闭环

闭环目标：创建工作台数据源，并围绕应用、作业、统计配置、分页查询和删除组织闭环。

推荐顺序：

1. `POST /athena-designer/workbench/datasource/queryAppListForDataSource`
2. `POST /athena-designer/workbench/datasource/queryAppJobList`
3. `POST /athena-designer/workbench/datasource/pageQueryAppJobList`
4. `POST /athena-designer/workbench/datasource/save`
5. `POST /athena-designer/workbench/datasource/pageQuery`
6. `POST /athena-designer/workbench/datasource/count/queryCountConfigList`
7. `POST /athena-designer/workbench/datasource/queryAppListForCountJob`
8. `DELETE /athena-designer/workbench/datasource/delete`

关键规则：

- 这条链不建议从 `pageQuery` 开始，而应先拿应用和作业列表作为真实前置
- `save` 与 `delete` 都需要真实数据源对象
- `queryCountConfigList` 更适合作为创建后的补充查询

建议缓存：

- `workbench_datasource_id`
- `workbench_datasource_name`
- `workbench_datasource_app_code`

### 3.6 补充链 F：公共发布与同步链

当前只建议保留为补充链，不建议第一批直接纳入稳定集。

相关接口：

1. `POST /athena-designer/workbench/common/updateWorkbenchPublished`
2. `POST /athena-designer/workbench/common/dataSync/jobSync`

原因：

- `updateWorkbenchPublished` 依赖门户、数据源、SSO、组件等多类对象已有发布数据
- `jobSync` 依赖 AES 解密后的外部同步数据，不适合直接硬生成

## 4. 接口分类建议

### 4.1 A 类：优先进入稳定闭环

- `POST /athena-designer/work-bench/app/get`
- `POST /athena-designer/work-bench/app/custom-setting`
- `POST /athena-designer/work-bench/app/custom-setting/save`
- `DELETE /athena-designer/work-bench/app/custom-setting/delete/{id}`
- `POST /athena-designer/work-bench/component/pageQuery`
- `POST /athena-designer/work-bench/component/save`
- `POST /athena-designer/work-bench/component/detail`
- `POST /athena-designer/work-bench/component/queryComponents`
- `POST /athena-designer/work-bench/component/menu/queryComponents`
- `POST /athena-designer/work-bench/component/batchDelete`
- `POST /athena-designer/work-bench/portal/pageQuery`
- `POST /athena-designer/work-bench/portal/save`
- `POST /athena-designer/work-bench/portal/getPortalDetail`
- `POST /athena-designer/work-bench/portal/validMenuTempName`
- `POST /athena-designer/work-bench/portal/published`
- `POST /athena-designer/work-bench/portal/asDraft`
- `POST /athena-designer/work-bench/portal/confirmDraft`
- `POST /athena-designer/work-bench/portal/copyPortal`
- `POST /athena-designer/work-bench/portal/batchDelete`
- `POST /athena-designer/workbench/sso/validAppCode`
- `POST /athena-designer/workbench/sso/save`
- `POST /athena-designer/workbench/sso/queryAll`
- `POST /athena-designer/workbench/sso/detail`
- `DELETE /athena-designer/workbench/sso/delete/{id}`
- `POST /athena-designer/workbench/datasource/queryAppListForDataSource`
- `POST /athena-designer/workbench/datasource/queryAppJobList`
- `POST /athena-designer/workbench/datasource/pageQueryAppJobList`
- `POST /athena-designer/workbench/datasource/save`
- `POST /athena-designer/workbench/datasource/pageQuery`
- `DELETE /athena-designer/workbench/datasource/delete`

### 4.2 B 类：适合作为补充查询或第二批

- `POST /athena-designer/workbench/datasource/count/queryCountConfigList`
- `POST /athena-designer/workbench/datasource/queryAppListForCountJob`
- `POST /athena-designer/work-bench/portal/relatedApp/queryWorkList`
- `POST /athena-designer/work-bench/component/initialisePCPreComponent`
- `POST /athena-designer/work-bench/component/initialiseMobilePreComponent`
- `POST /athena-designer/workbench/common/updateWorkbenchPublished`

### 4.3 C 类：探测或专项接口

- `POST /athena-designer/workbench/common/dataSync/jobSync`

## 5. YAML 落地建议

建议不要一次把 30 个接口直接平铺进一个链，而是按 5 条主闭环分批写入 `ai_application.yaml`：

1. 应用与自定义配置闭环
2. 组件闭环
3. 门户闭环
4. SSO 闭环
5. 数据源闭环

推荐优先顺序：

1. `work-bench/app`
2. `workbench/sso`
3. `work-bench/portal`
4. `workbench/datasource`
5. `work-bench/component`

这样一轮就能带来明显高于之前的小步增量。

## 6. 下一步建议

如果目标是“这次明显提高有效接口数”，后续最值得直接落 YAML 的就是这份 `workbench` 文档。  
它已经整理出 `20+` 个可优先实现接口，而且大多数都不需要依赖后端特别深的业务对象链。
