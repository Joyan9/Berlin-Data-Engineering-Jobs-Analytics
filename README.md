# Berlin Data Engineering Jobs Analytics

This repository contains a data engineering project focused on extracting, transforming, and analyzing job postings for Data Engineering roles in **Berlin**. The goal is to uncover insights about hiring trends, company demand, industry breakdowns, and commonly required skills using a modern data stack deployed on **Google Cloud Platform (GCP)**.

---

## 📌 Project Objectives

The project aims to answer the following questions:

1. **How many job postings related to Data Engineering were made in the last X days?**  
   - What is the **Month-over-Month (MoM)** percentage change in volume?

2. **How many different companies** have job openings for Data Engineering roles?

3. **Which industries** are hiring Data Engineers the most?

4. **What are the most in-demand skills or tech stacks** based on job descriptions?

---

## 🧩 Project Architecture

> *(Insert Architecture Diagram Here)*

The pipeline involves API data extraction, cloud data storage, transformations using dbt, and orchestration with Apache Airflow.

---

## 🔄 ETL Process Overview

### 🔍 Data Source

- **Source**: [LinkedIn Job Search API](https://rapidapi.com/)
- **Access via**: RapidAPI (Free Tier: 15 requests/month, ~500 jobs)
- **Extracted using**: [`dlt`](https://github.com/dlt-hub/dlt) — an open-source Python library built for scalable API ingestion

### ☁️ Cloud Setup (Terraform)

- **Provider**: Google Cloud Platform (GCP)
- **Provisioned via Terraform:**
  - BigQuery datasets:
    - `raw_data`: for unprocessed API data
    - `transformed_data`: for transformed insights
  - Cloud Storage bucket *(created but not used in current implementation)*

---

## 🛠️ dbt Transformation

Data transformation is handled using `dbt` with the following model structure:

- **Staging Layer**: Cleans and normalizes raw API data
- **Intermediate Layer**: Refines data further for analysis
- **Core Layer**: Final analytics models used to answer key business questions

### 🧪 dbt Tests

- Built-in generic tests:
  - Check for duplicates
  - Null value validation
  - Source freshness check for job postings

---

## 🎯 Workflow Orchestration (Airflow)

An Airflow DAG coordinates the pipeline with the following tasks:

1. `fetch_and_upload_data`: Extract and load raw data to BigQuery
2. `dbt_run`: Run dbt transformations
3. `dbt_test`: Execute data quality tests on the models

---

## 📊 Dashboard

A **Looker Studio Dashboard** visualizes insights from the transformed data.  
🔗 [View the Dashboard](https://lookerstudio.google.com/reporting/05e19323-d5db-494c-ad7d-528cbda1ff4f)

---

## 🧰 Tech Stack

| Layer              | Tool/Service                    |
|--------------------|---------------------------------|
| Extraction         | Python, `dlt`                   |
| Cloud Infrastructure | GCP (Terraform)              |
| Storage            | BigQuery                       |
| Transformation     | dbt                            |
| Orchestration      | Apache Airflow                 |
| Visualization      | Looker Studio                  |

---

## 📦 Repository Structure

```
Berlin-Data-Engineering-Jobs-Analytics/
├── .dlt/                         # DLT configuration and secrets
│   └── secrets.toml              # Your API and BigQuery credentials
├── airflow/
│   └── dags/                     # Airflow DAG definitions
│       └── bigquery_dbt_pipeline.py
├── dbt_project/                  # dbt project files
│   └── berlin_data_engg_job_analytics/
├── pipeline/                     # Python scripts for extraction and loading
│   └── run_extract_load_job.py
├── terraform/                    # Terraform configuration (optional)
│   ├── main.tf
│   ├── variables.tf
│   └── credentials/
│       └── service-account.json  # Your GCP service account key
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Service configuration
└── requirements.txt              # Python dependencies
```

---
## Setup Guide

This guide will help you set up and run the Berlin Data Engineering Jobs Analytics project using Docker. The project consists of an ELT pipeline orchestrated by Airflow that extracts job data, loads it to BigQuery, and transforms it with dbt.

### Prerequisites

Before you begin, make sure you have:

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine
- A Google Cloud Platform (GCP) account with:
  - A project with BigQuery enabled
  - A service account with BigQuery Admin permissions
  - A service account key file (JSON)
- An API key for [LinkedIn Jobs API on RapidAPI](https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/linkedin-job-search-api) (for data extraction)


#### 1. Clone the Repository

```bash
git clone https://github.com/Joyan9/Berlin-Data-Engineering-Jobs-Analytics.git
cd Berlin-Data-Engineering-Jobs-Analytics
```

#### 2. Configure Your Credentials

##### `dlt` Secrets

Create a file `.dlt/secrets.toml` with your credentials:

```toml
[sources.linkedin_jobs_api]
rapid_api_key = "YOUR_RAPID_API_KEY"

[destination.bigquery]
dataset_name = "raw_data"
location = "YOUR_PREFERRED_LOCATION" # e.g., europe-west10

[destination.bigquery.credentials]
project_id = "YOUR_GCP_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "YOUR_PRIVATE_KEY" # Copy full key including "-----BEGIN PRIVATE KEY-----" and "-----END PRIVATE KEY-----"
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CLIENT_X509_CERT_URL"
universe_domain = "googleapis.com"
```

##### Terraform Credentials (Optional)

If you plan to use Terraform to manage your GCP infrastructure:

1. Create the directory `terraform/credentials/`
2. Save your service account key as `terraform/credentials/service-account.json`

#### 3. Update DAG Configuration

In `airflow/dags/bigquery_dbt_pipeline.py`, update the email configuration:

```python
default_args = {
    'email': ['your-email@example.com'],  # Change to your email
    # Other settings...
}
```

#### 4. Build and Start the Containers

From the project root directory, run:

```bash
docker-compose build
docker-compose up -d
```

This will:
- Build the Docker image with all required dependencies
- Start the Airflow webserver, scheduler, and PostgreSQL database
- Initialize the dbt documentation server
- Start a Terraform service (if needed)

#### 5. Access the Services

- **Airflow UI**: http://localhost:8080 (default username/password: airflow/airflow)
- **dbt Documentation**: http://localhost:8888

#### 6. Initialize Infrastructure (Optional)

If you want to use Terraform to set up your GCP resources:

```bash
docker-compose exec terraform bash
cd $TERRAFORM_PATH
terraform init
terraform apply
```

---

## Customizing the Project

### Modifying the Schedule

To change when the pipeline runs, edit the `schedule_interval` parameter in `airflow/dags/bigquery_dbt_pipeline.py`:

```python
dag = DAG(
    'bigquery_dbt_pipeline',
    default_args=default_args,
    description='Weekly pipeline to load data into BigQuery and run dbt models',
    schedule_interval='30 9 * * 1',  # Every Monday at 9:30 AM - modify as needed
    catchup=False,
    tags=['bigquery', 'dbt', 'jobs_data'],
)
```

### Changing Resource Allocation

If you need to adjust container resource limits, modify the `docker-compose.yml` file to add resource constraints:

```yaml
services:
  airflow-webserver:
    # Existing configuration...
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

## Troubleshooting

### Container Startup Issues

Check container logs:

```bash
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler
```

### DAG Running Issues

1. Check Airflow logs through the UI or:
```bash
docker-compose exec airflow-scheduler bash -c "cat /opt/airflow/logs/dag_id/task_id/execution_date/number.log"
```

2. Restart services if needed:
```bash
docker-compose restart airflow-webserver airflow-scheduler
```

### Data Pipeline Issues

Run the pipeline manually to debug:

```bash
docker-compose exec airflow-scheduler bash
cd $PROJECT_ROOT/pipeline
python run_extract_load_job.py
```

---

## Stopping the Project

To stop the project:

```bash
docker-compose down
```

To remove all data (including volumes):

```bash
docker-compose down -v
```

---

## 👤 Author

**Joyan Bhathena**  
[LinkedIn](https://www.linkedin.com/in/joyanbhathena)
