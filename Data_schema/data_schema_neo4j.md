## Neo4j 图数据库结构定义

本节定义图数据库（Neo4j）中各类节点与边的数据结构，基于 PostgreSQL 中的 `actors`、`repos` 和 `events` 三张表进行转换和映射。详细的映射代码请参考 `for_neo4j/2-data_process.py`。

---

### Actor 节点（Actor）

| 字段名        | 类型   | 描述                     |
|---------------|--------|--------------------------|
| `actor_id`    | ID     | 节点唯一标识（从 PG 表 id 转换） |
| `login`       | Text   | 用户名（login）           |
| `type`        | Text   | 用户类型（一般为 User 或 Bot） |
| `site_admin`  | Bool   | 是否为站点管理员         |

**Neo4j 节点定义格式（CSV 中）**：
```
actor_id:ID(Actor),login,type,site_admin
```



### Repo 节点（Repo）

| 字段名       | 类型   | 描述                       |
|--------------|--------|----------------------------|
| `repo_id`    | ID     | 仓库唯一标识（PG 表 id）     |
| `name`       | Text   | 仓库名称（格式为 user/repo） |

**Neo4j 节点定义格式（CSV 中）**：
```
repo_id:ID(Repo),name
```


### INTERACTS_WITH 边（Actor → Repo）

表示用户与仓库之间存在交互行为（如 Watch、Star、Fork、Push 等）。

| 字段名           | 类型        | 描述                      |
|------------------|-------------|---------------------------|
| `event_id`       | bigint      | 原始事件的唯一标识         |
| `:START_ID(Actor)` | ID        | 起点 Actor 节点 ID         |
| `:END_ID(Repo)`    | ID        | 终点 Repo 节点 ID          |
| `actor_login`    | text        | 交互者用户名               |
| `repo_name`      | text        | 仓库名称（user/repo）       |
| `org_id`         | bigint      | 所属组织 ID（可为 null）     |
| `org_login`      | text        | 所属组织名（可为 null）     |
| `event_type`     | text        | 事件类型（PushEvent 等）   |
| `payload`        | json/text   | 原始 payload 内容         |
| `body`           | text        | 评论内容（如 IssueComment） |
| `abnormal`       | int         | 异常标记（0 正常，1 异常）  |
| `created_at`     | timestamp   | 事件发生时间               |
| `:TYPE`          | string      | 固定为 "INTERACTS_WITH"    |

**Neo4j 边定义格式（CSV 中）**：
```
event_id,:START_ID(Actor),actor_login,:END_ID(Repo),repo_name,org_id,org_login,event_type,payload,body,abnormal,created_at,:TYPE
```

