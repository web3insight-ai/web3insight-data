#!/usr/bin/env python3
"""
@Author: Justin
@Date: 2025-09-27
@Filename: 3.clean.py
# @version: 1.2
@Description: gharchive 清洗脚本（字段标准化 + 并行 + 多级目录支持）
@Version: 2.0
"""

import os
import json
import argparse
from multiprocessing import Pool
from datetime import datetime

# ========= 路径配置 =========
INPUT_BASE = "../Data/extracted"
OUTPUT_BASE = "../Data/cleaned"
LOG_DIR = "../Data/logs"
LOG_FILE = os.path.join(LOG_DIR, "clean.log")
os.makedirs(LOG_DIR, exist_ok=True)


# ========= 日志输出 =========
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ========= 清洗逻辑 =========
def clean_event(event):
    try:
        if event.get("actor", {}).get("login") is None:
            return None
        if event.get("type") == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            if not commits:
                return None
        event["actor_login"] = event["actor"]["login"]
        event["repo_name"] = event["repo"]["name"]
        if "gravatar_id" in event["actor"] and not event["actor"]["gravatar_id"]:
            del event["actor"]["gravatar_id"]
        return event
    except:
        return None


# ========= 清洗单文件 =========
def clean_file(input_path, output_path):
    if os.path.exists(output_path):
        log(f"⏭️ 已存在，跳过：{output_path}")
        return

    cleaned = []
    try:
        with open(input_path, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    result = clean_event(event)
                    if result:
                        cleaned.append(result)
                except:
                    continue

        if cleaned:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as fout:
                for e in cleaned:
                    fout.write(json.dumps(e) + "\n")
            log(f"✅ 清洗完成：{output_path}（保留 {len(cleaned)} 条）")
        else:
            log(f"⚠️ 无有效数据：{input_path}")

    except Exception as e:
        log(f"❌ 处理失败：{input_path}，错误：{e}")


# ========= 用于并行处理 =========
def worker_file(pair):
    input_path, output_path = pair
    clean_file(input_path, output_path)


# ========= 文件路径收集 =========
def collect_file_pairs(input_root, output_root):
    file_pairs = []
    for root, _, files in os.walk(input_root):
        for fname in files:
            if fname.endswith(".json"):
                rel_path = os.path.relpath(os.path.join(root, fname), input_root)
                input_path = os.path.join(input_root, rel_path)
                output_path = os.path.join(
                    output_root, rel_path.replace(".json", ".cleaned.json")
                )
                file_pairs.append((input_path, output_path))
    return file_pairs


# ========= CLI帮助信息 =========
def show_help():
    print(
        f"""
用法:
  python 3.clean.py [选项]

选项:
  -f <file.json>         清洗指定单个文件
  -d <YYYY/MM/DD>        清洗指定日期（例如 2025/09/01）
  -m <YYYY/MM>           清洗指定月份目录
  -y <YYYY>              清洗指定年份目录
  -j <N>                 并行任务数（默认 4）
  -h                     显示帮助信息

默认路径:
  输入目录:   {INPUT_BASE}
  输出目录:   {OUTPUT_BASE}
  日志文件:   {LOG_FILE}

示例:
  python 3.clean.py -f 2025/09/01/2025-09-01-12.json
  python 3.clean.py -d 2025/09/01
  python 3.clean.py -m 2025/09
  python 3.clean.py -y 2025
  python 3.clean.py -d 2025/09/01 -j 8
"""
    )


# ========= 主入口 =========
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-f", type=str, help="单个文件路径（相对路径）")
    parser.add_argument("-d", type=str, help="某日目录")
    parser.add_argument("-m", type=str, help="某月目录")
    parser.add_argument("-y", type=str, help="某年目录")
    parser.add_argument("-j", type=int, default=4, help="并行进程数")
    parser.add_argument("-h", action="store_true", help="显示帮助")

    args = parser.parse_args()

    if args.h:
        show_help()
        return

    file_pairs = []

    if args.f:
        rel_path = args.f
        input_path = os.path.join(INPUT_BASE, rel_path)
        output_path = os.path.join(
            OUTPUT_BASE, rel_path.replace(".json", ".cleaned.json")
        )
        clean_file(input_path, output_path)
        return

    elif args.d or args.m or args.y:
        if args.d:
            sub_dir = args.d
        elif args.m:
            sub_dir = args.m
        elif args.y:
            sub_dir = args.y

        input_root = os.path.join(INPUT_BASE, sub_dir)
        output_root = os.path.join(OUTPUT_BASE, sub_dir)
        file_pairs = collect_file_pairs(input_root, output_root)

        log(f"📦 共 {len(file_pairs)} 个文件，将使用 {args.j} 进程清洗")
        with Pool(processes=args.j) as pool:
            pool.map(worker_file, file_pairs)
    else:
        show_help()


if __name__ == "__main__":
    main()
