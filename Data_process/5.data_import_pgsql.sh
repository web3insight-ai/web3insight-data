#!/bin/bash
set -e
###
 # @Author: Justin
 # @Date: 2025-08-27 21:26:11
 # @filename: 5.data_import_pgsql.sh
 # @version: 1.0
 # @Description: 数据导入脚本，将结构化数据导入 PostgreSQL 数据库
 # @LastEditTime: 2025-09-27 21:26:12
### 

# ========== 路径定义 ==========
STRUCTURED_DIR="../Data/structured"
LOG_DIR="../Data/logs"
LOG_FILE="$LOG_DIR/pgsql_import.log"
mkdir -p "$LOG_DIR"

# ========== 数据库配置 ==========
DB_NAME="web3"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
SCHEMA="web3"

# ========== 表结构映射 ==========
declare -A TABLE_DIRS=(
  ["actors"]="actors"
  ["repos"]="repos"
  ["events"]="events"
)

# ========== 帮助信息 ==========
print_help() {
  echo "用法：$0 [选项]"
  echo "选项："
  echo "  --dry-run         仅打印 SQL，不执行导入"
  echo "  -h, --help        显示帮助信息"
}

# ========== 执行 COPY 命令 ==========
import_csv() {
  table="$1"
  csv_file="$2"

  log_entry="[$(date '+%F %T')] 导入 $csv_file 到表 $SCHEMA.$table"
  echo -e "\033[0;32m✔\033[0m $log_entry"
  echo "$log_entry" >> "$LOG_FILE"

  psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" <<EOF
\copy $SCHEMA.$table FROM '$csv_file' WITH (FORMAT csv, HEADER true)
EOF
}

# ========== 参数解析 ==========
DRY_RUN=0
for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=1
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
  esac
done

# ========== 导入逻辑 ==========
for table in "${!TABLE_DIRS[@]}"; do
  dir="$STRUCTURED_DIR/${TABLE_DIRS[$table]}"
  if [[ -d "$dir" ]]; then
    find "$dir" -type f -name '*.csv' | sort | while read -r csv_file; do
      if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "DRY-RUN: Would import $csv_file to table $table"
      else
        import_csv "$table" "$csv_file"
      fi
    done
  else
    echo -e "\033[0;33m⚠\033[0m 目录不存在：$dir"
  fi
done