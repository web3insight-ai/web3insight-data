#!/bin/bash
set -e

###
# @Author: Justin
# @Date: 2025-07-19
# @filename: 1.gharchive_downloader.sh
# @version: 1.2
# @Description: gharchive数据下载脚本（macOS + Linux 兼容版，含日志）
 # @LastEditTime: 2025-09-27 20:44:17
###

RAW_DIR="../Data/raw"
LOG_DIR="../Data/logs"
LOG_FILE="$LOG_DIR/gharchive_download.log"
BASE_URL="https://data.gharchive.org"
RETRIES=3

mkdir -p "$LOG_DIR"

log_msg() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检测系统类型（macOS vs Linux）
IS_MACOS=false
if [[ "$(uname)" == "Darwin" ]]; then
  IS_MACOS=true
fi

# 将 YYYY-MM-DD 转换为 Unix 时间戳（兼容 macOS 和 Linux）
to_timestamp() {
  if $IS_MACOS; then
    date -jf "%Y-%m-%d" "$1" +%s
  else
    date -d "$1" +%s
  fi
}

# 日期加一天（返回 YYYY-MM-DD）
add_one_day() {
  if $IS_MACOS; then
    date -v+1d -jf "%Y-%m-%d" "$1" +"%Y-%m-%d"
  else
    date -d "$1 + 1 day" +"%Y-%m-%d"
  fi
}

# 下载某天的数据
download_day() {
  date="$1"
  year=$(echo "$date" | cut -d- -f1)
  month=$(echo "$date" | cut -d- -f2)
  day=$(echo "$date" | cut -d- -f3)

  day_dir="$RAW_DIR/$year/$month/$day"
  mkdir -p "$day_dir"

  for hour in $(seq 0 23); do
    filename="$date-$hour.json.gz"
    url="$BASE_URL/$filename"
    outpath="$day_dir/$filename"

    if [ -f "$outpath" ]; then
      echo "已存在：$outpath，跳过。"
      log_msg "SKIP   $outpath 已存在"
    else
      echo "下载中：$url"
      success=false
      for attempt in $(seq 1 $RETRIES); do
        if curl -C - -s -o "$outpath" "$url"; then
          echo "下载完成：$outpath"
          log_msg "SUCCESS $url -> $outpath"
          success=true
          break
        else
          log_msg "RETRY  ($attempt) $url 失败"
          sleep 1
        fi
      done
      if ! $success; then
        echo "❌ 下载失败：$url"
        log_msg "FAILED $url"
      fi
    fi
  done
}

# 下载日期范围
download_range() {
  start_date="$1"
  end_date="$2"

  current="$start_date"
  while [ "$(to_timestamp "$current")" -le "$(to_timestamp "$end_date")" ]; do
    download_day "$current"
    current=$(add_one_day "$current")
  done
}

# 帮助信息
print_help() {
  echo "用法：$0 [选项]"
  echo "选项："
  echo "  --all                             下载全部数据（修改脚本内年份范围）"
  echo "  --from YYYY-MM-DD --to YYYY-MM-DD    下载指定日期范围"
  echo "  --help                            显示帮助信息"
  echo ""
  echo "示例："
  echo "  $0 --from 2025-09-01 --to 2025-09-03"
  echo "  # 下载 2025 年 9 月 1 日 到 9 月 3 日（含）的 gharchive 数据"
}

# 参数处理
if [ "$1" = "--all" ]; then
  for year in $(seq 2015 2015); do  # ❗修改年份范围
    for month in $(seq -w 1 12); do
      for day in $(seq -w 1 31); do
        date="$year-$month-$day"
        if $IS_MACOS; then
          if date -jf "%Y-%m-%d" "$date" +%Y &>/dev/null; then
            download_day "$date"
          fi
        else
          if date -d "$date" &>/dev/null; then
            download_day "$date"
          fi
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