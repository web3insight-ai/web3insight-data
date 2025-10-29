## PostgreSQL 表结构定义文档

本节定义 Web3Insights 项目中 PostgreSQL 所使用的三个主要数据表结构：`actors`、`repos`、`events`。所有表均使用结构化字段，支持类型校验、索引优化、并可用于图数据库映射与进一步分析。



## 1. `actors` 表
### 表名

`actors`



### 字段定义

| 字段名        | 类型                        | 说明                          |
|---------------|-----------------------------|-------------------------------|
| `actor_id`    | `bigint`                    | 用户唯一标识符（GitHub 分配的 ID） |
| `actor_login` | `text`                      | 用户登录名（GitHub 用户名）        |
| `created_at`  | `timestamp with time zone`  | 首次被记录入库的时间              |


### 示例数据（仅供参考）

```json
{
  "actor_id": 41898282,
  "actor_login": "github-actions[bot]",
  "created_at": "2025-09-01T00:00:00Z"
}
```


## 2. `repos` 表

### 表名

`repos`

### 字段定义

| 字段名           | 类型                        | 说明                                       |
|------------------|-----------------------------|--------------------------------------------|
| `repo_id`        | `bigint`                    | 仓库唯一标识符（GitHub 分配的 ID）         |
| `repo_name`      | `text`                      | 仓库全名（形式如 `owner/repo`）            |
| `upstream_marks` | `jsonb`                     | 系统自动打标的仓库属性（如 Web3、AI 等）   |
| `custom_marks`   | `jsonb`                     | 用户自定义打标（人工或规则追加的标签）     |
| `indexed`        | `boolean`                   | 是否已被索引（用于数据处理状态标志）       |
| `created_at`     | `timestamp with time zone`  | 仓库首次被记录入库的时间                   |
| `api_updated_at` | `timestamp with time zone`  | 来自 GitHub API 的最后更新时间             |
| `api`            | `jsonb`                     | 原始 GitHub API 数据（完整仓库详情快照）   |

### 示例数据（仅供参考）

```json
{
  "repo_id": 664878753,
  "repo_name": "sibellyvih/sibellyvih",
  "upstream_marks": ["automation", "bot"],
  "custom_marks": ["web3"],
  "indexed": true,
  "created_at": "2025-09-01T00:00:00Z",
  "api_updated_at": "2025-09-01T01:00:00Z",
  "api": {
    "id": 664878753,
    "name": "sibellyvih",
    "owner": {
      "login": "sibellyvih",
      "type": "User"
    },
    "stargazers_count": 0,
    "forks_count": 0,
    "language": "HTML"
  }
}
```



## 3. `events` 表

### 表名

`events`


### 字段定义

| 字段名        | 类型                        | 说明                                              |
|---------------|-----------------------------|---------------------------------------------------|
| `id`          | `bigint`                    | GitHub 事件唯一标识符                              |
| `actor_id`    | `bigint`                    | 发起事件的用户 ID                                  |
| `actor_login` | `text`                      | 发起事件的用户登录名                                |
| `repo_id`     | `bigint`                    | 事件发生的仓库 ID                                  |
| `repo_name`   | `text`                      | 事件发生的仓库名称                                  |
| `org_id`      | `bigint`                    | 所属组织 ID（如有）                                 |
| `org_login`   | `text`                      | 所属组织登录名（如有）                              |
| `event_type`  | `text`                      | GitHub 事件类型（如 `PushEvent`, `ForkEvent` 等）  |
| `payload`     | `json`                      | GitHub 事件的完整原始结构体                         |
| `body`        | `text`                      | （可选）事件正文/提交信息（如 issue 评论内容）       |
| `abnormal`    | `integer`                   | 异常标记（0=正常，1=异常），用于过滤恶意行为等         |
| `created_at`  | `timestamp with time zone`  | 事件发生时间（GitHub 记录时间）                      |


### 示例数据（仅供参考）

```json
{
  "id": 54065642408,
  "actor_id": 41898282,
  "actor_login": "github-actions[bot]",
  "repo_id": 664878753,
  "repo_name": "sibellyvih/sibellyvih",
  "org_id": null,
  "org_login": null,
  "event_type": "PushEvent",
  "payload": { "ref": "refs/heads/output", "size": 1, ... },
  "body": "deploy: f48cdab9f0b7afe273291db1ec1642951f8d1053",
  "abnormal": 0,
  "created_at": "2025-09-01T01:00:00Z"
}
```
---
**说明**：

- 所有时间字段统一为 `timestamp with time zone`，以保证跨时区数据一致性；
- `events` 表中将结构化字段与 `payload` 的半结构化字段共存，以支持灵活查询；
- 数据来源于 GHArchive 清洗后的结果，经过恶意行为标注与结构标准化处理；
- 所有主键字段（如 `actor_id`、`repo_id`、`id`）建议建立索引以优化性能；
- 可根据需求额外添加外键约束、唯一约束或物化视图。

