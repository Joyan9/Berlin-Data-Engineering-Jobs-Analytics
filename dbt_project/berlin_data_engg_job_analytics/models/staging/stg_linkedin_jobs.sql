WITH linkedin_jobs AS (
    SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY date_posted DESC) AS row_num
    FROM {{ source('staging', 'linkedin_jobs') }}
)

SELECT 
    SAFE_CAST(id AS INTEGER) AS job_id,
    SAFE_CAST(title AS STRING) AS job_title,
    SAFE_CAST(date_posted AS TIMESTAMP) AS date_posted,
    SAFE_CAST(organization AS STRING) AS company_name,
    SAFE_CAST(linkedin_org_employees AS INTEGER) AS company_size,
    SAFE_CAST(linkedin_org_industry AS STRING) AS company_industry,
    SAFE_CAST(linkedin_org_url AS STRING) AS company_url,
    SAFE_CAST(linkedin_org_followers AS INTEGER) AS company_followers,
    SAFE_CAST(employment_type AS STRING) AS employment_type,
    SAFE_CAST(seniority AS STRING) AS seniority_level,
    SAFE_CAST(directapply AS BOOLEAN) AS direct_apply,
    SAFE_CAST(url AS STRING) AS job_url,
    SAFE_CAST(location_city AS STRING) AS job_location,
    SAFE_CAST(ai_experience_level AS STRING) AS experience_level,
    SAFE_CAST(ai_job_language AS STRING) AS job_language,
    SAFE_CAST(ai_work_arrangement AS STRING) AS work_arrangement,
    SAFE_CAST(_dlt_id AS STRING) AS _dlt_id
FROM linkedin_jobs
WHERE row_num = 1
