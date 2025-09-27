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
from multiprocessing import Pool
from datetime import datetime

# ========= 路径配置 =========
INPUT_BASE = "../Data/cleaned"
OUTPUT_BASE = "../Data/structured"
LOG_DIR = "../Data/logs"
LOG_FILE = os.path.join(LOG_DIR, "extract.log")
os.makedirs(LOG_DIR, exist_ok=True)


# ========= 日志函数 =========
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ========= 结构提取逻辑 =========
def extract_from_file(input_path, output_prefix):
    actors = {}
    repos = {}
    interactions = []

    try:
        with open(input_path, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    actor = event.get("actor", {})
                    repo = event.get("repo", {})
                    type_ = event.get("type", "")
                    created_at = event.get("created_at", "")

                    # actors
                    aid = actor.get("id")
                    if aid:
                        actors[aid] = actor.get("login", "")

                    # repos
                    rid = repo.get("id")
                    if rid:
                        repos[rid] = repo.get("name", "")

                    # interaction
                    if aid and rid:
                        interactions.append([aid, rid, type_, created_at])
                except:
                    continue

        if not interactions:
            log(f"⚠️ 无交互数据：{input_path}")
            return

        os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

        # 写 actors
        with open(output_prefix + "_actors.csv", "w", newline="") as fa:
            writer = csv.writer(fa)
            writer.writerow(["actor_id", "actor_login"])
            for aid, login in actors.items():
                writer.writerow([aid, login])

        # 写 repos
        with open(output_prefix + "_repos.csv", "w", newline="") as fr:
            writer = csv.writer(fr)
            writer.writerow(["repo_id", "repo_name"])
            for rid, name in repos.items():
                writer.writerow([rid, name])

        # 写 interactions
        with open(output_prefix + "_interactions.csv", "w", newline="") as fi:
            writer = csv.writer(fi)
            writer.writerow(["actor_id", "repo_id", "event_type", "created_at"])
            for row in interactions:
                writer.writerow(row)

        log(f"✅ 提取完成：{input_path} → {output_prefix}_*.csv")

    except Exception as e:
        log(f"❌ 提取失败：{input_path}，错误：{e}")


# ========= 并行 worker =========
def worker(pair):
    input_path, output_prefix = pair
    extract_from_file(input_path, output_prefix)


# ========= 路径扫描 =========
def collect_file_pairs(sub_path):
    input_root = os.path.join(INPUT_BASE, sub_path)
    output_root = os.path.join(OUTPUT_BASE, sub_path)
    file_pairs = []

    for root, _, files in os.walk(input_root):
        for fname in files:
            if fname.endswith(".cleaned.json"):
                rel_path = os.path.relpath(os.path.join(root, fname), input_root)
                input_path = os.path.join(input_root, rel_path)
                rel_no_ext = rel_path.replace(".cleaned.json", "")
                output_prefix = os.path.join(output_root, rel_no_ext)
                file_pairs.append((input_path, output_prefix))

    return file_pairs


# ========= CLI 帮助 =========
def show_help():
    print(
        f"""
用法:
  python 4.extract.py [选项]

选项:
  -f <file.json>         提取单个文件（如 2025/09/01/2025-09-01-15.cleaned.json）
  -d <YYYY/MM/DD>        提取某天目录
  -m <YYYY/MM>           提取某月目录
  -y <YYYY>              提取某年目录
  -j <N>                 并行任务数（默认 4）
  -h                     显示帮助信息

默认路径:
  输入目录:   {INPUT_BASE}
  输出目录:   {OUTPUT_BASE}
  日志文件:   {LOG_FILE}

示例:
  python 4.extract.py -f 2025/09/01/2025-09-01-15.cleaned.json
  python 4.extract.py -d 2025/09/01
  python 4.extract.py -m 2025/09
  python 4.extract.py -y 2025
  python 4.extract.py -d 2025/09/01 -j 8
"""
    )


# ========= 主程序 =========
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-f", type=str, help="单个文件路径")
    parser.add_argument("-d", type=str, help="指定某日目录")
    parser.add_argument("-m", type=str, help="指定某月目录")
    parser.add_argument("-y", type=str, help="指定某年目录")
    parser.add_argument("-j", type=int, default=4, help="并行进程数")
    parser.add_argument("-h", action="store_true", help="显示帮助信息")
    args = parser.parse_args()

    if args.h:
        show_help()
        return

    if args.f:
        rel_path = args.f
        input_path = os.path.join(INPUT_BASE, rel_path)
        output_prefix = os.path.join(OUTPUT_BASE, rel_path.replace(".cleaned.json", ""))
        extract_from_file(input_path, output_prefix)
        return

    sub_path = args.d or args.m or args.y
    if sub_path:
        file_pairs = collect_file_pairs(sub_path)
        log(f"📦 共 {len(file_pairs)} 个文件，将使用 {args.j} 进程提取结构化数据")
        with Pool(processes=args.j) as pool:
            pool.map(worker, file_pairs)
        return

    show_help()


if __name__ == "__main__":
    main()
