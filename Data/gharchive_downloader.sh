###
# @Author: Justin
# @Date: 2025-07-19 14:10:10
# @filename: 
# @version: 
# @Description: 
 # @LastEditTime: 2025-07-19 14:11:34
### 
#!/bin/bash
-set -e

RAW_DIR="./raw"
BASE_URL="https://data.gharchive.org"

# 创建三级目录并下载某天所有小时数据
download_day() {
  date="$1"
  year=$(date -d "$date" +%Y)
  month=$(date -d "$date" +%m)
  day=$(date -d "$date" +%d)

  day_dir="$RAW_DIR/$year/$month/$day"
  mkdir -p "$day_dir"

  for hour in $(seq 0 23); do
    filename="$date-$hour.json.gz"
    url="$BASE_URL/$filename"
    outpath="$day_dir/$filename"

    if [ -f "$outpath" ]; then
      echo "已存在：$outpath，跳过。"
    else
      echo "下载中：$url"
      curl -s -o "$outpath" "$url"
    fi
  done
}

# 下载指定日期范围
download_range() {
  start_date="$1"
  end_date="$2"

  current="$start_date"
  while [ "$(date -I -d "$current")" != "$(date -I -d "$end_date + 1 day")" ]; do
    download_day "$current"
    current=$(date -I -d "$current + 1 day")
  done
}

# 帮助信息
print_help() {
  echo "用法：$0 [选项]"
  echo "选项："
  echo "  --all                 下载全部数据（修改脚本内年份范围）"
  echo "  --from YYYY-MM-DD --to YYYY-MM-DD    下载指定日期范围"
  echo "  --help                显示帮助信息"
}

# 参数处理
if [ "$1" = "--all" ]; then
  for year in $(seq 2015 2015); do  # ❗修改年份范围
    for month in $(seq -w 1 12); do
      for day in $(seq -w 1 31); do
        date="$year-$month-$day"
        if date -d "$date" >/dev/null 2>&1; then
          download_day "$date"
        fi
      done
    done
  done
elif [ "$1" = "--from" ] && [ "$3" = "--to" ]; then
  download_range "$2" "$4"
else
  print_help
  exit 1
fi