-- P1: Product health funnel (DuckDB / BigQuery-friendly SQL)
-- Grain: signup cohort -> activation -> feature adoption -> retention

WITH users AS (
  SELECT * FROM users
),
activated AS (
  SELECT user_id, MIN(event_ts) AS activated_at
  FROM events
  WHERE event_name = 'activation_success'
  GROUP BY 1
),
adopted AS (
  SELECT DISTINCT user_id
  FROM events
  WHERE event_name = 'feature_used'
),
retained AS (
  SELECT
    user_id,
    MAX(CASE WHEN properties_json LIKE '%"retention_day":1%' THEN 1 ELSE 0 END) AS retained_d1,
    MAX(CASE WHEN properties_json LIKE '%"retention_day":7%' THEN 1 ELSE 0 END) AS retained_d7,
    MAX(CASE WHEN properties_json LIKE '%"retention_day":30%' THEN 1 ELSE 0 END) AS retained_d30
  FROM events
  WHERE event_name = 'session_start'
  GROUP BY 1
),
user_flags AS (
  SELECT
    u.user_id,
    u.signup_date,
    u.acquisition_channel,
    u.experiment_variant,
    CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END AS activated,
    CASE WHEN d.user_id IS NOT NULL THEN 1 ELSE 0 END AS adopted_any_feature,
    COALESCE(r.retained_d1, 0) AS retained_d1,
    COALESCE(r.retained_d7, 0) AS retained_d7,
    COALESCE(r.retained_d30, 0) AS retained_d30
  FROM users u
  LEFT JOIN activated a ON u.user_id = a.user_id
  LEFT JOIN adopted d ON u.user_id = d.user_id
  LEFT JOIN retained r ON u.user_id = r.user_id
)
SELECT
  COUNT(*) AS signups,
  AVG(activated) AS activation_rate,
  AVG(adopted_any_feature) AS adoption_rate,
  AVG(retained_d1) AS d1_retention,
  AVG(retained_d7) AS d7_retention,
  AVG(retained_d30) AS d30_retention
FROM user_flags;
