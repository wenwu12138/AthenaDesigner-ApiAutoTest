# activity_message接口用例文档

## 1. 文档定位

本文档用于整理 `activity_message` 相关后端接口的闭环单位，并作为后续生成 `data/ai/ai_activity_message.yaml` 的直接依据。

目标不是穷举所有接口，而是先区分：

- 可直接进入稳定集的小闭环
- 可作为稳定查询集的接口
- 当前环境缺少稳定种子或后端返回异常，只能保留为探测集的接口

对应后端源码主要来自：

- `com.digiwin.athena.controller.activity.ActivityController`
- `com.digiwin.athena.controller.activity.ActivityConfigsController`
- `com.digiwin.athena.controller.messageCenter.AimSceneController`
- `com.digiwin.athena.controller.messageCenter.AimEventController`
- `com.digiwin.athena.controller.system.MessageNotificationController`
- `com.digiwin.athena.controller.system.UpgradeNotificationController`

## 2. 模块拆分

`activity_message` 当前可拆成 5 个子域：

1. 活动作业只读查询
2. 消息中心事件与场景闭环
3. 消息通知只读查询
4. 升级通知只读查询
5. 活动配置与消息通知探测接口

其中真正适合先做稳定闭环的是第 2 类，最适合做稳定查询集的是第 1、3、4 类。

## 3. 稳定闭环

### 3.1 事件场景闭环

闭环目标：构造一个应用级消息事件，再基于该事件创建应用级消息场景，最后删除场景恢复环境。

#### 3.1.1 事件入口

- 接口：`POST /athena-designer/aimEvent/insert`
- 作用：新增事件
- 前置：需要 `application`
- 用例类型：`create`
- 关键缓存：
  - `aim_event_first_id`
  - `aim_event_first_name`

建议断言：

- `$.code == 0`
- 新建后能在事件列表或详情中命中

#### 3.1.2 事件查询

- 接口：`GET /athena-designer/aimEvent/detail`
- 作用：按 `eventId` 查询详情
- 用例类型：`detail`
- 前置来源：新建事件返回值

建议断言：

- `$.code == 0`
- `$.data.id == $cache{aim_event_first_id}`

#### 3.1.3 场景创建

- 接口：`POST /athena-designer/aimScene/insert`
- 作用：创建应用级消息场景
- 前置：已有事件
- 用例类型：`create`
- 关键缓存：
  - `aim_scene_event_sid`
  - `aim_scene_event_name`

建议断言：

- `$.code == 0`
- 场景编码存在

#### 3.1.4 场景详情

- 接口：`GET /athena-designer/aimScene/detail/{sceneId}`
- 作用：查询新建场景详情
- 用例类型：`detail`
- 前置来源：新建场景返回值

建议断言：

- `$.code == 0`
- `$.data.application == 当前 app`
- `$.data.type.name` 非空

#### 3.1.5 场景关联校验

- 接口：`GET /athena-designer/aimEvent/queryAllSceneByEventId`
- 作用：查询事件关联场景
- 用例类型：`query`
- 前置来源：新建事件 + 新建场景

建议断言：

- `$.code == 0`
- 返回列表非空
- 首条或命中项的 `type.triggerId == $cache{aim_event_first_id}`

#### 3.1.6 场景事件体说明

- 接口：`GET /athena-designer/aimScene/queryEventBodyExplain`
- 作用：查询场景事件体说明
- 用例类型：`query`
- 前置来源：新建场景

建议断言：

- `$.code == 0`
- `$.data` 非空

#### 3.1.7 场景删除

- 接口：`GET /athena-designer/aimScene/delete/{sceneId}`
- 作用：删除新建场景恢复环境
- 用例类型：`delete`
- 前置来源：新建场景

建议断言：

- `$.code == 0`

#### 3.1.8 事件闭环状态

当前结论：

- 该闭环可作为 `activity_message` 的主稳定闭环
- 删除场景已具备可逆性
- 事件删除是否纳入闭环取决于当前环境是否允许安全删除新建事件

当前建议：

- 先保持“事件创建 -> 场景创建 -> 关联校验 -> 场景删除”
- 事件删除暂不默认启用，除非确认不会影响跨用例稳定性

## 4. 稳定查询集

### 4.1 活动类型与分页

可稳定保留：

- `GET /athena-designer/activity/types`
- `GET /athena-designer/activity/queryActivityConfigsByPage`
- `POST /athena-designer/activity/checkResIdUsed`
- `GET /athena-designer/activityConfigs/getActivityListByPattern`
- `GET /athena-designer/activityConfigs/getDataEntryByApplication`
- `GET /athena-designer/activityConfigs/getCustomId`
- `GET /athena-designer/activityConfigs/getAbiInnerToken`
- `GET /athena-designer/activityConfigs/getTbbInnerToken`
- `GET /athena-designer/aimScene/queryChannels`
- `GET /athena-designer/aimEvent/queryListOfPlatForm`

这些接口的共同特点：

- 不依赖当前应用下必须存在某个特定活动
- 只需断言返回结构或基础字段存在
- 能提供后端可用性和契约结构覆盖

### 4.2 消息通知查询

优先保留：

- `GET /athena-designer/messageNotification/queryTopic`

条件保留：

- `GET /athena-designer/messageNotification/queryAll`
- `GET /athena-designer/messageNotification/queryMessageByUser`
- `GET /athena-designer/messageNotification/queryValid`
- `GET /athena-designer/messageNotification/queryProductNews`

说明：

- `queryTopic` 最稳定，只校验 SYS/USER/TENANT 主题存在即可
- 其余通知查询接口依赖当前环境是否存在有效公告，不建议再做“首条一致性强绑定”
- 如果保留，断言应降到“返回对象存在”或“列表结构合法”，不要要求首条跨接口一致

### 4.3 升级通知查询

条件保留：

- `GET /athena-designer/upgradeNotification/queryHistory`
- `GET /athena-designer/upgradeNotification/queryAll`
- `GET /athena-designer/upgradeNotification/queryValid`

说明：

- 这组接口适合做查询型覆盖
- 不适合再用“历史首条 == 全量首条”的强绑定断言
- 推荐仅校验返回对象存在、状态字段合法、列表结构正确

## 5. 探测集

### 5.1 依赖当前应用活动种子的接口

以下接口当前不应进入稳定集：

- `GET /athena-designer/activityConfigs/getActivityListByPatternAndApplication`
- `GET /athena-designer/activityConfigs/getActivityByCode`
- `GET /athena-designer/activityConfigs/getActivityBasicInfo`
- `GET /athena-designer/activityConfigs/getActivityListByApplication`
- `GET /athena-designer/activityConfigs/getActivityConfigByCode/{code}`
- `GET /athena-designer/activityConfigs/getDataEntryUserTableName`
- `GET /athena-designer/activityConfigs/getSignDataEntryMetaData`
- `GET /athena-designer/activityConfigs/validateExist`
- `POST /athena-designer/activityConfigs/getActivityList`
- `GET /athena-designer/activityConfigs/{code}`
- `GET /athena-designer/activity/queryByActivityCode`

原因：

- 当前环境下 `DATA_ENTRY` 活动种子并不稳定
- 某些接口返回空列表、空对象，甚至 `NullPointerException`
- 这些接口更适合后续通过“先造可控活动实体”再进入闭环

### 5.2 强依赖环境通知数据的接口

当前保留为探测集：

- `GET /athena-designer/messageNotification/queryAll`
- `GET /athena-designer/messageNotification/queryMessageByUser`
- `GET /athena-designer/messageNotification/queryValid`
- `GET /athena-designer/messageNotification/queryProductNews`
- `GET /athena-designer/upgradeNotification/queryHistory`
- `GET /athena-designer/upgradeNotification/queryAll`
- `GET /athena-designer/upgradeNotification/queryValid`

原因：

- 当前环境下数据存在性不稳定
- 旧 YAML 依赖“首条记录一致”或“首条状态一致”，过脆弱

## 6. 推荐 YAML 生成策略

### 6.1 第一批稳定集

建议保留或生成：

- 事件场景闭环
- `activity/types`
- `activity/queryActivityConfigsByPage`
- `activity/checkResIdUsed`
- `activityConfigs/getActivityListByPattern`
- `activityConfigs/getDataEntryByApplication`
- `activityConfigs/getCustomId`
- `activityConfigs/getAbiInnerToken`
- `activityConfigs/getTbbInnerToken`
- `aimScene/queryChannels`
- `aimEvent/queryListOfPlatForm`
- `messageNotification/queryTopic`

### 6.2 第二批条件查询集

建议在断言降级后再保留：

- `messageNotification/queryAll`
- `messageNotification/queryMessageByUser`
- `messageNotification/queryValid`
- `messageNotification/queryProductNews`
- `upgradeNotification/queryHistory`
- `upgradeNotification/queryAll`
- `upgradeNotification/queryValid`

### 6.3 暂不生成或保留 skip

- 所有依赖 `DATA_ENTRY` 首条活动种子的接口
- 已知返回 `NullPointerException` 的活动配置全量属性接口
- 返回精简对象、无法形成稳定业务断言的活动详情接口

## 7. 结论

`activity_message` 不应该继续围绕“当前应用下首条活动配置”去拼伪闭环。

当前正确的生成方向是：

- 以 `aimEvent + aimScene` 作为主闭环
- 以活动类型、平台事件、渠道、token、分页查询作为稳定查询集
- 将活动配置详情、消息通知列表、升级通知列表中的环境依赖项降为探测集

后续 YAML 重构应遵循这个分层，不再以“列表首条跨接口一致”作为主要断言策略。
