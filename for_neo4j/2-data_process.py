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

os.makedirs(CLEAN_DIR, exist_ok=True)


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
    # 检查缺失节点文件
    missing_repo_file = os.path.join(CLEAN_DIR, "missing_repo_ids.txt")
    missing_actor_file = os.path.join(CLEAN_DIR, "missing_actor_ids.txt")
    missing_repo_set = set()
    missing_actor_set = set()
    if os.path.exists(missing_repo_file):
        with open(missing_repo_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    missing_repo_set.add(line)
    if os.path.exists(missing_actor_file):
        with open(missing_actor_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    missing_actor_set.add(line)
    if missing_repo_set:
        print(
            f"🔍 检测到 {len(missing_repo_set)} 个缺失 repo_id，将在 clean 时过滤相关边。"
        )
    else:
        print("✅ 未检测到缺失 repo_id。")
    if missing_actor_set:
        print(
            f"🔍 检测到 {len(missing_actor_set)} 个缺失 actor_id，将在 clean 时过滤相关边。"
        )
    else:
        print("✅ 未检测到缺失 actor_id。")
    # 类型异常
    illegal_actor_file = os.path.join(CLEAN_DIR, "illegal_actor_id_events.txt")
    illegal_repo_file = os.path.join(CLEAN_DIR, "illegal_repo_id_events.txt")
    illegal_actor_set = set()
    illegal_repo_set = set()
    if os.path.exists(illegal_actor_file):
        with open(illegal_actor_file) as f:
            illegal_actor_set = set(line.strip() for line in f)
    if os.path.exists(illegal_repo_file):
        with open(illegal_repo_file) as f:
            illegal_repo_set = set(line.strip() for line in f)

    for file in sorted(glob(f"{RAW_DIR}/events_*.csv")):
        df = pd.read_csv(file, low_memory=False)
        before = len(df)
        df = df[
            [
                "id",
                "actor_id",
                "repo_id",
                "org_id",
                "org_login",
                "event_type",
                "abnormal",
                "created_at",
            ]
        ]
        # 字段重命名
        df.rename(
            columns={
                "id": "event_id",
                "actor_id": ":START_ID(Actor)",
                "repo_id": ":END_ID(Repo)",
            },
            inplace=True,
        )
        # 过滤异常 event（event_id 类型问题 或 两端缺失 node）
        if (
            not illegal_actor_set
            and not illegal_repo_set
            and not missing_repo_set
            and not missing_actor_set
        ):
            # 没有任何异常，直接保留所有
            pass
        else:
            # 过滤掉异常事件
            df = df[
                ~df["event_id"].astype(str).isin(illegal_actor_set | illegal_repo_set)
            ]
            if missing_repo_set:
                df = df[~df[":END_ID(Repo)"].astype(str).isin(missing_repo_set)]
            if missing_actor_set:
                df = df[~df[":START_ID(Actor)"].astype(str).isin(missing_actor_set)]
        after = len(df)
        df[":TYPE"] = "INTERACTS_WITH"
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
        basename = os.path.basename(file).replace("events_", "event_repo_edge_")
        out_path = os.path.join(CLEAN_DIR, basename)
        df.to_csv(out_path, index=False)
        print(f"✅ cleaned: {basename}（原始 {before} 条，过滤后 {after} 条）")
    print("🎉 All events cleaned and saved as legal edges in data_edgeclean/.")


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


def is_int_str(x):
    try:
        # 必须是整数
        intx = int(str(x))
        # 防止'123.0'这种通过
        return str(x).strip().isdigit() or str(intx) == str(x).strip()
    except:
        return False


def check_types():
    illegal_actor_events = set()
    illegal_repo_events = set()
    for file in sorted(glob(f"{RAW_DIR}/events_*.csv")):
        df = pd.read_csv(file, low_memory=False)
        # 找出 :START_ID(Actor)/actor_id 非整数行
        if "actor_id" in df.columns:
            bad_actor = df[~df["actor_id"].apply(is_int_str)]
            if not bad_actor.empty:
                illegal_actor_events.update(bad_actor["id"].astype(str).tolist())
                print(
                    f"{os.path.basename(file)} 有 {len(bad_actor)} 条 actor_id 类型非法"
                )
        if "repo_id" in df.columns:
            bad_repo = df[~df["repo_id"].apply(is_int_str)]
            if not bad_repo.empty:
                illegal_repo_events.update(bad_repo["id"].astype(str).tolist())
                print(
                    f"{os.path.basename(file)} 有 {len(bad_repo)} 条 repo_id 类型非法"
                )
    # 保存到文件
    with open(os.path.join(CLEAN_DIR, "illegal_actor_id_events.txt"), "w") as f:
        for eid in sorted(illegal_actor_events):
            f.write(eid + "\n")
    with open(os.path.join(CLEAN_DIR, "illegal_repo_id_events.txt"), "w") as f:
        for eid in sorted(illegal_repo_events):
            f.write(eid + "\n")
    print(
        f"已保存非法 actor_id 事件 {len(illegal_actor_events)} 条，repo_id 事件 {len(illegal_repo_events)} 条。"
    )


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
        elif step == "check_types":
            check_types()
        else:
            print_usage()
