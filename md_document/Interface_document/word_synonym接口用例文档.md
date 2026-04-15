# word_synonym接口用例文档

更新时间：2026-04-14

## 1. 文档说明

本文档基于后端项目 `D:\sort\athena_designer` 中 `WordController`、`SynonymController`、`EntityTypeController` 源码整理，用于作为 `D:\sort\AthenaDesigner-ApiAutoTest\data\ai` 中 AI YAML 的中间设计文档。

本次目标不是补零散查询，而是一次性落地一组可以自清理的小闭环，用来在稳定前提下拉高有效覆盖数。

建议归属：

- 业务域：`ai_inquiry.yaml`
- 设计原则：新增 -> 查询/详情 -> 删除

## 2. 模块结论

`word + synonym` 适合一次性推进，原因有两点：

1. `word` 模块天然拆成 5 条标准 CRUD 小闭环。
2. `synonym/entityType` 可以组成一条可逆闭环，新增实体类型作为前置，再新增同义词、查询、校验、删除。

按唯一接口计，本批可直接推进的稳定接口数为 `20`：

- `word`：12 个
- `entityType`：4 个
- `synonym`：4 个

这一批满足“业务小闭环 + 清理残留 + 单轮 1% 左右增量”的推进目标。

## 3. 推荐业务闭环

### 3.1 主闭环 A：分类闭环

顺序：

1. `POST /athena-designer/word/categorySave`
2. `POST /athena-designer/word/categoryQuery`
3. `POST /athena-designer/word/categoryDelete`

缓存建议：

- `word_ai_category_id`
- `word_ai_category_code`
- `word_ai_category_name`

### 3.2 主闭环 B：特征闭环

顺序：

1. `POST /athena-designer/word/featureSave`
2. `POST /athena-designer/word/featureQuery`
3. `POST /athena-designer/word/featureDelete`

缓存建议：

- `word_ai_feature_id`
- `word_ai_feature_code`
- `word_ai_feature_name`

### 3.3 主闭环 C：单词闭环

顺序：

1. `POST /athena-designer/word/wordSave`
2. `POST /athena-designer/word/wordQuery`
3. `POST /athena-designer/word/wordDelete`

关键约束：

- `wordSave` 使用当前闭环生成的分类与特征
- 删除后不再依赖该 `wordId`

缓存建议：

- `word_ai_word_id`
- `word_ai_word_code`
- `word_ai_word_name`

### 3.4 主闭环 D：观察者闭环

顺序：

1. `POST /athena-designer/word/observerSave`
2. `POST /athena-designer/word/observerQuery`
3. `POST /athena-designer/word/observerDelete`

关键约束：

- `observerSave` 消费 `word` 闭环缓存的真实 `wordId`

缓存建议：

- `word_ai_observer_id`

### 3.5 主闭环 E：实体类型 + 同义词闭环

顺序：

1. `POST /athena-designer/entityType/insertSysEntity`
2. `GET /athena-designer/entityType/getPage`
3. `GET /athena-designer/entityType/getList`
4. `POST /athena-designer/synonym/creatOrUpdate`
5. `POST /athena-designer/synonym/getList`
6. `POST /athena-designer/synonym/checkSynonym`
7. `POST /athena-designer/synonym/delete`
8. `POST /athena-designer/entityType/deleteSys`

关键约束：

- 先新增实体类型，再新增依赖该实体类型名称的同义词
- 同义词删除必须消费查询返回的真实 `objectId`
- 实体类型删除放在同义词删除之后

缓存建议：

- `word_ai_entity_type_name`
- `word_ai_entity_type_id`
- `word_ai_synonym_proper_noun`
- `word_ai_synonym_id`

## 4. 接口分级建议

### 4.1 A 类：优先直接进入稳定集

- `POST /athena-designer/word/categorySave`
- `POST /athena-designer/word/categoryQuery`
- `POST /athena-designer/word/categoryDelete`
- `POST /athena-designer/word/featureSave`
- `POST /athena-designer/word/featureQuery`
- `POST /athena-designer/word/featureDelete`
- `POST /athena-designer/word/wordSave`
- `POST /athena-designer/word/wordQuery`
- `POST /athena-designer/word/wordDelete`
- `POST /athena-designer/word/observerSave`
- `POST /athena-designer/word/observerQuery`
- `POST /athena-designer/word/observerDelete`
- `POST /athena-designer/entityType/insertSysEntity`
- `GET /athena-designer/entityType/getPage`
- `GET /athena-designer/entityType/getList`
- `POST /athena-designer/entityType/deleteSys`
- `POST /athena-designer/synonym/creatOrUpdate`
- `POST /athena-designer/synonym/getList`
- `POST /athena-designer/synonym/checkSynonym`
- `POST /athena-designer/synonym/delete`

### 4.2 B 类：后续可补

- `POST /athena-designer/synonym/update`
- `POST /athena-designer/synonym/download`
- `GET /athena-designer/synonym/templateDownload`
- `POST /athena-designer/synonym/uploadData`
- `GET /athena-designer/synonym/downloadError`

### 4.3 C 类：暂缓

- 文件上传下载链
- 与外部模板、Excel 导入导出强耦合的接口

## 5. YAML 落地建议

本批建议一次性写入 `ai_inquiry.yaml`，但按 6 条小闭环顺序组织，不要打成单一大链。

推荐执行顺序：

1. 分类闭环
2. 特征闭环
3. 单词闭环
4. 观察者闭环
5. 实体类型 + 同义词闭环
