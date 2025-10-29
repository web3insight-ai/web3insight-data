# Web3Insights-data

本项目用于挖掘 Web3 开发者生态的图数据库分析项目，涵盖 GHArchive 数据下载与处理、PostgreSQL 导入与分析、Neo4j 图数据库构建等功能。
##  项目模块概览

本仓库包含以下三个主要部分：

### 1. 数据处理与结构化（`Data_process/`）

- `1.gharchive_downloader.sh`：支持指定日期范围下载 `.json.gz` 原始事件数据；
- `2.decompress.sh`：并行解压原始数据；
- `3.data_clean.py`：清洗单条 JSON，去除空值字段；
- `4.data_extract.py`：提取结构化 CSV 文件：`actors`、`repos`、`events`；
- `5.data_import_pgsql.sh`：一键导入结构化 CSV 至 PostgreSQL；

---

### 2. PostgreSQL 分析查询（`SQL/`）

- `getDataBase/`：数据库初始化与数据导出；
- `SQL_count/`：数据库信息查询等基础操作
- `SQL_with_normalization/`：带有归一化操作的查询语句
- `SQL_with_graph/`：结合图算法的查询语句

---

### 3. Neo4j 图数据构建（`for_neo4j/`）

- `1-export_gharchive.sh`：导出数据为 Neo4j 格式；
- `2-data_process.py`：字段转换处理（含 `.ipynb` 调试）；
- `3-import_neo4j.sh`：自动导入节点和边；
- `cypher/`：图算法脚本如 PageRank、Dijkstra、社区发现等；
- `data/`：中间文件存储与日志。

##   目录结构

``` bash
├── Data/                 # 数据文件
├── Data_process/         # 数据处理脚本
├── SQL/                  # PostgreSQL 查询与分析 SQL
├── for_neo4j/            # Neo4j 数据处理与导入
├── doc/                  # 文档说明
├── test/                 # 脚本测试文件
└── README.md             # 项目说明文件（本文件）
```

