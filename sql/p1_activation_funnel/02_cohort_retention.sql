-- P1: Weekly signup cohort retention

WITH activated AS (
  SELECT user_id, MIN(event_ts) AS activated_at
  FROM events
  WHERE event_name = 'activation_success'
  GROUP BY 1
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
)
SELECT
  DATE_TRUNC('week', CAST(u.signup_date AS DATE)) AS signup_week,
  COUNT(*) AS users,
  AVG(CASE WHEN a.user_id IS NOT NULL THEN 1.0 ELSE 0.0 END) AS activation_rate,
  AVG(COALESCE(r.retained_d1, 0)) AS d1,
  AVG(COALESCE(r.retained_d7, 0)) AS d7,
  AVG(COALESCE(r.retained_d30, 0)) AS d30
FROM users u
LEFT JOIN activated a ON u.user_id = a.user_id
LEFT JOIN retained r ON u.user_id = r.user_id
GROUP BY 1
ORDER BY 1;
