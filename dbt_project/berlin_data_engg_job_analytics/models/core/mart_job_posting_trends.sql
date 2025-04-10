WITH daily_counts AS (
    SELECT
        posting_date,
        daily_job_count,
        distinct_companies,
        -- Get month start for monthly aggregations
        DATE_TRUNC(posting_date, MONTH) AS month_start
    FROM {{ ref('int_job_postings_daily') }}
),

monthly_counts AS (
    SELECT
        month_start,
        SUM(daily_job_count) AS monthly_job_count,
        COUNT(DISTINCT posting_date) AS days_with_data
    FROM daily_counts
    GROUP BY 1
),

monthly_change AS (
    SELECT
        month_start,
        monthly_job_count,
        days_with_data,
        LAG(monthly_job_count) OVER (ORDER BY month_start) AS prev_month_count,
        CASE 
            WHEN LAG(monthly_job_count) OVER (ORDER BY month_start) IS NOT NULL 
            THEN (monthly_job_count - LAG(monthly_job_count) OVER (ORDER BY month_start)) / LAG(monthly_job_count) OVER (ORDER BY month_start) * 100
            ELSE NULL
        END AS mom_percent_change
    FROM monthly_counts
)

SELECT * FROM monthly_change
ORDER BY month_start DESC