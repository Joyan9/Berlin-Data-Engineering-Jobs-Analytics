# Berlin Data Engineering Job Analytics (dbt Project)

This dbt project powers analytics on LinkedIn job postings with a focus on data engineering roles in Berlin. It transforms raw job listing data into clean, analysis-ready models for trends, company insights, and skill analysis.

---

## 📁 Project Structure

- **Sources**
  - `linkedin_jobs`: Raw job postings
  - `linkedin_jobs__ai_key_skills`: Extracted or AI-enhanced job skills

- **Staging Models (`stg_*`)**
  - Clean and standardize raw source fields

- **Intermediate Models (`int_*`)**
  - Join job posts with companies, compute daily posting metrics, and associate skills

- **Mart Models (`mart_*`)**
  - Final, analysis-ready tables for reporting:
    - `mart_job_posting_trends`
    - `mart_company_analytics`
    - `mart_skills_analysis`

---

## ✅ Tests & Freshness

- **Data Tests:**
  - Not null, unique, and referential integrity on key fields
- **Freshness Checks:**
  - Ensures `linkedin_jobs` is updated regularly via `date_posted` field

Run with:
```bash
dbt test
dbt source freshness
```

---

## 🚀 Build Commands

```bash
dbt build         # Run all models and tests
dbt run           # Run transformations only
dbt test          # Run data integrity tests
```

---

## 📊 Target Use Cases

- Monitor hiring trends over time
- Analyze top companies hiring for data roles
- Understand in-demand skills in the Berlin tech market

