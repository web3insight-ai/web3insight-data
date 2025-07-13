-- 查询所有的数据库
SELECT datname FROM pg_database WHERE datistemplate = false;

-- 查询data数据库的信息 有哪些表
SELECT schema_name
FROM information_schema.schemata;

-- 查询web3 schema 的信息
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'web3';

-- 查看 web3.repos表 具体的字段信息
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'web3' AND table_name = 'repos';

-- 查看 web3.event表 具体的字段信息
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'web3' AND table_name = 'event';

-- 查看 web3.actors表 具体的字段信息
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'web3' AND table_name = 'actors';

SELECT repo_name FROM web3.repos LIMIT 10;


-- 熟悉event表
-- 查询 web3.event 表中前5个 字段
SELECT actor_login, repo_name, event_type, created_at
FROM web3.event
ORDER BY created_at DESC
LIMIT 5;

-- 查询 web3.event 表中每种 event_type 的数量
SELECT event_type, COUNT(*) AS count
FROM web3.event
GROUP BY event_type
ORDER BY count DESC;

SELECT actor_login, event_type, created_at
FROM web3.event
WHERE repo_name = 'ethereum/ERCs'
ORDER BY created_at DESC
LIMIT 20;

-- 找出在某个生态系统（如 Ethereum）中最活跃的开发者
SELECT e.actor_login, COUNT(*) AS event_count
FROM web3.event e
JOIN web3.repos r ON e.repo_id = r.repo_id
WHERE 'Ethereum' = ANY(r.eco_names)
GROUP BY e.actor_login
ORDER BY event_count DESC
LIMIT 10;

SELECT tablename
FROM pg_tables
WHERE schemaname = 'web3';


SELECT
    e.actor_login,
    COUNT(*) AS event_count
FROM
    web3.event e
JOIN
    web3.repos r ON e.repo_id = r.repo_id
WHERE
    'Ethereum' = ANY(r.eco_names)
GROUP BY
    e.actor_login
ORDER BY
    event_count DESC
LIMIT 10;