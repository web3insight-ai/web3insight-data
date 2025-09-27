"""
@Author: Justin
@Date: 2025-07-27 21:15:33
@Filename: 4.extract.py
@Version: 1.1
@Description: 从 .cleaned.json 提取结构化 CSV（actor / repo / interaction）
@LastEditTime: 2025-09-27 21:15:34
"""

import os
import json
import csv
import argparse
import multiprocessing as mp
from datetime import datetime

# ========= 路径配置（集中定义） =========
INPUT_DIR = "../Data/cleaned"
OUTPUT_BASE = "../Data/structured"
LOG_DIR = "../Data/logs"
LOG_FILE = os.path.join(LOG_DIR, "extract.log")
os.makedirs(LOG_DIR, exist_ok=True)


# ========= 日志函数 =========
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    with open(LOG_FILE, "a") as f:
        f.write(full_msg + "\n")


# ========= 处理单个文件 =========
def process_file(input_path):
    try:
        with open(input_path, "r") as f:
            data = json.load(f)

        actors = {}
        repos = {}
        interactions = []

        for event in data:
            actor = event.get("actor", {})
            repo = event.get("repo", {})
            event_type = event.get("type")
            created_at = event.get("created_at")

            actor_id = actor.get("id")
            actor_login = actor.get("login")
            repo_id = repo.get("id")
            repo_name = repo.get("name")

            if actor_id and actor_login:
                actors[actor_id] = actor_login
            if repo_id and repo_name:
                repos[repo_id] = repo_name
            if actor_id and repo_id and event_type and created_at:
                interactions.append([actor_id, repo_id, event_type, created_at])

        # 组织输出路径
        rel_subpath = os.path.relpath(input_path, INPUT_DIR)
        rel_no_ext = rel_subpath.replace(".cleaned.json", "")
        rel_date_path = os.path.dirname(rel_no_ext)
        filename = os.path.basename(rel_no_ext)

        actor_path = os.path.join(
            OUTPUT_BASE, "actors", rel_date_path, f"{filename}.csv"
        )
        repo_path = os.path.join(OUTPUT_BASE, "repos", rel_date_path, f"{filename}.csv")
        interact_path = os.path.join(
            OUTPUT_BASE, "events", rel_date_path, f"{filename}.csv"
        )

        os.makedirs(os.path.dirname(actor_path), exist_ok=True)
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)
        os.makedirs(os.path.dirname(interact_path), exist_ok=True)

        with open(actor_path, "w", newline="") as fa:
            writer = csv.writer(fa)
            writer.writerow(["actor_id", "actor_login"])
            for aid, login in actors.items():
                writer.writerow([aid, login])

        with open(repo_path, "w", newline="") as fr:
            writer = csv.writer(fr)
            writer.writerow(["repo_id", "repo_name"])
            for rid, name in repos.items():
                writer.writerow([rid, name])

        with open(interact_path, "w", newline="") as fi:
            writer = csv.writer(fi)
            writer.writerow(["actor_id", "repo_id", "event_type", "created_at"])
            for row in interactions:
                writer.writerow(row)

        log(f"✅ 提取完成：{input_path}")

    except Exception as e:
        log(f"❌ 处理失败：{input_path}，错误信息：{e}")


# ========= 扫描输入文件 =========
def collect_files_by_pattern(option, value):
    paths = []
    if option == "-f":
        paths.append(value)
    else:
        base = os.path.join(INPUT_DIR, value)
        for root, _, files in os.walk(base):
            for fname in files:
                if fname.endswith(".cleaned.json"):
                    paths.append(os.path.join(root, fname))
    return paths


# ========= 主程序入口 =========
def main():
    parser = argparse.ArgumentParser(
        description="结构化提取：actors、repos、interactions"
    )
    parser.add_argument("-f", help="指定单个文件")
    parser.add_argument("-d", help="指定日期目录（如 2025/09/01）")
    parser.add_argument("-m", help="指定月份目录（如 2025/09）")
    parser.add_argument("-y", help="指定年份目录（如 2025）")
    parser.add_argument("-j", help="并行数，默认 8", default=8, type=int)

    args = parser.parse_args()

    option = None
    value = None
    if args.f:
        option, value = "-f", args.f
    elif args.d:
        option, value = "-d", args.d
    elif args.m:
        option, value = "-m", args.m
    elif args.y:
        option, value = "-y", args.y
    else:
        parser.print_help()
        return

    all_files = collect_files_by_pattern(option, os.path.join(INPUT_DIR, value))
    log(f"📂 共发现 {len(all_files)} 个文件，开始并行提取……")

    with mp.Pool(processes=args.j) as pool:
        pool.map(process_file, all_files)

    log("✅ 全部任务完成")


if __name__ == "__main__":
    main()
