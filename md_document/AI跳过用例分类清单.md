# AI跳过用例分类清单

更新时间：2026-04-13

## 1. 目标

本清单用于处理 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai` 下大量 `is_run: false` 的 AI 用例，统一回答 3 个问题：

- 这些跳过用例为什么跳过
- 哪些跳过用例仍有实际意义
- 后续哪些应该保留，哪些应该回收成小闭环，哪些应该直接清理

当前原则：

- 稳定回归集优先
- 覆盖率探测集允许保留，但必须有边界
- 历史遗留的无效跳过项要逐步清掉

## 2. 当前现状

`data/ai` 当前显式 `is_run: false` 数量如下：

- `ai_activity_message.yaml`：`86`
- `ai_application.yaml`：`33`
- `ai_base_support.yaml`：`29`
- `ai_inquiry.yaml`：`5`
- `ai_task_process.yaml`：`55`

合计：`208`

说明：

- 这些不是 pytest 随机跳过
- 这些是 [conftest.py](D:\sort\AthenaDesigner-ApiAutoTest\test_case\conftest.py) 中 `case_skip` 固定按 `is_run: false` 执行 `pytest.skip()`
- 因此它们本质上是“人工定义的不进稳定集的用例”

## 3. 分类规则

后续所有跳过用例统一分为 3 类。

### 3.1 保留探测集

定义：

- 当前主要用于扩大唯一 `method + url` 覆盖面
- 还不适合进入稳定回归集
- 但短期内仍有覆盖率价值

典型特征：

- `detail` 中明确写了“先纳入覆盖集合”“当前保留为探测集”
- 依赖真实业务对象、外部同步、发布态、重请求体 DTO
- 当前还没有稳定前置闭环

处理策略：

- 保留 `is_run: false`
- 明确保留原因
- 后续有真实种子后，再择机回收

### 3.2 可回收闭环

定义：

- 当前因为环境数据、种子缺失、列表为空、排序不稳而跳过
- 但本质上可以通过补前置实体或重构链路回收成稳定小闭环

典型特征：

- `detail` 中出现“空列表”“无稳定种子”“排序不稳定”“缺少稳定公开数据”
- 依赖列表首条或环境现成数据
- 一旦补足前置创建链，就可以不跳过

处理策略：

- 优先重构为“新增 -> 查询 -> 删除”或“真实种子 -> 详情 -> 恢复”的小闭环
- 能回收的逐步从 `is_run: false` 改回稳定集

### 3.3 清理候选

定义：

- 既不再提供新的覆盖率价值
- 也没有明确回收路径
- 多数属于历史遗留的脆弱链路或重复探测项

典型特征：

- 依赖首条数据强绑定
- 跨接口比较首条记录一致
- 只是旧失败项先临时跳过，但后来一直没处理
- 该接口已被别的 YAML 覆盖，当前这个跳过项不再提供新增价值

处理策略：

- 优先核对该接口是否已在其他 YAML 覆盖
- 已覆盖且无回收价值的，直接移除
- 未覆盖但又无稳定回收路径的，单独收敛为探测集，不再混入老闭环段落

## 4. 各文件结论

### 4.1 `ai_activity_message.yaml`

当前判断：

- 这份文件里的跳过项最多，且混杂最明显
- 一部分是历史遗留的“首条活动 / 首条通知 / 首条事件”链
- 另一部分是最近为了提覆盖率新增的探测集

建议分层：

- 保留探测集：
  - `backendmanage_*`
  - `activity_message_visible_config_*`
  - `assistant_*`
  - `abi_*`
  - `message_notification_send/no_prompt/terminate`
- 可回收闭环：
  - `activity_configs_*`
  - `activity_config_seed_*`
  - `aim_event_*`
  - `aim_scene_*`
  - `message_notification_query_*`
  - `upgrade_notification_*`
- 清理候选：
  - 依赖“首条活动编码”“首条通知编码”的旧链
  - 与现有稳定场景无明显增量关系的旧探测项

主结论：

- `ai_activity_message.yaml` 后续应拆成“稳定活动/消息闭环”和“覆盖率探测集”两块思路
- 不能继续把两类内容混写

### 4.2 `ai_application.yaml`

当前判断：

- 这份文件的大多数跳过项其实不是“无意义跳过”
- 主要是 `workbench / customConfig / individual_case / appInitData` 这类重依赖对象

建议分层：

- 保留探测集：
  - `workbench_add/update/queryByCode/delete`
  - `workbench_portal_*` 中依赖真实 portal id 的项
  - `workbench_component_*` 中依赖真实 component id 的项
  - `workbench_datasource_*` 中依赖真实 datasource id 或真实作业的项
  - `workbench_common_*`
- 可回收闭环：
  - `custom_config_*` 中依赖系统共享列表为空的链
  - `individual_case_*` 中依赖个案应用存在的链
  - `app_init_*` 中依赖初始化 redis uuid 的链
  - `workbench_sso_*` 中依赖真实保存后对象的链
- 清理候选：
  - 已被新 workbench 覆盖策略替代、但仍保留的旧跳过项

主结论：

- `ai_application.yaml` 的跳过项大多有回收价值
- 后续应优先把 `workbench` 做成真正的主闭环，而不是长期维持半闭环探测状态

### 4.3 `ai_task_process.yaml`

当前判断：

- 这份文件的跳过项现在有两类很清楚
- 一类是老的页面设计/流程详情脆弱链
- 一类是最近补覆盖率时新增的 `task_process_*` 探测集

建议分层：

- 保留探测集：
  - `task_process_project_*`
  - `task_process_tenant_*`
  - `task_process_pagedesign_*`
  - `task_process_mobile_page_*`
  - `task_process_mechanism_*`
  - `task_process_data_*`
  - `task_process_build_data_*`
- 可回收闭环：
  - `page_design_*`
  - `process_find_*`
  - `process_version_*`
  - `task_query_assist_task_flow_info_*`
  - `task_get_task_and_data_state_by_skill_code_*`
- 清理候选：
  - 明确依赖旧首条项目/页面缓存、且已被新主闭环替代的旧 case

主结论：

- `ai_task_process.yaml` 的新跳过项是有意义的，因为它们直接贡献了覆盖率
- 但旧的页面/流程脆弱跳过项需要单独清掉一轮

### 4.4 `ai_base_support.yaml`

当前判断：

- 这份文件的跳过项以老查询链和环境异常为主
- 新增的大闭环已经相对干净，遗留问题主要集中在旧字典/动作/后端服务链

建议分层：

- 保留探测集：
  - 当前较少，必要时仅保留明确未覆盖的后端服务探测项
- 可回收闭环：
  - `dictionary_*`
  - `duty_*`
  - `tagDefinition_*`
  - `action_*` 中依赖真实 actionId 的链
  - `model_driver_server_source_*` 中依赖真实发布记录的链
- 清理候选：
  - 已知长期 `NullPointerException` 且短期无修复预期的项
  - 已被新 agiledata 闭环覆盖掉价值的旧查询跳过项

主结论：

- `ai_base_support.yaml` 更适合做“旧 skip 清理”
- 不适合作为下一批主要放量文件

### 4.5 `ai_inquiry.yaml`

当前判断：

- 这份文件已经是最干净的一份
- 剩余跳过项很少，且原因清楚

建议分层：

- 保留探测集：
  - 无需新增
- 可回收闭环：
  - `favourite_query_activity_*`
  - `favourite_get_dtd_*`
- 清理候选：
  - 无明显优先项

主结论：

- `ai_inquiry.yaml` 不需要优先清理
- 等环境有稳定收藏种子后直接回收即可

## 5. 为什么现在 skip 看起来很多

核心原因不是“这些 case 都没用”，而是当前把两层东西放在了一起：

- 稳定回归层
- 覆盖率探测层

最近几轮为了在不破坏稳定性的前提下尽快提高覆盖率，我们新增了很多探测集 case，它们本来就不应该进入稳定门禁，因此自然会推高 `skip` 数。

问题不在于“有 skip”，而在于：

- 探测集没有独立标识层
- 旧历史跳过项没有及时清理
- 可回收闭环还没有被系统性回收

## 6. 后续执行顺序

后续建议按以下顺序处理。

1. 先保留真正有覆盖价值的探测集
2. 再回收“明确可补成小闭环”的跳过项
3. 最后清理无增量价值的旧 skip

按文件优先级建议：

1. `ai_activity_message.yaml`
2. `ai_task_process.yaml`
3. `ai_application.yaml`
4. `ai_base_support.yaml`
5. `ai_inquiry.yaml`

## 7. 实操标准

后续每个跳过项都按以下标准判断：

- 这个接口是否仍然贡献新增唯一覆盖率
- 这个接口是否能通过补前置实体回收成小闭环
- 这个接口是否只是历史遗留的旧失败项

判定规则：

- 能贡献新增覆盖率：保留为探测集
- 能补前置实体回收：进入回收计划
- 两者都不是：进入清理候选

## 8. 下一步建议

下一步不要同时做三件事，而是按顺序来：

1. 先处理 [ai_activity_message.yaml](D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_activity_message.yaml)
2. 把它的 `86` 条跳过项分成：
   - 保留探测集
   - 可回收闭环
   - 直接清理
3. 清完再处理 [ai_task_process.yaml](D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_task_process.yaml)

这样做的目标不是把 `skip` 立刻砍到最低，而是让每一条 `skip` 都有明确存在理由。
