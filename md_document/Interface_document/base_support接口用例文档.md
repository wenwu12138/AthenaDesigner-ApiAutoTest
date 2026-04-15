# base_support接口用例文档

更新时间：2026-04-10

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中基础支撑相关 Controller 源码整理，用于作为后续维护 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai\ai_base_support.yaml` 的中间设计文档。

本模块当前统一归属建议：

- 业务域：`ai_base_support.yaml`
- 文档来源：Controller 方法签名 + 当前稳定 YAML + 现网回归表现

本次重点分析的后端入口包括：

- `com.digiwin.athena.controller.dictionary.DictionaryController`
- `com.digiwin.athena.controller.duty.DutyController`
- `com.digiwin.athena.controller.tag.TagController`
- `com.digiwin.athena.controller.tag.TagDefinitionController`

## 2. 模块结论

### 2.1 当前最适合先保留的稳定查询闭环

`base_support` 当前更适合做“查询闭环”，而不是新增/删除类闭环。

优先建议保留的主线：

1. 字典查询闭环
2. 标签动作查询闭环
3. 标签内建属性查询
4. 系统信息与简表类稳定查询

原因：

- 这类接口天然偏只读，环境副作用低。
- 大部分已经存在稳定查询入口，不需要额外创建业务实体。
- 当前环境下职责、标签定义等数据并不稳定存在，不适合硬做详情闭环。

### 2.2 当前建议保留为稳定查询集的接口

建议保留为稳定查询，不强行串成新增/编辑链：

- `GET /athena-designer/dictionary/querySystemInfos`
- `GET /athena-designer/dictionary/queryDictionary`
- `GET /athena-designer/dictionary/queryDictionaryByKey`
- `GET /athena-designer/dictionary/V2/queryDictionary`
- `GET /athena-designer/dictionary/V2/getDictByEnumKey`
- `GET /athena-designer/dictionary/V2/getDictInfoByEnumKey`
- `GET /athena-designer/dictionary/simpleDictionary`
- `GET /athena-designer/dictionary/V2/simpleDictionary`
- `GET /athena-designer/tag/public/actions`
- `GET /athena-designer/tag/taskAction`
- `GET /athena-designer/tag/builtInAttrs`

### 2.3 当前建议作为探测集或暂缓的接口

以下接口当前不建议默认纳入 AI 稳定集：

- `GET /athena-designer/duty/all`
- `GET /athena-designer/duty`
- `GET /athena-designer/tagDefinition/all`
- `GET /athena-designer/tagDefinition`
- `GET /athena-designer/dictionary/getDictByKey`
- `GET /athena-designer/dictionary/V2/getDictByKey`

原因：

- `duty` 与 `tagDefinition` 当前环境里可能直接返回空列表，没有稳定种子。
- `getDictByKey` / `V2/getDictByKey` 目前更多是在用“伪造不存在 key”探空，不是业务闭环。
- 不适合为提高覆盖率而硬塞进稳定集。

## 3. 推荐小闭环

### 3.1 字典查询闭环

闭环目标：从字典全量列表中拿到真实 key / enumKey，再查询对应详情，形成低副作用查询闭环。

推荐顺序：

1. `GET /athena-designer/dictionary/queryDictionary`
2. `GET /athena-designer/dictionary/queryDictionaryByKey`
3. `GET /athena-designer/dictionary/V2/queryDictionary`
4. `GET /athena-designer/dictionary/V2/getDictByEnumKey`
5. `GET /athena-designer/dictionary/V2/getDictInfoByEnumKey`

关键规则：

- `legacy` 与 `V2` 两套字典口径分开维护，不要跨口径比较首条记录。
- `queryDictionaryByKey` 只能消费同闭环里缓存的真实 key。
- `getDictByEnumKey` 与 `getDictInfoByEnumKey` 只能消费同闭环里缓存的真实 enumKey。
- 不建议用 `NON_EXIST_*` 之类伪造 key 来构造“空列表闭环”。

建议缓存：

- `dictionary_legacy_key`
- `dictionary_v2_key`
- `dictionary_v2_enum_key`
- `dictionary_v2_application`

建议断言：

- 列表接口：列表非空、关键字段非空
- 明细接口：key / enumKey / application 与缓存一致

### 3.2 标签动作查询闭环

闭环目标：先拿到真实公共动作，再查动作详情，形成标签动作轻量闭环。

推荐顺序：

1. `GET /athena-designer/tag/public/actions`
2. `GET /athena-designer/tag/taskAction`

关键源码结论：

- `public/actions` 返回的是分页对象，不要只依赖 `total`，还要校验 `data` 非空。
- `taskAction` 详情里当前环境更稳定的是 `request` 字段，不是 `response` 字段。

建议缓存：

- `tag_action_id`
- `tag_action_attr`

建议断言：

- `public/actions`：`$.data.data` 非空，`actionId` 非空
- `taskAction`：`$.data.actionId == $cache{tag_action_id}`，`request` 非空

### 3.3 标签内建属性查询

闭环目标：保留为稳定单点查询，不强行和动作链混绑。

接口：

- `GET /athena-designer/tag/builtInAttrs`

建议断言：

- 列表非空
- 首条 `attr`、`attrName` 非空

这是稳定查询，不建议继续往详情链扩。

## 4. duty 与 tagDefinition 的处理建议

### 4.1 duty

源码入口：

- `GET /athena-designer/duty/all`
- `GET /athena-designer/duty?code=...`

当前问题：

- 这组接口本来适合做 `all -> get` 轻量闭环。
- 但当前环境并没有稳定职责种子，`all` 可能直接为空。

建议：

- 先作为探测集保留。
- 后续若环境补齐稳定职责数据，再恢复：
  - `duty/all`
  - `duty`

### 4.2 tagDefinition

源码入口：

- `GET /athena-designer/tagDefinition/all`
- `GET /athena-designer/tagDefinition?code=...`

当前问题：

- 和 `duty` 类似，理论上适合做 `all -> get` 轻量闭环。
- 但当前环境没有稳定标签定义列表，不能默认进入稳定集。

建议：

- 继续保留为探测集
- 等环境有稳定数据后，再恢复详情链

## 5. 对现有 ai_base_support.yaml 的修正方向

当前文档对应的核心修正原则：

1. 不再把“当前环境空列表”写成业务契约，除非这是明确口径。
2. 查询闭环优先消费真实列表缓存，不消费伪造 key。
3. 标签动作链优先基于 `request` 字段，不再依赖 `response` 首项。
4. `duty`、`tagDefinition` 在没有稳定种子前，保持探测集，不强行恢复。

## 6. 接口分类建议

### 6.1 A 类：优先保留并纳入稳定集

- `GET /athena-designer/dictionary/querySystemInfos`
- `GET /athena-designer/dictionary/queryDictionary`
- `GET /athena-designer/dictionary/queryDictionaryByKey`
- `GET /athena-designer/dictionary/V2/queryDictionary`
- `GET /athena-designer/dictionary/V2/getDictByEnumKey`
- `GET /athena-designer/dictionary/V2/getDictInfoByEnumKey`
- `GET /athena-designer/dictionary/simpleDictionary`
- `GET /athena-designer/dictionary/V2/simpleDictionary`
- `GET /athena-designer/tag/public/actions`
- `GET /athena-designer/tag/taskAction`
- `GET /athena-designer/tag/builtInAttrs`

### 6.2 B 类：稳定单点查询保留

- `GET /athena-designer/dmc/queryDmcToken`
- `GET /athena-designer/file/getDmcToken`
- `GET /athena-designer/button/queryProjectInitData`
- `GET /athena-designer/button/queryManuallyInitData`
- `GET /athena-designer/button/queryButtonsByKey/{key}`

### 6.3 C 类：探测集或暂缓

- `GET /athena-designer/duty/all`
- `GET /athena-designer/duty`
- `GET /athena-designer/tagDefinition/all`
- `GET /athena-designer/tagDefinition`
- `GET /athena-designer/dictionary/getDictByKey`
- `GET /athena-designer/dictionary/V2/getDictByKey`

## 7. 后续 YAML 落地建议

后续如果继续清理 `ai_base_support.yaml`，建议按下面顺序推进：

1. 先把字典闭环全部统一成“真实 key / enumKey 查询”
2. 再保持标签动作链为主闭环
3. 最后再看 `duty`、`tagDefinition` 是否具备恢复条件

不建议优先做：

- `duty` 新增/删除
- `tagDefinition` 新增/删除
- 用伪造 key 探空的字典用例

因为这些要么强依赖环境种子，要么检测价值偏低，不适合当前 AI 稳定集目标。
