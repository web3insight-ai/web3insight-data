"""
Author: Justin
Date: 2025-08-19 14:27:31
filename:
version:
Description:
LastEditTime: 2025-09-01 14:27:33
"""

import os
import sys
import pandas as pd
from glob import glob

# 路径设置
RAW_DIR = "./data/data_raw"
CLEAN_DIR = "./data/data_clean"
EDGECLEAN_DIR = "./data/data_edgeclean"
os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(EDGECLEAN_DIR, exist_ok=True)


### 1. 处理 actors 节点 ###
def clean_actors():
    df = pd.read_csv(f"{RAW_DIR}/actors.csv", low_memory=False)
    # 只保留 id 和 login 两列
    df = df[
        [
            "actor_id",
            "actor_login",
        ]
    ]
    df.rename(
        columns={
            "actor_id": "actor_id:ID(Actor)",
        },
        inplace=True,
    )
    df.to_csv(f"{CLEAN_DIR}/actors_neo4j_node.csv", index=False)
    print("✅ actors cleaned")


### 2. 处理 repos 节点 ###
def clean_repos():
    df = pd.read_csv(f"{RAW_DIR}/repos.csv", low_memory=False)

    df = df[
        [
            "repo_id",
            "repo_name",
            "upstream_marks",
            "created_at",
            "indexed",
        ]
    ]
    df.rename(
        columns={
            "repo_id": "repo_id:ID(Repo)",
        },
        inplace=True,
    )
    df.to_csv(f"{CLEAN_DIR}/repos_neo4j_node.csv", index=False)
    print("✅ repos cleaned")


### 3. 处理 events 边 ###
# 这里的边 是分为了多个文件的，
def clean_events_split():
    for file in sorted(glob(f"{RAW_DIR}/events_*.csv")):
        df = pd.read_csv(file, low_memory=False)
        # 字段重命名
        df.rename(
            columns={
                "id": "event_id",
                "actor_id": ":START_ID(Actor)",
                "repo_id": ":END_ID(Repo)",
            },
            inplace=True,
        )

        # 添加边类型
        df[":TYPE"] = "INTERACTS_WITH"

        # 重排序字段
        reorder = [
            "event_id",
            ":START_ID(Actor)",
            "actor_login",
            ":END_ID(Repo)",
            "repo_name",
            "org_id",
            "org_login",
            "event_type",
            "payload",
            "body",
            "abnormal",
            "created_at",
            ":TYPE",
        ]
        df = df[[col for col in reorder if col in df.columns]]

        # 输出为清洗后的分文件
        basename = os.path.basename(file).replace("events_", "event_repo_edge_")
        out_path = os.path.join(CLEAN_DIR, basename)
        df.to_csv(out_path, index=False)
        print(f"✅ cleaned: {basename}")

    print("🎉 All events cleaned and saved as separate files.")


### 4. 检查 events 边文件是否有引用缺失节点 ###
def check_nodes():
    repo_file = os.path.join(RAW_DIR, "repos.csv")
    actor_file = os.path.join(RAW_DIR, "actors.csv")
    if not os.path.exists(repo_file):
        print(f"❌ repo 节点文件不存在: {repo_file}")
        return
    if not os.path.exists(actor_file):
        print(f"❌ actor 节点文件不存在: {actor_file}")
        return

    repos = pd.read_csv(repo_file, low_memory=False)
    actors = pd.read_csv(actor_file, low_memory=False)
    repo_ids = set(repos["repo_id"])
    actor_ids = set(actors["actor_id"])

    all_missing_repo = set()
    all_missing_actor = set()

    for file in sorted(glob(f"{RAW_DIR}/events_*.csv")):
        df = pd.read_csv(file, low_memory=False)
        # 检查 :END_ID(Repo)
        if "repo_id" in df.columns:
            missing_repo = df.loc[~df["repo_id"].isin(repo_ids), "repo_id"]
            if not missing_repo.empty:
                print(
                    f"❗ 文件 {os.path.basename(file)} 中引用了 {missing_repo.nunique()} 个缺失 repo_id，共 {len(missing_repo)} 条边。"
                )
                print(
                    "   缺失 repo_id 示例: ",
                    list(missing_repo.value_counts().index[:5]),
                )
                all_missing_repo.update(missing_repo.unique())
            else:
                print(f"✅ 文件 {os.path.basename(file)} 无缺失 repo_id。")
        else:
            print(f"⚠️ 文件缺少 :END_ID(Repo) 列: {file}")

        # 检查 :START_ID(Actor)
        if "actor_id" in df.columns:
            missing_actor = df.loc[~df["actor_id"].isin(actor_ids), "actor_id"]
            if not missing_actor.empty:
                print(
                    f"❗ 文件 {os.path.basename(file)} 中引用了 {missing_actor.nunique()} 个缺失 actor_id，共 {len(missing_actor)} 条边。"
                )
                print(
                    "   缺失 actor_id 示例: ",
                    list(missing_actor.value_counts().index[:5]),
                )
                all_missing_actor.update(missing_actor.unique())
            else:
                print(f"✅ 文件 {os.path.basename(file)} 无缺失 actor_id。")
        else:
            print(f"⚠️ 文件缺少 :START_ID(Actor) 列: {file}")

    # 保存所有缺失 repo_id
    if all_missing_repo:
        with open(os.path.join(CLEAN_DIR, "missing_repo_ids.txt"), "w") as f:
            for rid in sorted(all_missing_repo):
                f.write(str(rid) + "\n")
        print(
            f"🔍 所有缺失 repo_id 已保存到 missing_repo_ids.txt，数量: {len(all_missing_repo)}"
        )
    else:
        print("🎉 所有边文件均无引用缺失 repo 节点。")

    # 保存所有缺失 actor_id
    if all_missing_actor:
        with open(os.path.join(CLEAN_DIR, "missing_actor_ids.txt"), "w") as f:
            for aid in sorted(all_missing_actor):
                f.write(str(aid) + "\n")
        print(
            f"🔍 所有缺失 actor_id 已保存到 missing_actor_ids.txt，数量: {len(all_missing_actor)}"
        )
    else:
        print("🎉 所有边文件均无引用缺失 actor 节点。")


def print_usage():
    print(
        "\n用法: python clean.py [step]\n"
        "step 可选: actors | repos | events | check_nodes | all\n"
        "示例: python clean.py check_nodes\n"
    )


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "all":
        clean_actors()
        clean_repos()
        clean_events_split()
        print("🎉 All done!")
    else:
        step = sys.argv[1].lower()
        if step == "actors":
            clean_actors()
        elif step == "repos":
            clean_repos()
        elif step == "events":
            clean_events_split()
        elif step == "check_nodes":
            check_nodes()
        else:
            print_usage()
