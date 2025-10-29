-- 查询最多参与仓库的开发者
-- 排除了bot
MATCH (actor :actors) - [r:event] ->()
WHERE
    NOT actor.actor_login CONTAINS '[bot]' RETURN actor.actor_login,
    COUNT(r) AS repo_count
ORDER BY
    repo_count DESC
LIMIT
    15;

-- 查询被最多开发者参与的仓库
-- 排除了bot
MATCH () - [r:event] ->(repo :repos)
WHERE
    NOT repo.repo_name CONTAINS '[bot]' RETURN repo.repo_name,
    COUNT(r) AS actor_count
ORDER BY
    actor_count DESC
LIMIT
    15;

-- 查询某个开发者参与的所有仓库 前十个 以 samczsun 为例子
MATCH (actor :actors { actor_login: 'samczsun' }) - [r:event] ->(repo :repos) RETURN repo.repo_name,
COUNT(r) AS event_count
ORDER BY
    event_count DESC
LIMIT
    10;

-- 查询某个仓库被哪些开发者参与 前十个 以 bitcoin/bitcoin 为例子
MATCH (actor :actors) - [r:event] ->(repo :repos { repo_name: 'bitcoin/bitcoin' })
WHERE
    NOT actor.actor_login CONTAINS '[bot]' RETURN actor.actor_login,
    COUNT(r) AS event_count
ORDER BY
    event_count DESC
LIMIT
    15;

-- 统计 近一年来的活跃开发者
MATCH (actor :actors) - [e:event] ->()
WHERE
    e.event_type = 'PullRequestEvent'
    AND e.created_at >= datetime().epochMillis - duration('P1Y').toMillis()
    AND e.payload CONTAINS '"action":"opened"'
    AND e.payload CONTAINS '"type":"User"'
    AND NOT actor.actor_login CONTAINS '[bot]' WITH actor.actor_id AS actor_id,
    toString(e.created_at.year) + '-' + lpad(toString(e.created_at.month), 2, '0') AS year_month WITH actor_id,
    COUNT(DISTINCT year_month) AS active_months
WHERE
    active_months >= 9 RETURN actor_id,
    active_months
ORDER BY
    active_months DESC
LIMIT
    15;


MATCH (n) WITH n LIMIT 10
MATCH (n)-[r]->(m) RETURN n, r, m;

