# AI用例生成规范

## 1. 文档定位

这份文档已经合并了原来的“AI用例生成规范”和“AI生成用例说明”。以后只维护这一份，作为：

- AI 生成 YAML 的规则来源
- 当前统一调试集的说明文档
- 每一轮调试后经验回灌的记录入口

旧文档 [`AI生成用例说明.md`](D:/sort/AthenaDesigner-ApiAutoTest/AI生成用例说明.md) 不再单独维护。

## 2. 当前文件组织

`data/ai` 现已按业务域归并为以下 5 个文件：


- [`ai_inquiry.yaml`](D:/sort/AthenaDesigner-ApiAutoTest/data/ai/ai_inquiry.yaml)：洞察、知识库、数据集、词典、收藏等查询闭环
- [`ai_application.yaml`](D:/sort/AthenaDesigner-ApiAutoTest/data/ai/ai_application.yaml)：应用、参数、用户、个例、引导、定制配置闭环
- [`ai_task_process.yaml`](D:/sort/AthenaDesigner-ApiAutoTest/data/ai/ai_task_process.yaml)：项目、流程、任务、版本、资源树、页面设计闭环
- [`ai_activity_message.yaml`](D:/sort/AthenaDesigner-ApiAutoTest/data/ai/ai_activity_message.yaml)：活动、消息、场景、事件、应用分组闭环
- [`ai_base_support.yaml`](D:/sort/AthenaDesigner-ApiAutoTest/data/ai/ai_base_support.yaml)：字典、标签、按钮、预置数据、后台管理等基础支撑闭环

规则：

- 后续新增 AI 用例默认并入以上已有业务域文件，不再按“本次批次”继续新建零散小 YAML
- 只有当出现全新的顶层业务域，且无法合理归入现有 5 类时，才允许新增第 6 个业务域 YAML
- 文件名统一采用 `ai_业务域.yaml` 风格，便于长期维护和后续扩充

## 2.1 当前归并说明

本轮归并后：

- `data/ai` 只保留上述 5 个业务域 YAML
- 原先按单批次沉淀的碎片化 YAML 已从 `data/ai` 移除
- 本轮只重构 YAML 归类，不处理 `test_case/ai/test_*.py`
- 旧生成测试文件由用户手动清理或重建，AI 默认不在本轮归并中处理测试侧

## 3. 标准 YAML 结构

每个用例必须保持以下结构：

```yaml
case_id:
  host: ${{athena_designer_host()}}
  url: /athena-designer/xxx
  method: POST
  detail: 接口场景说明
  headers:
    digi-middleware-auth-user: $cache{token}
    token: $cache{token}
    locale: zh_CN
    content-type: application/json
  requestType: JSON
  is_run: true
  data:
  dependence_case: false
  dependence_case_data:
  assert:
    code:
      jsonpath: $.code
      type: ==
      value: 0
      AssertType:
```

规则：

- `requestType` 必须使用项目已有枚举，如 `JSON`、`PARAMS`
- `is_run` 默认 `true`
- `dependence_case` 固定 `false`
- `detail` 只写场景，不写变量
- `detail`、`name`、`description` 等文案字段必须使用标准 UTF-8 文本，禁止把 `????` 之类占位符写入 YAML 文件
- 每次生成或批量改写后，必须至少扫描 2 类问题：`detail: ?` / `????` 和不可打印控制字符；发现后必须先修复再提交 YAML
- `assert` 第一阶段统一只保留 `$.code == 0`

## 4. 请求头规则

默认保留：

- `digi-middleware-auth-user: $cache{token}`
- `token: $cache{token}`
- `adpversion`
- `adpstatus`
- `locale`
- `content-type`

例外规则：

- 如果后端方法显式要求 `@RequestHeader("Authorization")`，允许补 `Authorization: $cache{token}`
- 头部精简要让位于后端真实签名，不能为追求统一而删掉必需头

## 5. 参数生成规则

### 5.1 应用编码

以下字段优先替换为项目变量：

- `application`
- `appCode`
- 其他明确表示应用编码的字段

统一替换为：

```yaml
${{app2_code()}}
```

### 5.2 名称和描述

新增/更新接口中的 `name`、`description` 等字段，应贴合用例语义并拼接时间后缀：

```yaml
name: AI调试应用更新${{get_time()}}
```

### 5.3 唯一键

`code`、`id`、`actionId` 等唯一字段优先随机化：

```yaml
code: process_ai_${{random_id()}}
actionId: action_ai_${{random_id()}}
```

但新增约束：

- 随机值只用于“创建型”或“纯校验型”接口
- 如果接口语义要求引用已存在实体，禁止用随机值伪造真实实体

## 6. 缓存规则

`current_request_set_cache` 仅在结构明确时允许生成。

允许场景：

- 请求字段明确，且要把请求值缓存给后续接口
- 响应字段明确，且响应路径已确认

禁止场景：

- 猜测响应里“应该有 id/code”就写缓存
- 没有稳定前置创建链路时，强行串联编辑/删除/授权接口

当前统一规则：

- 优先用 `type: request` 缓存请求唯一键
- 只有确认响应结构后，才允许 `type: response`

## 7. 链路生成规则

删除和编辑接口不应被当成“独立接口”直接生成，而应默认视为链路型接口。

核心规则：

- 查询接口和新增接口通常更容易直接跑通，优先作为链路起点
- 编辑接口、删除接口如果依赖真实实体，必须复用前面的新增接口或查询接口产出的实体
- 不能用随机 `code/id` 冒充“待编辑对象”或“待删除对象”
- 如果前置实体不存在，就先生成前置新增用例，再生成编辑和删除用例

推荐链路：

1. 新增实体
2. 缓存新增时使用的唯一键，或缓存响应中的真实主键
3. 查询实体确认可访问
4. 编辑实体
5. 删除实体
6. 如有必要，再补删除后的查询校验

实现要求：

- 新增接口不仅是覆盖点，也是编辑/删除接口的前置数据提供者
- 如果新增接口返回结构不稳定，优先缓存请求中的唯一键
- 如果删除接口需要的不是 `code` 而是 `id/processId/objectId`，必须先确认后端真实字段来源
- 没有稳定前置链路的编辑/删除接口，不进入统一稳定集

## 8. 可执行性优先级

后续生成接口分 3 类。

### A 类：可直接生成可执行用例

特点：

- controller 参数清晰
- 最小请求体明确
- 不依赖真实已有实体
- 不依赖复杂权限链路

### B 类：需要特殊规则后才能生成

典型情况：

- `query + body` 混合
- `List<String>` / `List<DTO>` 数组 body
- 需要 `Authorization` 等额外请求头
- 需要简单缓存串联，但返回路径明确

### C 类：不进入首批 AI 通用调试集

典型情况：

- 必须引用真实存在的 `code/id/processId/taskCode/pageCode`
- 强依赖权限
- 强依赖下游服务、查询模型、真实业务关系
- 没有前置链路就无法稳定返回 `code=0`

## 9. 失败回灌经验

### 9.1 DTO 形状不能靠接口名猜

失败例子：

- `grantAuth`
- `saveStateRelation`
- `createOrUpdate`

规则更新：

- 只要请求对象不是简单扁平 DTO，就必须看请求类字段和 service 实际使用方式

### 9.2 显式请求头要求必须满足

失败例子：

- `task/updateTask`

规则更新：

- 发现 `@RequestHeader("Authorization")` 时，必须补 `Authorization`

### 9.3 数组 body 不能包成对象

失败例子：

- `queryExperienceOverTime`
- `saveTaskDataState`

规则更新：

- 只要后端签名是列表，`data` 必须直接是数组

### 9.4 随机 code 不能冒充真实实体

失败例子：

- `getPageDesignAuth`
- `editTenantProcess`
- `removeProcess`
- `setPageModel`

规则更新：

- 需要真实实体的接口，不再放入首批通用 AI 调试集
- 只有在前置创建链路稳定后才允许生成
- 编辑、删除接口优先复用新增接口生成的前置实体

### 9.5 权限接口不能当通用冒烟接口

失败例子：

- `grantAuth`
- `removeAuth`
- `transferAuth`
- `funcAuth`

规则更新：

- 权限接口从通用调试集移出，后续单独做权限专项链路集

### 9.6 已验证成功的链路模板

当前已经证明稳定可复用的链路有 3 组：

- `action`：`saveAction -> findActionByActionId -> updateAction -> deleteActionByActionId`
- `application`：`addV3 -> authAppInfo -> update -> delete/v2 -> queryDeleteProgress`
- `process`：`findAppEffectAdpVersion -> upsertSingleProject -> findProcessById -> copySingleProject -> removeProcess
- `pageDesign`：`businessDir/add -> modelDriver/queryModelByCode -> dataView/generateJustQueryPlan -> dataView/queryDataViewByModel -> pageDesign/generatePageDesignByQueryPlan -> pageDesign/queryByCode -> pageDesign/update -> pageDesign/delete -> businessDir/delete`

规则更新：

- 后续优先扩这种“新增产出实体，后续步骤消费实体”的链路
- 同一链路内允许重复使用同一接口，例如删除原对象和删除副本
- 覆盖率统计按唯一 `method + url` 计，不按链路步骤数计

## 10. 增量协作约定（2026-04-01补充）

本节用于沉淀当前对话里已经确认的执行口径。后续 AI 继续生成用例时，默认直接遵循本节，不再重复确认。

### 10.1 文件修改范围

- 新增或修复接口用例时，只修改 `data/ai` 目录下的 YAML 文件
- 允许按模块拆分多个 YAML 文件，不再要求统一收敛到单一 `AllInOne_ai.yaml`
- 测试包装文件 `test_case/ai/*.py` 默认不由 AI 维护，除非用户明确提出
- 文档类补充默认写入 `md_document` 目录

### 10.2 生成后必须自检

- 每次新增或修改 `data/ai` 下的 YAML 后，必须先执行自检
- 自检前，必须先运行以下文件生成最新 case 文件：

```powershell
python D:\sort\AthenaDesigner-ApiAutoTest\utils\read_files_tools\case_automatic_control.py
```

- 生成完成后，再执行当前统一自检命令：

```powershell
pytest test_case/ai
```

- 自检未通过时，不得直接把该批用例视为完成
- 必须先定位失败用例，修复对应 YAML 后再次执行 `pytest test_case/ai`
- 只有当 `pytest test_case/ai` 全量通过后，才允许继续下一批覆盖

### 10.3 自检判定规则

- 自检不只看 `$.code == 0`
- 必须结合后端 Controller、DTO、Service 的真实业务逻辑判断断言是否有效
- 断言应优先校验以下内容：
  - 必填条件是否满足
  - 返回主键/编码/名称是否与入参或缓存值一致
  - 链路前后资源状态是否一致
  - 非空列表、数量字段、资源归属字段是否符合业务语义
- 如果接口实际返回结构中存在类型差异，例如缓存值是字符串、响应值是数字，禁止继续使用脆弱的强等比较
- 遇到这种情况，应改成更稳定的业务断言，例如：
  - 校验 `enumKey / key / code` 一致
  - 校验 `id > 0`
  - 校验列表非空、统计值非负

### 10.4 新增接口筛选原则

- 优先生成当前环境下可稳定联调成功的查询型接口
- 优先覆盖项目现有 YAML 尚未出现的 `method + url`
- 如果真实探测发现接口具备以下情况，则当前批次不进入稳定集：
  - 返回空列表且缺少可证明业务价值的断言点
  - 强依赖外部授权、第三方服务、特殊租户资源
  - 返回 `NullPointerException`
  - 依赖真实存在但当前环境无法稳定拿到的前置实体

### 10.5 覆盖率记录要求

- 每次新增稳定用例并完成自检后，都要更新：
  - `md_document/覆盖率增加记录补丁.md`
- 记录内容必须包含：
  - 本次时间，精确到分钟
  - 本次新增或修复了哪些 YAML 文件
  - 每个 YAML 文件分别对应哪些 case id
  - 本次自检结果
  - 当前正式覆盖率
- `覆盖率增加记录补丁.md` 每次新增记录前必须加明显分割线，便于快速区分批次
- `覆盖率增加记录补丁.md` 只保留最近 `5` 次新增记录，更早记录不继续保留在正文中

正式覆盖率口径统一为：

- 基准契约：`data/ServerApi.json`
- 统计对象：`GET / POST / PUT / DELETE / PATCH`
- 有效覆盖定义：与契约成功匹配的唯一 `method + url`

### 10.6 当前已确认的执行习惯

- 每次开始新一批覆盖前，先分析后端源码和当前环境返回，不盲生成
- 优先使用“小链路闭环”思路生成用例
- 同一接口允许在不同小链路中重复出现，但覆盖率统计仍按唯一接口计算
- 如果只是修复 YAML 断言、不新增接口，也要先跑 `pytest test_case/ai` 验证基线恢复
- 任何新增或修改 `data/ai` YAML 的动作，在自检前都要先执行 `case_automatic_control.py` 重新生成 `test_case/ai` 下对应 case 文件
- 执行 `case_automatic_control.py` 和 `pytest test_case/ai` 时，默认补齐：
  - `PYTHONPATH=D:\sort\AthenaDesigner-ApiAutoTest`
  - `PYTHONIOENCODING=utf-8`
- 原因：直接运行脚本时，若未补 `PYTHONPATH`，可能出现 `ModuleNotFoundError: No module named 'common'`
- 标准自检顺序固定为：

```powershell
$env:PYTHONPATH = "D:\sort\AthenaDesigner-ApiAutoTest"
$env:PYTHONIOENCODING = "utf-8"
python D:\sort\AthenaDesigner-ApiAutoTest\utils\read_files_tools\case_automatic_control.py
pytest test_case/ai
```

### 10.7 控制台乱码说明

- 当前项目日志文件本身按 `UTF-8` 写入，文件内容通常正常
- 若手动执行 `pytest test_case/ai` 时控制台出现乱码，优先按“终端编码问题”处理，不直接判定为用例失败
- 建议手动自检前先执行：

```powershell
chcp 65001 > $null
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
pytest test_case/ai
```

- 如果日志文件正常、仅控制台乱码，则优先记录为“输出编码问题”，不算用例业务失败

### 10.8 Allure 标题层级命名规则

- `data/ai` 下所有 YAML 的 `case_common` 必须统一维护以下三层标题：

```yaml
case_common:
  allureEpic: 开发平台接口
  allureFeature: AI闭环用例
  allureStory: 具体业务闭环名称
```

- `allureEpic` 固定为：`开发平台接口`
- `allureFeature` 固定为：`AI闭环用例`
- `allureStory` 必须直接表达“这是哪个业务闭环”，要求言简意赅，一眼能看出所属模块或业务链路
- `allureStory` 命名优先使用“业务名 + 闭环”或“两个关联业务名 + 闭环”的格式，例如：
  - `知识库与数据集闭环`
  - `应用查询闭环`
  - `后台管理查询闭环`
  - `收藏查询闭环`
- `allureStory` 禁止继续使用冗长、技术味过重或识别度差的表述，例如：
  - 直接写 `XXXController稳定查询闭环`
  - 混入过多限定词，如“稳定”“生成”“接口”“Controller”
  - 写成难以一眼识别业务归属的泛化名称，如 `Common稳定查询`
- 若一个 YAML 内同时覆盖两个紧密相关模块，应直接在 `allureStory` 里写出两个业务名，不强行拆成 Controller 名称
- 后续新增或修改 `data/ai` YAML 时，AI 默认先自检 `case_common` 是否符合本规则，再进行 case 生成与回归

### 10.9 参考历史沉淀用例的生成规则

- 生成 `data/ai` 新用例前，优先扫描项目中已有的稳定沉淀 YAML，不闭门造车
- 重点参考的不是文件格式，而是项目里已经被长期使用的业务写法：
  - 前置依赖如何准备
  - `current_request_set_cache` 如何串联请求值与响应值
  - `detail` 如何描述业务动作
  - 同一链路里如何做“写后查”“查后比对”“最终恢复”
- 如果历史用例已经证明某类接口适合做闭环，AI 生成时应优先复用这种链路形态
- 历史用例里若只有 `code == 0` 的弱断言，AI 不应机械照搬；应在当前环境允许的前提下补上更实的业务校验

### 10.10 缓存链与闭环优先级

- 优先生成“可串联缓存链”的小闭环，而不是孤立单点接口
- 缓存值优先来自真实业务关键字段：
  - `code`
  - `objectId`
  - `id`
  - `name`
  - `key`
  - `status`
- 允许同时缓存请求值与响应值，用于后续链路做一致性校验
- 若一个接口只能 `code == 0`，但其后续查询接口能证明初始化、生成、设置结果已生效，则允许把它作为闭环中的前置步骤保留

### 10.11 可逆闭环与环境恢复

- 若接口涉及用户态、配置态、开关态、状态位等可修改资源，优先设计成“可逆闭环”
- 标准思路优先采用：
  - 查询当前状态
  - 修改为目标状态
  - 再查询确认生效
  - 恢复原始或约定初始状态
  - 最终再查一次确认恢复成功
- 若接口修改后无法恢复，默认不进入稳定集，除非用户明确要求且业务风险可控
- 若为了稳定回归需要专用隔离标识，应优先使用专用 `type/code/key`，避免污染真实业务数据

### 10.12 detail 与业务表达

- `detail` 要直接表达业务动作和校验目的，不只写接口名翻译
- 推荐写法：
  - “查询XXX并缓存首条编码与名称用于后续闭环校验”
  - “更新XXX状态并验证查询结果同步变化”
  - “恢复XXX配置，保证环境回到初始状态”
- 禁止把 `detail` 写成只有技术接口名、没有业务语义的短句

### 10.13 从旧用例迁移到 AI 用例的约束

- 可借鉴旧用例的接口、链路和断言思路，但新增 AI YAML 时仍必须遵守当前规则：
  - 只改 `data/ai`
  - 先 `case_automatic_control.py`
  - 再 `pytest test_case/ai`
  - 全量回归通过后才记入覆盖率
- 若旧用例里存在以下情况，AI 生成时应主动纠偏：
  - 只有 `code == 0` 且没有业务价值
  - 依赖路径过长，当前环境难以稳定复现
  - 清理不彻底，可能污染共享环境
  - 使用过于脆弱的 JSONPath 位置断言



## ??????
- ?????????? `code == 0`????????????????????? `id`?`objectId`?`code`?`name`?
- ?????????????????????????????? `id/objectId/code/name` ??????????????????
- ?????????????????????????????????????????????
- ?????????????????????????????????????????????????????
- ??????????????????????? schema ??????????????????????????? JSONPath?

### 10.9 覆盖率统计口径补充

- 覆盖率数字统一以 `utils/other_tools/InterfaceCoverage.py` 的输出为准，不再手工估算
- 记录文件中的 `当前 YAML 唯一接口数`、`当前未覆盖接口数`、`当前正式覆盖率` 必须来自该脚本的正式统计口径
- 如果发现手工估算与脚本结果不一致，以脚本结果为准，并在当次记录里注明口径已按脚本修正

### 10.10 AI YAML 自检范围补充

- 默认自检范围调整为“本次新增或本次修改的 AI YAML 对应用例”，不再每轮默认全量执行 `pytest test_case/ai`
- 标准顺序仍保持不变：
  - 先执行 `utils/read_files_tools/case_automatic_control.py`
  - 再执行对应新增 YAML 生成出的 `test_case/ai/test_xxx.py`
- 若定向自检失败，先修新增 YAML，再重复定向自检，直到该批稳定
- 只有在出现以下情况时，才需要升级为全量 `pytest test_case/ai`：
  - 修改影响了公共缓存链或公共前置数据
  - 同时改动了多个已存在 YAML 文件
  - 定向通过但怀疑与现有稳定集存在冲突
  - 用户明确要求做全量回归

### 10.14 data/ai 归并与后续新增策略

- `data/ai` 现在按“业务域”维护，而不是按“本次做了哪几个接口”维护
- 后续新增或修复时，优先判断应该并入哪个业务域 YAML，而不是先创建新文件
- 当前默认归并边界如下：
  - `ai_inquiry.yaml`
    - `KnowledgeBase`
    - `Dataset`
    - `Common`
    - `EntityType`
    - `WordDictionary`
    - `Favourite`
  - `ai_application.yaml`
    - `Application`
    - `ApplicationParam`
    - `CustomConfig`
    - `User`
    - `Guide`
    - `IndividualCase`
  - `ai_task_process.yaml`
    - `Project`
    - `Process`
    - `ProcessVersion`
    - `Task`
    - `TenantTask`
    - `GroupHistory`
    - `ResourceTree`
    - `PageDesign`
    - `MonitorRule`
  - `ai_activity_message.yaml`
    - `Activity`
    - `ActivityConfigs`
    - `AimScene`
    - `AimEvent`
    - `ApplicationGroup`
    - `MessageNotification`
    - `UpgradeNotification`
    - `BusinessDir`
  - `ai_base_support.yaml`
    - `BackgroundManagement`
    - `BaseInfo`
    - `Classification`
    - `BusinessType`
    - `DataStandardBusinessType`
    - `Dictionary`
    - `Dmc/File`
    - `Duty/Eoc`
    - `Tag/TagDefinition`
    - `Button`
    - `PresetData`
- 若一个接口同时和多个域有关，优先归到“主业务语义更强”的文件，而不是按 controller 名机械拆分
- 一轮新增允许覆盖多个小闭环，但尽量保持在同一个或相邻两个业务域内，避免再次把文件切碎

### 10.15 归并后的生成约束

- 后续新增 AI 用例时，默认流程改为：
  - 先判断所属业务域
  - 再并入对应 `ai_业务域.yaml`
  - 再执行 `case_automatic_control.py`
  - 再执行对应新增 YAML 的定向自检
- 非必要不再创建新的微型 YAML，例如：
  - `xxx_query_ai.yaml`
  - `yyy_detail_ai.yaml`
  - `zzz_temp_ai.yaml`
- 只有满足以下条件时，才允许新增新的业务域 YAML：
  - 现有 5 个文件都无法合理承载
  - 新域后续会持续扩充，而不是一次性临时批次
  - 新域本身可以形成清晰、长期可维护的业务边界
- 本轮归并阶段只处理 `data/ai` 下的 YAML；若产生旧的 `test_case/ai/test_*.py` 孤儿文件，由用户手动处理
- 归并阶段默认不以 `pytest` 结果作为门槛，优先保证：
  - YAML 分类边界清晰
  - YAML 结构可解析
  - 后续新增策略统一到业务域维度



