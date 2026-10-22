-- 001: plans table — one row per generated website plan.
CREATE TABLE IF NOT EXISTS plans (
    id             CHAR(10)    NOT NULL COMMENT 'Public short id: random, lowercase letters + digits',
    created_at     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    input_json     JSON        NOT NULL COMMENT 'Wizard answers',
    result_json    JSON        NOT NULL COMMENT 'Generated plan',
    engine_version VARCHAR(16) NOT NULL COMMENT 'Rule-engine version that produced the plan',
    PRIMARY KEY (id),
    KEY ix_plans_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
