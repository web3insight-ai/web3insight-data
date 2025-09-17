-- data.actors
DROP TABLE IF EXISTS data.actors;

CREATE TABLE data.actors
(
    actor_id    BIGINT PRIMARY KEY,
    actor_login TEXT,
    created_at  TIMESTAMPTZ NOT NULL
);

-- data.repos
DROP TABLE IF EXISTS data.repos;

CREATE TABLE data.repos
(
    repo_id        BIGINT PRIMARY KEY,
    repo_name      TEXT,
    upstream_marks JSONB,
    custom_marks   JSONB,
    indexed        BOOLEAN,
    created_at     TIMESTAMPTZ,
    api_updated_at TIMESTAMPTZ,
    api            JSONB
);

-- data.events
DROP TABLE IF EXISTS data.events;

CREATE TABLE data.events
(
    id          BIGINT PRIMARY KEY,
    actor_id    BIGINT,
    actor_login TEXT,
    repo_id     BIGINT,
    repo_name   TEXT,
    org_id      BIGINT,
    org_login   TEXT,
    event_type  TEXT,
    payload     JSON,
    body        TEXT,
    abnormal    INTEGER,
    created_at  TIMESTAMPTZ
);

-- data.ecosystems
DROP TABLE IF EXISTS data.ecosystems;

CREATE TABLE data.ecosystems
(
    id          BIGINT PRIMARY KEY,
    name        TEXT,
    icon        TEXT,
    description TEXT,
    active      BOOLEAN,
    created_at  TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ,
    score       NUMERIC,
    kind        TEXT
);