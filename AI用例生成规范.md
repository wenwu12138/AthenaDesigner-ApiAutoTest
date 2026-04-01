# AI用例生成规范

## 1. 文档定位

这份文档已经合并了原来的“AI用例生成规范”和“AI生成用例说明”。以后只维护这一份，作为：

- AI 生成 YAML 的规则来源
- 当前统一调试集的说明文档
- 每一轮调试后经验回灌的记录入口

旧文档 [`AI生成用例说明.md`](D:/sort/AthenaDesigner-ApiAutoTest/AI生成用例说明.md) 不再单独维护。

## 2. 当前文件组织

- 统一 AI 调试集：[`AllInOne_ai.yaml`](D:/sort/AthenaDesigner-ApiAutoTest/data/ai/AllInOne_ai.yaml)
- 对应测试包装：[`test_AllInOne_ai.py`](D:/sort/AthenaDesigner-ApiAutoTest/test_case/ai/test_AllInOne_ai.py)

规则：

- 当前调试阶段，新增 AI 用例统一先放到 `data/ai/AllInOne_ai.yaml`
- 等规则稳定后，再按业务模块拆回原目录
- 文件名必须以 `ai` 结尾，便于区分 AI 生成文件和人工维护文件

## 2.1 当前统一调试集快照

截至 2026-03-26，统一 AI 调试集状态为：

- 调试集文件：[`AllInOne_ai.yaml`](D:/sort/AthenaDesigner-ApiAutoTest/data/ai/AllInOne_ai.yaml)
- 测试入口：[`test_AllInOne_ai.py`](D:/sort/AthenaDesigner-ApiAutoTest/test_case/ai/test_AllInOne_ai.py)
- 当前收集用例数：`858`
- 最新结构校验结果：`858 tests collected`
- 当前契约内有效接口数：`998`

当前已经验证成功并沉淀下来的链路样板包括：

- `action` 链路：新增 -> 查询 -> 更新 -> 删除
- `application` 链路：新增 -> 查询 -> 更新 -> 删除 -> 删除进度查询
- `process` 链路：取 ADP 版本 -> 新增 -> 查询 -> 复制 -> 删除原对象 -> 删除副本
- `pageDesign` 链路：创建业务对象 -> 查询业务对象 -> 生成查询方案 -> 查询数据视图 -> 生成页面 -> 查询页面 -> 更新页面 -> 删除页面 -> 清理业务对象

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



## ??????
- ?????????? `code == 0`????????????????????? `id`?`objectId`?`code`?`name`?
- ?????????????????????????????? `id/objectId/code/name` ??????????????????
- ?????????????????????????????????????????????
- ?????????????????????????????????????????????????????
- ??????????????????????? schema ??????????????????????????? JSONPath?


