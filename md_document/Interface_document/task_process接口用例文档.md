# task_process接口用例文档

更新时间：2026-04-10

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中任务、项目、流程、页面设计、多版本相关 Controller 源码整理，用于作为后续重构 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_task_process.yaml` 的中间设计文档。

本模块当前统一归属建议：

- 业务域：`ai_task_process.yaml`
- 文档来源：Controller 方法签名 + 现有稳定 YAML + 当前环境回归表现

本次重点分析的后端入口包括：

- `com.digiwin.athena.controller.task.TaskController`
- `com.digiwin.athena.controller.task.ProjectController`
- `com.digiwin.athena.controller.process.ProcessController`
- `com.digiwin.athena.controller.pagedesign.DapPageDesignController`
- `com.digiwin.athena.controller.DataGroupHistoryController`

## 2. 模块结论

### 2.1 当前最适合保留的小闭环

`task_process` 当前真正适合先保留为稳定闭环的，不是创建类接口，而是“同一业务对象下的查询闭环”：

1. 任务数据组查询闭环
2. 项目查询闭环
3. 流程查询闭环

原因：

- 当前环境下并没有稳定、低副作用的任务/项目/流程创建入口可直接纳入 AI 稳定集。
- 现有 YAML 大量依赖“列表首条数据”串详情，容易受排序和环境数据变化影响。
- 同一对象内的“列表 -> 详情 / 扩展查询”仍然可以形成轻量小闭环，但前提是不要跨接口强行要求首条记录一致。

### 2.2 当前更适合保留为稳定查询集的接口

推荐保留为稳定查询，不强行串详情或闭环：

- `GET /athena-designer/task/application`
- `GET /athena-designer/task/project`
- `GET /athena-designer/task/pageViewTree`
- `GET /athena-designer/task/taskTree`
- `GET /athena-designer/task/queryOutputStates`
- `GET /athena-designer/task/endState/{taskCode}`
- `GET /athena-designer/project/projectList/{application}`
- `GET /athena-designer/project/projects`
- `POST /athena-designer/project/v2/queryProjectList`
- `GET /athena-designer/project/projectTree/{application}`
- `GET /athena-designer/project/getRootProjects/{appCode}`
- `GET /athena-designer/process/findProcessCountByTriggerType`
- `GET /athena-designer/process/findProcessPagination`
- `GET /athena-designer/process/findProcessList`
- `GET /athena-designer/process/queryWaitingNodes`
- `GET /athena-designer/pageDesign/queryByApplication`
- `GET /athena-designer/pageDesign/queryByCode`
- `GET /athena-designer/pageDesign/queryDataSourcesByCode`
- `GET /athena-designer/pageDesign/getActionIdByCode`
- `GET /athena-designer/pageDesign/assignNameCheck`
- `GET /athena-designer/groupHistory/findAppEffectAdpVersion`
- `GET /athena-designer/groupHistory/queryList`
- `GET /athena-designer/groupHistory/getDataGroupHistory`

### 2.3 当前建议退出稳定闭环，只保留探测属性的接口

以下接口暂不建议默认进入稳定集：

- `GET /athena-designer/task/getTaskAndDataStateByApplicationAndSkillCode`
- `GET /athena-designer/task/queryAssistTaskFlowInfo`
- `GET /athena-designer/task/getMainLine`
- `GET /athena-designer/process/findApprovalsButtonByConditionId`
- `GET /athena-designer/process/findFiledByModelCode`
- `POST /athena-designer/process/findModelByCode`
- `GET /athena-designer/pageDesign/espProduct/{application}`

原因：

- 依赖技能编码、审批条件、模型服务编码、外部 ESP 注册信息等环境种子。
- 部分接口当前环境下会出现空数据、精简对象，甚至 `NullPointerException`。
- 不适合用来构造 AI 稳定闭环的第一批。

## 3. 推荐小闭环

### 3.1 任务数据组查询闭环

闭环目标：先在当前应用下定位一个稳定数据组，再围绕该数据组查询任务、数据、画布和历史版本，形成“同对象多接口查询闭环”。

推荐顺序：

1. `GET /athena-designer/groupHistory/queryList`
2. `GET /athena-designer/task/getTaskList`
3. `GET /athena-designer/task/getDataList`
4. `GET /athena-designer/task/getDtdCanvas`
5. `GET /athena-designer/groupHistory/getDataGroupHistory`

关键规则：

- 数据组 code 必须来自真实列表查询，不允许伪造。
- 不要求首条数据组在所有接口中都排第一，只要求“有命中且结构有效”。
- `getDtdCanvas` 只校验结果对象存在，不校验复杂节点内容。

建议缓存：

- `task_process_group_code`

建议断言：

- `$.code == 0`
- 列表接口只校验 `$.data != null` 或 `len_gt 0`
- 详情接口只校验对象存在，不跨接口比较首条元素

### 3.2 项目查询闭环

闭环目标：在当前应用下定位一个真实项目，围绕该项目做列表、简表、详情、树结构查询。

推荐顺序：

1. `GET /athena-designer/project/projectList/{application}`
2. `GET /athena-designer/project/projects`
3. `GET /athena-designer/project/getProject/{code}`
4. `GET /athena-designer/project/projectTree/{application}`

关键源码结论：

- `projectList`、`projects` 都来自 `ProjectController`，但底层查询入口不同，不能假设两者首条记录一致。
- `getProject/{code}` 适合消费真实缓存的 `project code`，而不是消费另一个接口首条排序结果。

建议缓存：

- `task_process_project_code`

建议断言：

- `projectList`：首条 code/name 非空
- `projects`：列表非空、首条 code 非空，不比较与 `projectList` 首条一致
- `getProject`：`$.data.code == $cache{task_process_project_code}`
- `projectTree`：根结构存在

### 3.3 流程查询闭环

闭环目标：在当前应用下定位一个真实流程，再查询流程详情和分页结果。

推荐顺序：

1. `GET /athena-designer/process/findProcessPagination`
2. `GET /athena-designer/process/findProcessById`
3. `GET /athena-designer/process/findProcessList`

关键规则：

- `processId` 必须来自同一次分页查询缓存。
- `findProcessList` 更适合做补充查询，不适合反过来约束分页首条。
- `findProcessCountByTriggerType` 只适合作为聚合查询，不适合用来断言流程列表细节。

建议缓存：

- `task_process_process_id`

建议断言：

- 分页结果对象存在
- `findProcessById` 返回对象存在
- `findProcessList` 返回对象非空或非 null

## 4. pageDesign 与 groupHistory 的处理建议

### 4.1 pageDesign

当前更适合作为“从真实页面 code 出发”的补充查询，不适合自己充当闭环起点。

原因：

- `queryByApplication` 返回的是页面列表，但当前环境可能返回精简对象。
- `queryByCode`、`queryDataSourcesByCode`、`getActionIdByCode` 都更依赖页面 code 作为已知种子。
- 如果种子来自“列表首条页面”，就会重新落回环境排序依赖。

建议：

- 只有在前置闭环已经拿到稳定页面 code 时，再挂：
  - `GET /athena-designer/pageDesign/queryByCode`
  - `GET /athena-designer/pageDesign/queryDataSourcesByCode`
  - `GET /athena-designer/pageDesign/getActionIdByCode`
- `assignNameCheck` 可作为独立单点查询，不应反向约束页面详情。

### 4.2 groupHistory

`groupHistory` 是当前模块最适合作为真实种子来源的入口之一。

关键源码结论：

- `findAppEffectAdpVersion` 可以作为应用维度的稳定状态查询。
- `queryList` 按应用查询多版本列表，但当前控制层并不真正消费 `code` 入参，因此不适合把请求里的 `code` 当严格筛选条件。
- `getDataGroupHistory` 则适合基于真实 code 拉详情。

建议：

- `findAppEffectAdpVersion` 作为稳定单点查询保留。
- `queryList -> getDataGroupHistory` 适合作为历史数据组轻量闭环。

## 5. 对现有 ai_task_process.yaml 的修正方向

当前文档对应的核心修正原则：

1. 不再使用“跨接口首条记录相等”作为断言。
2. 不再把“当前环境空列表”写成正式业务契约。
3. 已知可能返回 `NullPointerException` 的接口退出稳定集。
4. 详情接口必须消费同一闭环中真实缓存的 id/code。
5. 没有稳定种子的页面、模型、审批条件类接口，转为探测集。

## 6. 接口分类建议

### 6.1 A 类：优先保留并重构进稳定集

- `GET /athena-designer/project/projectList/{application}`
- `GET /athena-designer/project/projects`
- `GET /athena-designer/project/getProject/{code}`
- `GET /athena-designer/groupHistory/queryList`
- `GET /athena-designer/groupHistory/getDataGroupHistory`
- `GET /athena-designer/task/getTaskList`
- `GET /athena-designer/task/getDataList`
- `GET /athena-designer/task/getDtdCanvas`
- `GET /athena-designer/process/findProcessPagination`
- `GET /athena-designer/process/findProcessById`

### 6.2 B 类：稳定查询保留，但不强行闭环

- `GET /athena-designer/task/application`
- `GET /athena-designer/task/project`
- `GET /athena-designer/task/pageViewTree`
- `GET /athena-designer/task/taskTree`
- `GET /athena-designer/task/queryOutputStates`
- `GET /athena-designer/task/endState/{taskCode}`
- `GET /athena-designer/project/projectTree/{application}`
- `GET /athena-designer/project/getRootProjects/{appCode}`
- `GET /athena-designer/process/findProcessCountByTriggerType`
- `GET /athena-designer/process/findProcessList`
- `GET /athena-designer/pageDesign/queryByApplication`
- `GET /athena-designer/pageDesign/assignNameCheck`
- `GET /athena-designer/groupHistory/findAppEffectAdpVersion`

### 6.3 C 类：探测集或暂缓

- `GET /athena-designer/task/getTaskAndDataStateByApplicationAndSkillCode`
- `GET /athena-designer/task/queryAssistTaskFlowInfo`
- `GET /athena-designer/task/getMainLine`
- `GET /athena-designer/process/findApprovalsButtonByConditionId`
- `GET /athena-designer/process/findFiledByModelCode`
- `POST /athena-designer/process/findModelByCode`
- `GET /athena-designer/pageDesign/queryByCode`
- `GET /athena-designer/pageDesign/queryDataSourcesByCode`
- `GET /athena-designer/pageDesign/getActionIdByCode`
- `GET /athena-designer/pageDesign/espProduct/{application}`

## 7. 后续 YAML 落地建议

后续重构 `ai_task_process.yaml` 时，建议按下面顺序推进：

1. 先重构“项目查询闭环”
2. 再重构“数据组查询闭环”
3. 最后清理“流程查询闭环”

不建议一开始就碰：

- 页面详情链
- 模型字段链
- 审批按钮链
- 技能码相关链

因为这些链路最容易因为环境差异重新把稳定集拖回失败状态。
