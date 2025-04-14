from datetime import timedelta
import os
import logging
import subprocess
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago


PROJECT_ROOT = os.getenv("PROJECT_ROOT")
DBT_PROJECT_PATH = os.getenv("DBT_PROJECT_PATH")
os.environ['DLT_PROJECT_DIR'] = os.getenv('DLT_PROJECT_PATH', '/home/joyan/Berlin-Data-Engineering-Jobs-Analytics/.dlt')

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1)
}

# Create the DAG
dag = DAG(
    'env_vars',
    default_args=default_args,
    description='Weekly pipeline to load data into BigQuery and run dbt models',
    schedule_interval='30 7 * * 1',
    catchup=False
    )

def print_env_vars(**kwargs):
    import os
    for key, value in os.environ.items():
        print(f"{key}={value}")

print_env_task = PythonOperator(
    task_id="print_env_vars",
    python_callable=print_env_vars,
    provide_context=True,
    dag=dag,
)

# Task: Check for required environment variables
def check_env_variables(**kwargs):
    # List the required environment variables here.
    required_vars = ["PROJECT_ROOT", "DBT_PROJECT_PATH", "DLT_PROJECT_PATH", 
                    "GOOGLE_APPLICATION_CREDENTIALS", "LINKEDIN_JOBS_API_KEY", 
                    "BIGQUERY_RAW_DATASET", "BIGQUERY_LOCATION"]
    
    # Check which of these are missing.
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        error_message = f"Missing required environment variables: {', '.join(missing_vars)}"
        logging.error(error_message)
        # Fail the task so that all downstream tasks will not execute.
        raise Exception(error_message)
    
    logging.info("All required environment variables are set.")
    return "Success"

check_env_task = PythonOperator(
    task_id="check_env_variables",
    python_callable=check_env_variables,
    provide_context=True,
    dag=dag,
)


print_env_task >> check_env_task
