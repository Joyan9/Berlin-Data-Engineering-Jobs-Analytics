SELECT 
    company_name,
    company_industry,
    company_url,
    company_size,
    company_followers,
    COUNT(DISTINCT job_id) AS job_posting_count,
    MIN(date_posted) AS first_job_posted_date,
    MAX(date_posted) AS latest_job_posted_date
FROM {{ ref('stg_linkedin_jobs') }}
GROUP BY 
    company_name,
    company_industry,
    company_url,
    company_size,
    company_followers