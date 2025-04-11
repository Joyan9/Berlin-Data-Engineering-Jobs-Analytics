from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# Define paths to dbt project and project root
PROJECT_ROOT = "/home/joyan/Berlin-Data-Engineering-Jobs-Analytics"
DBT_PROJECT_PATH = "/home/joyan/Berlin-Data-Engineering-Jobs-Analytics/dbt_project/berlin_data_engg_job_analytics"

# Default arguments for the DAG
default_args = {
    'owner': 'joyan',
    'depends_on_past': False,
    'email': ['joyan9@yopmail.com'], 
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,  # Exponential backoff for retries
    'max_retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(hours=1),  # Prevent tasks from running too long
    'start_date': days_ago(1),
}

# Create the DAG
dag = DAG(
    'bigquery_dbt_pipeline',
    default_args=default_args,
    description='Weekly pipeline to load data into BigQuery and run dbt models',
    schedule_interval='30 9 * * 1',  # Every Monday at 9:30 AM
    catchup=False,
    tags=['bigquery', 'dbt', 'jobs_data'],
    doc_md="""
    # BigQuery and DBT Pipeline
    
    This DAG orchestrates the weekly ETL process for Berlin data engineering jobs:
    1. Extracts jobs data from API for the last 7 days
    2. Loads data into BigQuery
    3. Transforms data using dbt models
    4. Validates data with dbt tests
    
    Runs every Monday at 9:30 AM CET.
    """
)

# Function to fetch data from API and upload to BigQuery
def fetch_and_upload_data(**context):
    """
    Fetch the last 7 days of data from the API and upload to BigQuery
    """
    import subprocess
    import logging
    
    script_path = os.path.join(PROJECT_ROOT, "pipeline/run_extract_load_job.py")
    
    logging.info(f"Starting data fetch and upload process using script: {script_path}")
    
    try:
        # Activate virtual environment and run the script
        cmd = f"python3 {script_path}"
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"Data upload completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during data upload: {e.stderr}")
        raise Exception(f"Data upload failed with error: {e.stderr}")

# Define the tasks
fetch_upload_task = PythonOperator(
    task_id='fetch_and_upload_data',
    python_callable=fetch_and_upload_data,
    provide_context=True,  # Provides Airflow context variables to the function
    dag=dag,
)

# Task to run dbt models
run_dbt = BashOperator(
    task_id='dbt_run',
    bash_command=f'cd {DBT_PROJECT_PATH} && source {PROJECT_ROOT}/venv/bin/activate && dbt run',
    dag=dag,
)

# Task to run dbt tests
test_dbt = BashOperator(
    task_id='dbt_test',
    bash_command=f'cd {DBT_PROJECT_PATH} && source {PROJECT_ROOT}/venv/bin/activate && dbt test',
    dag=dag,
)

# Define dependencies
fetch_upload_task >> run_dbt >> test_dbt