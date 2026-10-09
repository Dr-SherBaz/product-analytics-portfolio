-- P2: Onboarding checklist experiment readout

WITH activated AS (
  SELECT DISTINCT user_id
  FROM events
  WHERE event_name = 'activation_success'
),
adopted AS (
  SELECT DISTINCT user_id
  FROM events
  WHERE event_name = 'feature_used'
),
retained_d7 AS (
  SELECT DISTINCT user_id
  FROM events
  WHERE event_name = 'session_start'
    AND properties_json LIKE '%"retention_day":7%'
),
flags AS (
  SELECT
    e.variant,
    u.user_id,
    CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END AS activated,
    CASE WHEN d.user_id IS NOT NULL THEN 1 ELSE 0 END AS adopted_any_feature,
    CASE WHEN r.user_id IS NOT NULL THEN 1 ELSE 0 END AS retained_d7
  FROM experiment_assignments e
  JOIN users u ON u.user_id = e.user_id
  LEFT JOIN activated a ON a.user_id = u.user_id
  LEFT JOIN adopted d ON d.user_id = u.user_id
  LEFT JOIN retained_d7 r ON r.user_id = u.user_id
  WHERE e.experiment_name = 'onboarding_checklist_v1'
)
SELECT
  variant,
  COUNT(*) AS n,
  AVG(activated) AS activation_rate,
  AVG(adopted_any_feature) AS adoption_rate,
  AVG(retained_d7) AS d7_retention
FROM flags
GROUP BY 1
ORDER BY 1;
