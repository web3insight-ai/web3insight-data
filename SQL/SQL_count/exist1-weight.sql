WITH weight_config AS (
--     这里写死固定的 权重 用来测试
    SELECT 0.5::numeric AS weight_total,
           0.2::numeric AS weight_active,
           0.3::numeric AS weight_new),
     ecosystem_list
         AS (SELECT UNNEST(ARRAY ['Ethereum','Solana','Bitcoin','Hardhat','Solidity','Polygon','Truffle','IPFS','Sui']::text[]) AS ecosystem_name),
     ecosystem_repos AS (SELECT e.ecosystem_name,
                                r.repo_id
                         FROM ecosystem_list e
                                  JOIN web3.repos r
                                       ON r.upstream_marks ? e.ecosystem_name),
     actor_first_activity AS (SELECT er.ecosystem_name,
                                     ev.actor_id,
                                     MIN(ev.created_at) AS first_activity_time
                              FROM ecosystem_repos er
                                       JOIN web3.event ev
                                            ON ev.repo_id = er.repo_id
                              GROUP BY er.ecosystem_name, ev.actor_id),
     active_dev_ids AS (SELECT er.ecosystem_name,
                               ev.actor_id
                        FROM ecosystem_repos er
                                 JOIN web3.event ev
                                      ON ev.repo_id = er.repo_id
                        WHERE ev.event_type IN ('PullRequestEvent', 'PushEvent')
                          AND ev.created_at >= NOW() - INTERVAL '3 years'
                        GROUP BY er.ecosystem_name, ev.actor_id
                        HAVING COUNT(DISTINCT ev.event_type) = 2),
     total_participants AS (SELECT ecosystem_name,
                                   COUNT(DISTINCT actor_id) AS count
                            FROM actor_first_activity
                            GROUP BY ecosystem_name),
     active_participants AS (SELECT ecosystem_name,
                                    COUNT(DISTINCT actor_id) AS count
                             FROM active_dev_ids
                             GROUP BY ecosystem_name),
     new_developers AS (SELECT ecosystem_name,
                               COUNT(DISTINCT actor_id) AS count
                        FROM actor_first_activity
                        WHERE first_activity_time >= NOW() - INTERVAL '90 days'
                        GROUP BY ecosystem_name)
SELECT el.ecosystem_name                       AS ecosystem,
       COALESCE(tp.count, 0)                   AS total_actors,
       COALESCE(ap.count, 0)                   AS recent_active_actors,
       COALESCE(nd.count, 0)                   AS new_developers_90days,
       (COALESCE(tp.count, 0) * wc.weight_total +
        COALESCE(ap.count, 0) * wc.weight_active +
        COALESCE(nd.count, 0) * wc.weight_new) AS weighted_score
FROM ecosystem_list el
         LEFT JOIN total_participants tp ON el.ecosystem_name = tp.ecosystem_name
         LEFT JOIN active_participants ap ON el.ecosystem_name = ap.ecosystem_name
         LEFT JOIN new_developers nd ON el.ecosystem_name = nd.ecosystem_name
         CROSS JOIN weight_config wc
ORDER BY weighted_score DESC
LIMIT 5;