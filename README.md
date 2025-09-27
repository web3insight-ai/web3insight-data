# Web3Insights-data

本项目用于挖掘 Web3 开发者生态的图数据库分析项目，涵盖 GHArchive 数据处理、PostgreSQL 结构建模、Neo4j 图分析与聚类、中心性评估等功能。
## 目录结构

- `Data` : 数据获取与初步处理脚本
- `Data_process` : 数据清洗与预处理脚本
  - `for_neo4j` : 专用于 Neo4j 的数据处理与导入脚本
- `doc` : 设计说明与处理思路
- `SQL` : SQL 查询与分析脚本
  - `Neo4j` : Neo4j 图数据库查询脚本
  - `SQL_count` : PostgreSQL 数据库查询脚本
  - `SQL_with_graph` : 结合图数据的 SQL 查询脚本
  - `SQL_with_normalization` : 结合归一化处理的 SQL 查询脚本
- `test` : 测试脚本


## 核心功能
1. 下载数据：参考 `Data/gharchive_downloader.sh`
2. 清洗数据：参考 `Data_process/data_process_for_one.ipynb`
3. 导入Neo4j：参考 `Data_process/for_neo4j`
4. 图数据分析：参考 `SQL/Neo4j`
5. PGSQL数据分析：参考 `SQL`
