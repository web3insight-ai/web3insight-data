#!/bin/bash
###
# @Author: Justin
# @Date: 2025-09-26
# @filename: test_download_and_decompress.sh
# @version: 1.0
# @Description: 测试 gharchive_downloader.sh + decompress.sh 是否正常工作
###

set -e

# 测试日期
TEST_DATE="2023-01-01"
TEST_HOUR="0"
TEST_FILE="$TEST_DATE-$TEST_HOUR.json.gz"

RAW_DIR="./raw/2023/01/01"
EXTRACTED_DIR="./extracted/2023/01/01"
RAW_PATH="$RAW_DIR/$TEST_FILE"
EXTRACTED_PATH="$EXTRACTED_DIR/${TEST_DATE}-${TEST_HOUR}.json"

echo "🧪 开始测试 GHArchive 数据下载与解压流程"
echo "🔍 测试日期: $TEST_DATE 小时: $TEST_HOUR"

# 清理旧数据
echo "🧹 清理旧数据..."
rm -f "$RAW_PATH" "$EXTRACTED_PATH"

# 步骤 1：下载测试数据
echo "📥 执行下载脚本..."
bash ./Data/gharchive_downloader.sh --from "$TEST_DATE" --to "$TEST_DATE"

if [[ ! -f "$RAW_PATH" ]]; then
    echo "❌ 下载失败：未找到 $RAW_PATH"
    exit 1
fi
echo "✅ 下载成功：$RAW_PATH"

# 步骤 2：解压测试数据
echo "📦 执行解压脚本..."
bash ./Data/decompress.sh -f "$RAW_PATH"

if [[ ! -f "$EXTRACTED_PATH" ]]; then
    echo "❌ 解压失败：未找到 $EXTRACTED_PATH"
    exit 1
fi
echo "✅ 解压成功：$EXTRACTED_PATH"

# 步骤 3：验证 JSON 内容合法性（检查首行是否为合法 JSON）
echo "🔍 验证 JSON 格式..."
head -n 1 "$EXTRACTED_PATH" | jq . >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "❌ 解压后的 JSON 格式不合法"
    exit 1
fi
echo "✅ JSON 格式验证通过"

echo "🎉 所有测试通过！"