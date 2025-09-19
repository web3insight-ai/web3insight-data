"""
Author: Justin
Date: 2025-09-19 14:27:31
filename:
version:
Description:
LastEditTime: 2025-09-01 14:27:33
"""

import os
import pandas as pd
from glob import glob

# 路径设置
RAW_DIR = "./data_raw"
CLEAN_DIR = "./data_clean"
os.makedirs(CLEAN_DIR, exist_ok=True)


### 1. 处理 actors 节点 ###
def clean_actors():
    df = pd.read_csv(f"{RAW_DIR}/actors.csv")
    df.rename(
        columns={
            "id": "actor_id:ID(Actor)",
            "login": "login",
            "type": "type",
            "site_admin": "site_admin",
        },
        inplace=True,
    )
    df.to_csv(f"{CLEAN_DIR}/actors_neo4j_node.csv", index=False)
    print("✅ actors cleaned")


### 2. 处理 repos 节点 ###
def clean_repos():
    df = pd.read_csv(f"{RAW_DIR}/repos.csv")
    df.rename(columns={"id": "repo_id:ID(Repo)", "name": "name"}, inplace=True)
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


if __name__ == "__main__":
    clean_actors()
    clean_repos()
    clean_events_split()
    print("🎉 All done!")
