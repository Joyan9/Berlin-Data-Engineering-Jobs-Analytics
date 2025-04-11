from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# Define paths to dbt project and project root
PROJECT_ROOT = "/home/joyan/Berlin-Data-Engineering-Jobs-Analytics"
DBT_PROJECT_PATH = "/home/joyan/Berlin-Data-Engineering-Jobs-Analytics/dbt_project/berlin_data_engg_job_analytics"

# DAG default arguments
default_args = {
    'owner': 'joyan',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

# Define DAG
dag = DAG(
    'dbt_run',
    default_args=default_args,
    description='Run dbt models for Berlin data engineering jobs analytics',
    schedule_interval='45 9 * * 1',  # Every Monday at 9:45 AM
    catchup=False,
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

# Set task dependencies
run_dbt >> test_dbt