# athena_designer 后端接口文档

更新时间：2026-04-01

## 1. 文档目的

本文档基于后端项目 `D:\sort\athena_designer` 的源码扫描结果整理，目标是给接口自动化项目 `D:\sort\AthenaDesigner-ApiAutoTest` 提供一份可直接用于：

- 接口盘点
- 自动化覆盖率规划
- YAML 用例生成
- 鉴权和断言规则统一

说明：

- 本文档以源码静态分析为准，不依赖运行时 Swagger 页面
- 本文档重点关注 Controller 入口、路由分布、鉴权方式、返回约定和自动化价值
- 部分 Controller 已接入 OpenAPI 注解，但项目内 `SwaggerConfig` 当前是注释关闭状态

## 2. 项目概况

### 2.1 技术栈

- JDK：17
- 框架：Spring Boot 3.x、Spring MVC、Spring Security
- 数据访问：MyBatis / MyBatis-Plus、Spring Data MongoDB
- 基础设施：Redis、RabbitMQ、Quartz、WebSocket
- 文档能力：`springdoc-openapi-ui`
- 其他：MapStruct、EasyExcel、Apache POI、JGit、Hutool

### 2.2 服务入口与统一前缀

`application.yml` 中定义：

```yaml
server:
  port: 8000
  servlet:
    context-path: /athena-designer
```

因此接口完整访问路径统一形态为：

```text
/athena-designer/{controller_mapping}/{method_mapping}
```

### 2.3 主启动类

- `com.digiwin.athena.AppBoot`

项目是标准 Spring Boot 单体应用，Controller 为主入口，不是 Router 函数式风格。

## 3. 接口入口分布

基于 `src/main/java/com/digiwin/athena` 下全部 `*Controller.java` 扫描，排除 `BaseController.java` 后，当前代码规模如下：

| 顶层包 | Controller 数 | 方法级接口数 |
|---|---:|---:|
| `controller` | 134 | 1313 |
| `agiledata` | 25 | 194 |
| `agiledatainquiry` | 5 | 31 |
| `asa` | 7 | 46 |
| `backendmanage` | 5 | 41 |
| `mlops` | 5 | 57 |
| 合计 | 181 | 1682 |

说明：

- “方法级接口数”统计口径为 `@GetMapping`、`@PostMapping`、`@PutMapping`、`@DeleteMapping`、`@PatchMapping`
- 类级别 `@RequestMapping` 不计入接口数

## 4. 主业务包细分

`com.digiwin.athena.controller` 是最大接口来源。其子模块分布如下：

| 子模块 | Controller 数 | 接口数 |
|---|---:|---:|
| `root` | 9 | 193 |
| `pagedesign` | 9 | 107 |
| `ai` | 5 | 106 |
| `task` | 9 | 104 |
| `mechanism` | 5 | 62 |
| `modeldriver` | 6 | 54 |
| `activity` | 5 | 50 |
| `action` | 4 | 38 |
| `application` | 7 | 37 |
| `workbench` | 6 | 37 |
| `process` | 3 | 34 |
| `data` | 2 | 27 |
| `dictionary` | 1 | 26 |
| `datastandard` | 3 | 26 |
| `tag` | 2 | 26 |
| `individualApp` | 1 | 25 |
| `archive` | 2 | 25 |
| `appCustomConfig` | 1 | 22 |
| `messageCenter` | 2 | 20 |
| `system` | 3 | 19 |
| `favourite` | 2 | 18 |
| `presetData` | 2 | 17 |
| `auth` | 1 | 17 |
| `extendField` | 2 | 16 |
| `template` | 1 | 16 |

自动化优先级建议：

1. `application`
2. `pagedesign`
3. `task`
4. `agiledata`
5. `auth`
6. `agiledatainquiry`

原因：

- 路由数量大，回归价值高
- 多数接口具备查询、新增、更新、删除、复制、导出等稳定模式
- 能较快形成链路型自动化

## 5. 认证、拦截与请求约定

### 5.1 Spring Security

核心文件：

- `src/main/java/com/digiwin/athena/security/SecurityConfig.java`
- `src/main/java/com/digiwin/athena/config/AppWebMvcConfigurer.java`

关键结论：

- 默认策略：`anyRequest().authenticated()`
- 会话策略：`STATELESS`
- 核心认证过滤器：`TokenFilter2`
- 自定义认证提供者：`TokenAuthenticationProvider`

### 5.2 白名单接口

`application.yml` 与 `SecurityConfig` 中可以确认部分白名单：

- `/user/login`
- `/user/v2/login`
- `/user/bind`
- `/user/iamTokenLogin`
- `/inquiry/common/mcpLogin`
- `/healthcheck`
- `/swagger-ui/**`
- `/v3/api-docs/**`
- `/actuator/*`
- `/ws/**`

结论：

- 除白名单外，大部分接口都需要登录态
- 自动化调用时应默认带认证头

### 5.3 MVC 拦截器

`AppWebMvcConfigurer` 注册了以下拦截器：

- `CustomizationURLInterceptor`
- `UserAppAuthInterceptor`
- `RequestInterceptor`
- `CurThreadInterceptor`

这意味着很多接口除了登录态，还可能叠加：

- 应用级权限
- 当前线程上下文
- 请求日志追踪

### 5.4 自动化建议请求头

结合后端代码和现有自动化项目，建议默认使用：

```yaml
headers:
  digi-middleware-auth-user: $cache{token}
  token: $cache{token}
  locale: zh_CN
  content-type: application/json
```

补充规则：

- 文件下载类接口通常不需要 `content-type: application/json`
- 若后端显式要求其他头，如 `Authorization`、`callForPrivate`，必须按方法签名补充

## 6. 统一返回与断言规则

### 6.1 通用返回包装

核心返回对象：

- `src/main/java/com/digiwin/athena/base/ResultBean.java`

主要结构：

```json
{
  "code": 0,
  "msg": "",
  "data": {},
  "dataList": [],
  "pageIndex": 1,
  "pageSize": 10,
  "totalCount": 100,
  "ext": {},
  "token": ""
}
```

关键结论：

- 成功码：`0`
- 常见失败形式：`ResultBean.fail(code, msg)`
- 大多数 JSON 接口第一阶段都可以使用 `$.code == 0` 做基础断言

### 6.2 全局异常处理

核心文件：

- `GlobalExceptionHandler.java`
- `RestControllerExceptionHandler.java`

常见异常来源：

- `BusinessException`
- `MethodArgumentNotValidException`
- `BindException`
- `ValidateException`
- 兜底 `Exception`

自动化含义：

- 参数错误一般不会返回 HTTP 4xx，而更常见是 HTTP 200 + `code != 0`
- 负向用例应优先校验返回体 `code/msg`，而不是只看状态码

### 6.3 下载类接口断言

对导出、模板下载、错误文件下载等接口，建议断言：

- HTTP 状态码为 `200`
- `content-type` 包含文件流类型
- `content-disposition` 包含附件文件名

## 7. Swagger / OpenAPI 现状

项目引入了 `springdoc-openapi-ui`，并且不少 Controller / DTO 使用了：

- `@Operation`
- `@Tag`
- `@Schema`

但当前代码中的 `SwaggerConfig` 是注释关闭状态，因此：

- 源码层存在一定 OpenAPI 注解基础
- 运行环境不一定直接暴露完整 Swagger 文档
- 不能把 Swagger 页面当作唯一接口来源，仍应以源码扫描为准

## 8. 重点模块说明

### 8.1 ApplicationController

文件：

- `src/main/java/com/digiwin/athena/controller/ApplicationController.java`

类映射：

- `/application`

特点：

- 接口量极大，覆盖应用新增、更新、删除、复制、编译、导入导出、最近访问、方案模板、删除进度、部署计划等
- 是最值得优先持续扩充自动化的业务入口之一

代表接口：

- `GET /athena-designer/application/all`
- `GET /athena-designer/application/get`
- `POST /athena-designer/application/add`
- `POST /athena-designer/application/update`
- `GET /athena-designer/application/delete/{code}`
- `POST /athena-designer/application/copy`
- `POST /athena-designer/application/export`
- `POST /athena-designer/application/leadInto`
- `POST /athena-designer/application/queryDeleteProgress`

### 8.2 DapPageDesignController

文件：

- `src/main/java/com/digiwin/athena/controller/pagedesign/DapPageDesignController.java`

类映射：

- `/pageDesign`

特点：

- 页面设计主入口，包含增删改查、复制、发布、查询字段、生成页面、低代码切换等
- 适合构建链路型自动化：创建页面 -> 查询页面 -> 更新页面 -> 删除页面

代表接口：

- `POST /athena-designer/pageDesign/add`
- `POST /athena-designer/pageDesign/update`
- `GET /athena-designer/pageDesign/delete`
- `GET /athena-designer/pageDesign/queryByCode`
- `POST /athena-designer/pageDesign/queryByPage`
- `POST /athena-designer/pageDesign/generatePageDesignByQueryPlan`

### 8.3 DataFlowController

文件：

- `src/main/java/com/digiwin/athena/agiledata/controller/DataFlowController.java`

类映射：

- `/dataFlow`

特点：

- 敏捷数据核心入口，模式较标准，适合分页查询、详情、复制、删除、校验类用例
- 对自动化价值高，但部分接口依赖真实模型、模板或历史数据

代表接口：

- `POST /athena-designer/dataFlow/createOrUpdate`
- `POST /athena-designer/dataFlow/getDataFlowsByPage`
- `GET /athena-designer/dataFlow/delete`
- `POST /athena-designer/dataFlow/batchDelete`
- `GET /athena-designer/dataFlow/detail`
- `POST /athena-designer/dataFlow/copyDataFlow`

### 8.4 AuthController

文件：

- `src/main/java/com/digiwin/athena/controller/auth/AuthController.java`

类映射：

- `/auth`

特点：

- 既有登录态校验，又叠加 `@FuncAuth`、`@FuncAuth4Assign`
- 很多接口强依赖真实资源、角色、应用、授权主体
- 适合在已有应用/资源前置链路基础上逐步补充

代表接口：

- `POST /athena-designer/auth/grantAuth`
- `POST /athena-designer/auth/batchGrantAuth`
- `POST /athena-designer/auth/removeAuth`
- `POST /athena-designer/auth/queryAuthPolicy`
- `GET /athena-designer/auth/queryResourceRoleUser`

### 8.5 agiledatainquiry 模块

目录：

- `src/main/java/com/digiwin/athena/agiledatainquiry/controller`

特点：

- 总量不大，路由结构清晰
- 非常适合作为 AI 自动生成 YAML 的首批稳定模块
- 其中查询类和标准 CRUD 类最容易稳定跑通

详见第 10 章附录。

### 8.6 backendmanage 模块

目录：

- `src/main/java/com/digiwin/athena/backendmanage/controller`

特点：

- 以统计查询和导出类接口为主
- 多数为后台管理或测试用途
- 适合作为导出型接口专项补充

详见第 11 章附录。

## 9. 自动化测试落地建议

### 9.1 首批最适合补 YAML 的接口类型

A 类，优先直接落地：

- 分页查询
- 列表查询
- 详情查询
- 枚举/下拉/类型查询
- 标准新增
- 标准更新
- 标准删除

推荐优先顺序：

1. `agiledatainquiry`
2. `application`
3. `pagedesign`
4. `agiledata`
5. `backendmanage` 导出接口

### 9.2 适合链路生成的模式

推荐统一链路：

1. 新增
2. 缓存请求唯一键
3. 查询或详情校验
4. 更新
5. 删除
6. 删除后再查

### 9.3 不建议首批直接 AI 生成的接口

C 类，建议放后：

- 强依赖真实 `id/code/processId/pageCode` 的接口
- 强依赖授权资源和角色关系的接口
- 强依赖外部服务、文件上传、Excel 内容结构的接口
- 需要前置业务实体图谱的接口

## 10. 附录 A：agiledatainquiry 模块接口清单

### 10.1 KnowledgeBaseController

- 类映射：`/inquiry/knowledge`
- `POST /createOrUpdate`
- `POST /getPageList`
- `POST /getList`
- `POST /batchDelete`
- `DELETE /delete/{id}`

### 10.2 DatasetController

- 类映射：`/inquiry/dataset`
- `POST /add`
- `POST /edit`
- `GET /detail`
- `POST /getPageList`
- `GET /allDatasets`
- `POST /delete`
- `POST /updateStatus`
- `POST /parseExcel`
- `POST /addFromExcel`
- `POST /queryProcess`

### 10.3 ImplicitAssociationController

- 类映射：`/inquiry/association`
- `POST /save`
- `GET /query`
- `POST /fieldCheck`
- `GET /delete`

### 10.4 DataSourceController

- 类映射：`/inquiry/datasource`
- `POST /getList`
- `POST /getModels`
- `GET /getModelDetail`
- `GET /getDataSourceTypes`
- `POST /getTables`
- `GET /getTableDetail`

### 10.5 CommonController

- 类映射：`/inquiry/common`
- `GET /downTemplate`
- `GET /exportV2`
- `POST /import`
- `GET /downloadError`
- `GET /authModules`
- `POST /mcpLogin`

自动化建议：

- 首批优先：`knowledge`、`dataset`、`association/query`、`common/authModules`
- 第二批：`datasource`
- 第三批：导入导出、Excel 解析、模板下载

## 11. 附录 B：backendmanage 模块接口清单

### 11.1 ApplicationTestController

- 类映射：`/applicationTest6`
- `GET /exportApp`

### 11.2 PageDesignTestController

- 类映射：`/pageDesignTest6`
- `GET /export`
- `GET /exportWithMonth`

### 11.3 PageViewTestController

- 类映射：`/pageViewTest6`
- `GET /export`

### 11.4 UserTestController

- 类映射：`/userTest6`
- `GET /exportUser`

### 11.5 BackgroundTestController

- 类映射：`/backgroundManagement`
- `GET /isManager`
- `GET /queryApplicationDataListByPage`
- `GET /queryApplicationDataListTotal`
- `GET /allTenantApplicationDataListByPage`
- `GET /allTenantApplicationDataListTotal`
- `GET /queryApplicationDataNum`
- `GET /allTenantApplicationDataNum`
- `GET /queryApplicationNumByType`
- `GET /allTenantApplicationNumByType`
- `GET /queryDataCard2`
- `GET /allTenantDataCard2`
- `GET /queryDataCard`
- `GET /queryAllDataCard`
- `GET /queryDateDrivenLine`
- `GET /AllDateDrivenLine`
- `GET /queryApplicationByPage`
- `GET /queryApplicationTotal`
- `GET /queryModelByPage`
- `GET /queryModelTotal`
- `GET /queryWorkByPage`
- `GET /queryWorkTotal`
- `GET /queryActionByPage`
- `GET /queryActionTotal`
- `GET /queryDetectionByPage`
- `GET /queryDetectionTotal`
- `GET /querySchemeByPage`
- `GET /querySchemeTotal`
- `GET /queryUserByPage`
- `GET /queryUserTotal`
- `GET /queryProcessByPage`
- `GET /queryProcessTotal`
- `GET /queryTaskByPage`
- `GET /queryTaskTotal`
- `GET /queryHooksByPage`
- `GET /queryHooksTotal`

自动化建议：

- 背景统计查询接口可批量补 GET + PARAMS 类型 YAML
- 导出接口单独归类为下载断言模板

## 12. 结论

当前 `athena_designer` 后端项目接口规模很大，源码扫描结果显示至少有：

- `181` 个 Controller
- `1682` 个方法级接口

其中最值得先做高覆盖率自动化的，不是全量接口，而是“结构稳定、参数清晰、依赖较少”的接口族：

1. `agiledatainquiry`
2. `application`
3. `pagedesign`
4. `agiledata`
5. `backendmanage` 查询/导出接口

如果后续要继续落地到 YAML，建议直接以本文档第 10、11 章为入口，先补稳定查询接口，再补标准 CRUD 链路。

-----------------------------------------

## ?????????2026-04-03 14:22?
### ActivityController

- `GET /athena-designer/activity/types`
- `GET /athena-designer/activity/queryActivityConfigsByPage`
- `POST /athena-designer/activity/checkResIdUsed`
- `GET /athena-designer/activity/queryFavourite`

### AimSceneController

- `GET /athena-designer/aimScene/queryChannels`
- `GET /athena-designer/aimScene/queryAllOpenAimScenes`

### AimEventController

- `GET /athena-designer/aimEvent/queryListOfPlatForm`
- `GET /athena-designer/aimEvent/queryEventOfPlatFormAndApp`

### ApplicationGroupController

- `GET /athena-designer/applicationGroup/getGroupByApplication`

### ???? YAML ?????
- `data/ai/activity_message_ai.yaml`
- `activity_types_001`
- `activity_query_configs_by_page_001`
- `activity_check_res_id_used_001`
- `activity_query_favourite_public_001`
- `aim_scene_query_channels_001`
- `aim_event_query_platform_list_001`
- `aim_event_query_platform_and_app_001`
- `aim_scene_query_all_open_001`
- `application_group_query_by_application_001`

### ??????

- ????`python D:/sort/AthenaDesigner-ApiAutoTest/utils/read_files_tools/case_automatic_control.py`
- ????`pytest test_case/ai`
- ?????`207 passed, 4 skipped in 209.50s`

### ???????

- ???????`1802`
- ?? YAML ??????`388`
- ?????????`1414`
- ????????`21.53%`
- ???????????????? `utils/other_tools/InterfaceCoverage.py` ?????????
