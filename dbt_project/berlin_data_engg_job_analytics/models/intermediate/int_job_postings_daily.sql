SELECT 
    DATE(date_posted) AS posting_date,
    COUNT(*) AS daily_job_count,
    COUNT(DISTINCT company_name) AS distinct_companies
FROM {{ ref('stg_linkedin_jobs') }}
GROUP BY 1
ORDER BY 1