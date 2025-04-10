SELECT
    company_industry,
    COUNT(DISTINCT company_name) AS company_count,
    SUM(job_posting_count) AS total_job_postings,
    ARRAY_AGG(DISTINCT company_name) AS companies
FROM {{ ref('int_companies') }}
GROUP BY company_industry
ORDER BY company_count DESC