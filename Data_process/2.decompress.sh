#!/bin/bash
set -e
###
# @Author: Justin
# @Date: 2025-07-19
# @filename: 2.decompress.sh
# @version: 1.2
# @Description: gharchive 解压缩脚本（macOS+Linux 兼容 + 日志增强）
 # @LastEditTime: 2025-09-27 20:55:23
###

RAW_BASE="../Data/raw"
EXTRACTED_BASE="../Data/extracted"
LOG_DIR="../Data/logs"
LOG_FILE="$LOG_DIR/decompress.log"
JOBS=8 # 默认并行任务数

mkdir -p "$LOG_DIR"

# ANSI颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 清除颜色

show_help() {
    echo -e "${YELLOW}用法:${NC} $0 [选项] <路径>"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo "  -f <file.json.gz>     解压单个 .json.gz 文件"
    echo "  -d <YYYY/MM/DD>       解压指定日期目录"
    echo "  -m <YYYY/MM>          解压指定月份所有目录"
    echo "  -y <YYYY>             解压指定年份所有目录"
    echo "  -j <并行数>            并行任务数（默认 8）"
    echo "  -h                    显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 -d 2025/09/01      解压指定日期的数据"
    echo "  $0 -f ../Data/raw/2025/09/01/2025-09-01-15.json.gz"
}

log() {
    prefix="$1"
    color="$2"
    message="$3"
    echo -e "${color}${prefix}${NC} ${message}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${prefix} ${message}" >> "$LOG_FILE"
}

decompress_one() {
    input="$1"
    output="${input%.gz}"
    if [[ -f "$output" ]]; then
        log "⏭️" "$BLUE" "已存在，跳过：$output"
        return
    fi

    mkdir -p "$(dirname "$output")"
    if gunzip -c "$input" > "$output"; then
        log "✅" "$GREEN" "解压完成：$input → $output"
    else
        log "❌" "$RED" "解压失败：$input"
    fi
}

decompress_dir_parallel() {
    input_dir="$1"
    output_dir="$2"
    log "📁" "$YELLOW" "正在处理目录：$input_dir → $output_dir"

    find "$input_dir" -type f -name '*.json.gz' -print0 | while IFS= read -r -d '' file; do
        relative="${file#$input_dir/}"
        echo "$file:::${output_dir}/${relative%.gz}"
    done | tr '\n' '\0' | xargs -0 -P "$JOBS" -n 1 -I {} bash -c '
        input="${1%%:::*}"
        output="${1##*:::}"
        now=$(date "+%Y-%m-%d %H:%M:%S")

        mkdir -p "$(dirname "$output")"

        if [[ -f "$output" ]]; then
            echo -e "\033[0;34m⏭️\033[0m 已存在，跳过：$output"
            echo "[$now] ⏭️ 已存在，跳过：$output" >> "'"$LOG_FILE"'"
        elif gunzip -c "$input" > "$output" 2>/tmp/gunzip_err.txt; then
            echo -e "\033[0;32m✅\033[0m 解压完成：$input → $output"
            echo "[$now] ✅ 解压完成：$input → $output" >> "'"$LOG_FILE"'"
        else
            errmsg=$(cat /tmp/gunzip_err.txt)
            echo -e "\033[0;31m❌\033[0m 解压失败：$input"
            echo "[$now] ❌ 解压失败：$input" >> "'"$LOG_FILE"'"
            echo "[$now] 🗑️ 删除输出文件：$output，原因：$errmsg" >> "'"$LOG_FILE"'"
            rm -f "$output"
        fi
    ' _ {}
}

# 参数解析
while getopts ":f:d:m:y:j:h" opt; do
    case $opt in
        f)
            decompress_one "$OPTARG"
            exit 0
            ;;
        d)
            decompress_dir_parallel "$RAW_BASE/$OPTARG" "$EXTRACTED_BASE/$OPTARG"
            exit 0
            ;;
        m)
            decompress_dir_parallel "$RAW_BASE/$OPTARG" "$EXTRACTED_BASE/$OPTARG"
            exit 0
            ;;
        y)
            decompress_dir_parallel "$RAW_BASE/$OPTARG" "$EXTRACTED_BASE/$OPTARG"
            exit 0
            ;;
        j)
            JOBS="$OPTARG"
            ;;
        h)
            show_help
            exit 0
            ;;
        \?)
            log "❌" "$RED" "无效选项: -$OPTARG"
            show_help
            exit 1
            ;;
        :)
            log "❌" "$RED" "缺少参数: -$OPTARG"
            show_help
            exit 1
            ;;
    esac
done

show_help
exit 1