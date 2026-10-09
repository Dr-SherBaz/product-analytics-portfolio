SELECT
  event_id,
  user_id,
  event_name,
  CAST(event_ts AS TIMESTAMP) AS event_ts,
  properties_json
FROM {{ source('raw', 'events') }}
