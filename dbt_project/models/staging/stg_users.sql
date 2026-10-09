SELECT
  user_id,
  CAST(signup_date AS DATE) AS signup_date,
  experiment_variant,
  country,
  acquisition_channel
FROM {{ source('raw', 'users') }}
