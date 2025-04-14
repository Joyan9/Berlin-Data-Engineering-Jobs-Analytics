from datetime import timedelta
import os
import logging
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# Load environment variables or fallback defaults
PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/home/joyan/Berlin-Data-Engineering-Jobs-Analytics")
DBT_PROJECT_PATH = os.getenv("DBT_PROJECT_PATH", os.path.join(PROJECT_ROOT, "dbt_project/berlin_data_engg_job_analytics"))
EMAIL = os.getenv("AIRFLOW_EMAIL", "admin@example.com")

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': [EMAIL],   
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(hours=1),
    'start_date': days_ago(1),
}

# Create the DAG
dag = DAG(
    'bigquery_dbt_pipeline',
    default_args=default_args,
    description='Weekly pipeline to load data into BigQuery and run dbt models',
    schedule_interval='30 7 * * 1',
    catchup=False,
    tags=['bigquery', 'dbt', 'jobs_data'],
    doc_md="""
    # BigQuery and DBT Pipeline

    This DAG orchestrates the weekly ETL process for Berlin data engineering jobs:
    1. Extracts jobs data from API for the last 7 days
    2. Loads data into BigQuery
    3. Transforms data using dbt models
    4. Validates data with dbt tests

    Runs every Monday at 7:30 AM UTC.
    """
)

# Task: Fetch and upload data
def fetch_and_upload_data(**context):
    import subprocess
    import os
    
    script_path = os.path.join(PROJECT_ROOT, "pipeline", "run_extract_load_job.py")
    logging.info(f"Running script: {script_path}")
    
    try:
        result = subprocess.run(
            f"python3 {script_path}",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            env=os.environ.copy()  # Ensure the subprocess inherits the current environment
        )
        logging.info("Data fetch and upload completed.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e.stderr}")
        raise Exception(f"Script failed: {e.stderr}")

fetch_upload_task = PythonOperator(
    task_id='fetch_and_upload_data',
    python_callable=fetch_and_upload_data,
    provide_context=True,
    dag=dag,
)

# Bash Operators for dbt
run_dbt_command = f'cd {DBT_PROJECT_PATH} && dbt run'
test_dbt_command = f'cd {DBT_PROJECT_PATH} && dbt test'

run_dbt = BashOperator(
    task_id='dbt_run',
    bash_command=run_dbt_command,
    dag=dag,
)

test_dbt = BashOperator(
    task_id='dbt_test',
    bash_command=test_dbt_command,
    dag=dag,
)


fetch_upload_task >> run_dbt >> test_dbt
