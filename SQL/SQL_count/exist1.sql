WITH ecosystem_list AS (SELECT UNNEST(ARRAY ['Ethereum','Solana']::text[]) AS ecosystem_name),
     ecosystem_repos AS (SELECT e.ecosystem_name,
                                r.repo_id
                         FROM ecosystem_list e
                                  JOIN
                              web3.repos r ON r.upstream_marks ? e.ecosystem_name),

     actor_first_activity AS (SELECT er.ecosystem_name,
                                     ev.actor_id,
                                     MIN(ev.created_at) AS first_activity_time
                              FROM ecosystem_repos er
                                       JOIN web3.event ev ON ev.repo_id = er.repo_id
                              GROUP BY er.ecosystem_name, ev.actor_id),

     active_dev_ids AS (SELECT er.ecosystem_name,
                               ev.actor_id
                        FROM ecosystem_repos er
                                 JOIN web3.event ev ON ev.repo_id = er.repo_id

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

SELECT el.ecosystem_name     AS ecosystem,
       COALESCE(tp.count, 0) AS total_actors,
       COALESCE(ap.count, 0) AS recent_active_actors,
       COALESCE(nd.count, 0) AS new_developers_90days
FROM ecosystem_list el
         LEFT JOIN total_participants tp ON el.ecosystem_name = tp.ecosystem_name
         LEFT JOIN active_participants ap ON el.ecosystem_name = ap.ecosystem_name
         LEFT JOIN new_developers nd ON el.ecosystem_name = nd.ecosystem_name;