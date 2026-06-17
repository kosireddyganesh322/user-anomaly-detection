-- ============================================================
-- NFC User Anomaly Detection — PostgreSQL Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    user_id     VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(100),
    email       VARCHAR(150),
    role        VARCHAR(100),
    department  VARCHAR(100),
    start_date  DATE
);

CREATE TABLE IF NOT EXISTS ldap_info (
    user_id     VARCHAR(50) PRIMARY KEY REFERENCES users(user_id),
    title       VARCHAR(150),
    manager     VARCHAR(50),
    department  VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS logon_events (
    id          SERIAL PRIMARY KEY,
    event_id    VARCHAR(50),
    event_date  TIMESTAMP,
    user_id     VARCHAR(50) REFERENCES users(user_id),
    pc          VARCHAR(50),
    activity    VARCHAR(20)   -- 'Logon' or 'Logoff'
);

CREATE TABLE IF NOT EXISTS device_events (
    id          SERIAL PRIMARY KEY,
    event_id    VARCHAR(50),
    event_date  TIMESTAMP,
    user_id     VARCHAR(50) REFERENCES users(user_id),
    pc          VARCHAR(50),
    file_tree   TEXT,
    activity    VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS anomaly_scores (
    id             SERIAL PRIMARY KEY,
    user_id        VARCHAR(50) REFERENCES users(user_id),
    scored_at      TIMESTAMP DEFAULT NOW(),
    anomaly_score  FLOAT,
    is_anomaly     BOOLEAN,
    risk_level     VARCHAR(10)   -- LOW / MEDIUM / HIGH / CRITICAL
);

CREATE TABLE IF NOT EXISTS alerts (
    id             SERIAL PRIMARY KEY,
    user_id        VARCHAR(50) REFERENCES users(user_id),
    alert_type     VARCHAR(80),
    severity       VARCHAR(10),
    description    TEXT,
    created_at     TIMESTAMP DEFAULT NOW(),
    acknowledged   BOOLEAN DEFAULT FALSE
);
