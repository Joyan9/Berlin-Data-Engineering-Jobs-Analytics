SELECT
    skill,
    COUNT(job_id) as jobs
FROM {{ ref('int_job_skills') }}
INNER JOIN UNNEST(skills_array) as skill
GROUP BY skill
ORDER BY jobs DESC