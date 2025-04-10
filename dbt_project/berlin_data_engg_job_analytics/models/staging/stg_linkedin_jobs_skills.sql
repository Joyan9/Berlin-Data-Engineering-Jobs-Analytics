WITH linkedin_jobs_skills AS (
    SELECT
    *
    FROM {{ source('staging', 'linkedin_jobs__ai_key_skills') }}
)

SELECT 
    SAFE_CAST(value AS STRING) AS skill,
    -- _dlt_parent_id links to _dlt_id in linkedin_jobs table
    SAFE_CAST(_dlt_parent_id AS STRING) AS _dlt_parent_id
FROM linkedin_jobs_skills
WHERE _dlt_parent_id IS NOT NULL
