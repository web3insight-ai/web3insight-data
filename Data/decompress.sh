###
# @Author: Justin
# @Date: 2025-07-19 14:10:10
# @filename: 
# @version: 
# @Description: 
# @LastEditTime: 2025-07-19 14:10:56
### 
#!/bin/bash
-set -e

RAW_BASE="./raw"
EXTRACTED_BASE="./extracted"
JOBS=8 # 默认并行任务数

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
}

log() {
    prefix="$1"
    color="$2"
    message="$3"
    echo -e "${color}${prefix}${NC} ${message}"
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

    find "$input_dir" -type f -name '*.json.gz' | while read -r file; do
        relative="${file#$input_dir/}"
        echo "$file:::${output_dir}/${relative%.gz}"
    done | xargs -P "$JOBS" -n 1 -d '\n' -I {} bash -c '
        input="${1%%:::*}"
        output="${1##*:::}"
        mkdir -p "$(dirname "$output")"
        if [[ -f "$output" ]]; then
            echo -e "\033[0;34m⏭️\033[0m 已存在，跳过：$output"
        elif gunzip -c "$input" > "$output"; then
            echo -e "\033[0;32m✅\033[0m 解压完成：$input → $output"
        else
            echo -e "\033[0;31m❌\033[0m 解压失败：$input"
        fi
    ' _ {}
}

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