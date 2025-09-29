# Web3Insights-data

> 📊 数据管道：清洗、结构化 GitHub 数据，用于 Web3 项目分析

本项目是 [Web3Insights](https://www.gharchive.org/) 数据处理子模块，目标是高质量处理来自 [GHArchive](https://www.gharchive.org/) 的 GitHub 活动数据，构建干净、结构化的 GitHub 行为视图，为恶意行为识别、项目活跃度评估、贡献者分析等后续分析打好数据基础。

---

## 🗂 项目目录结构

```bash
Web3Insights-data/
├── Data/
│   ├── raw/             # 原始压缩文件（*.json.gz）
│   ├── extracted/       # 解压后的原始 JSON 文件
│   ├── cleaned/         # 清洗后的 JSON 文件
│   ├── structured/      # 提取后的结构化数据（CSV）
│   │   ├── actors/
│   │   ├── events/
│   │   └── repos/
│   └── logs/            # 各阶段日志文件
├── Data_process/
│   ├── 1.gharchive_downloader.sh   # 数据下载脚本
│   ├── 2.decompress.sh             # 解压脚本（支持并行）
│   ├── 3.clean.py                  # 清洗脚本（支持并行）
│   └── 4.extract.py                # 数据提取脚本（支持并行）
├── doc/                # 文档说明（可选）
├── json_graphDesign/   # 图数据库设计（Neo4j等）
├── SQL/                # SQL 脚本（结构化分析）
└── README.md           # 当前文件
```

---

## 🔁 数据处理流程

每一步都可以单独执行，支持并行任务、指定日期等参数：

1. **下载数据**  
   使用 `1.gharchive_downloader.sh` 从 GHArchive 下载指定时间段数据（按小时存储为 `.json.gz` 文件）

2. **解压数据**  
   使用 `2.decompress.sh` 将 `.json.gz` 文件解压为 `.json` 文件

3. **清洗数据**  
   使用 `3.clean.py` 过滤无效字段、空值、无效结构等，为后续结构化做准备

4. **提取结构化数据**  
   使用 `4.extract.py` 将每条 JSON 日志提取为：
   - **actors.csv**（开发者信息）
   - **repos.csv**（仓库信息）
   - **events.csv**（交互信息）

---

## 🛠 使用方法

### 下载数据

```bash
cd Data_process
./1.gharchive_downloader.sh --from 2025-09-01 --to 2025-09-02
```

### 解压数据（支持单日、月份、全年）

```bash
./2.decompress.sh -d 2025/09/01     # 解压某天
./2.decompress.sh -m 2025/09        # 解压某月
./2.decompress.sh -y 2025           # 解压某年
```

### 清洗数据（支持并行）

```bash
python3 3.data_clean.py -d 2025/09/01 -j 8
```

### 提取结构化数据

```bash
python3 4.data_extract.py -d 2025/09/01 -j 8
```

输出数据将分别保存至：

```
Data/structured/
├── actors/YYYY/MM/DD.csv
├── repos/YYYY/MM/DD.csv
└── events/YYYY/MM/DD.csv
```

---

## 📄 日志记录

每一步操作都会生成日志，便于调试与回溯：

- `logs/gharchive_download.log`：下载阶段
- `logs/decompress.log`：解压阶段
- `logs/clean.log`：清洗阶段
- `logs/extract.log`：提取阶段

---

## 📌 TODO（后续计划）

- [ ] 标记恶意行为（刷星、垃圾提交等）
- [ ] 引入图数据库（Neo4j）建模与导入
- [ ] 结构化行为网络（共同开发、互动、星标网络等）
- [ ] 模块化封装 CLI 接口

---

## 📄 License

[MIT License](./LICENSE)