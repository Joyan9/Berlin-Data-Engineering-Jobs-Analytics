SELECT 
    jobs.job_id,
    jobs.job_title,
    jobs.experience_level,
    jobs.job_language,
    ARRAY_AGG(DISTINCT skills.skill ORDER BY skills.skill) AS skills_array,
    COUNT(DISTINCT skills.skill) AS skill_count
FROM {{ ref('stg_linkedin_jobs') }} jobs
JOIN {{ ref('stg_linkedin_jobs_skills') }} skills
    ON jobs._dlt_id = skills._dlt_parent_id 
GROUP BY
    jobs.job_id,
    jobs.job_title,
    jobs.experience_level,
    jobs.job_language