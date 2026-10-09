WITH activated AS (
  SELECT user_id, MIN(event_ts) AS activated_at
  FROM {{ ref('stg_events') }}
  WHERE event_name = 'activation_success'
  GROUP BY 1
),
features AS (
  SELECT
    user_id,
    MAX(CASE WHEN properties_json LIKE '%"feature":"tts"%' THEN 1 ELSE 0 END) AS tts,
    MAX(CASE WHEN properties_json LIKE '%"feature":"voice_clone"%' THEN 1 ELSE 0 END) AS voice_clone,
    MAX(CASE WHEN properties_json LIKE '%"feature":"api"%' THEN 1 ELSE 0 END) AS api
  FROM {{ ref('stg_events') }}
  WHERE event_name = 'feature_used'
  GROUP BY 1
),
retained AS (
  SELECT
    user_id,
    MAX(CASE WHEN properties_json LIKE '%"retention_day":1%' THEN 1 ELSE 0 END) AS retained_d1,
    MAX(CASE WHEN properties_json LIKE '%"retention_day":7%' THEN 1 ELSE 0 END) AS retained_d7,
    MAX(CASE WHEN properties_json LIKE '%"retention_day":30%' THEN 1 ELSE 0 END) AS retained_d30
  FROM {{ ref('stg_events') }}
  WHERE event_name = 'session_start'
  GROUP BY 1
)
SELECT
  u.user_id,
  u.signup_date,
  u.experiment_variant,
  u.acquisition_channel,
  u.country,
  CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END AS activated,
  CASE WHEN COALESCE(f.tts, 0) + COALESCE(f.voice_clone, 0) + COALESCE(f.api, 0) > 0 THEN 1 ELSE 0 END AS adopted_any_feature,
  COALESCE(f.tts, 0) AS tts,
  COALESCE(f.voice_clone, 0) AS voice_clone,
  COALESCE(f.api, 0) AS api,
  COALESCE(r.retained_d1, 0) AS retained_d1,
  COALESCE(r.retained_d7, 0) AS retained_d7,
  COALESCE(r.retained_d30, 0) AS retained_d30
FROM {{ ref('stg_users') }} u
LEFT JOIN activated a ON u.user_id = a.user_id
LEFT JOIN features f ON u.user_id = f.user_id
LEFT JOIN retained r ON u.user_id = r.user_id
