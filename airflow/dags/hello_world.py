import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

# Get the project root directory (parent of airflow directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.environ.get('AIRFLOW_HOME'), '..'))

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 4, 11, 11, 50)
}

dag = DAG(
    'hello_world',
    default_args=default_args,
    description='A simple hello world DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example']
)

def hello_world():
    print("Hello, World!")
    return "Hello world returned!"

hello_task = PythonOperator(
    task_id = 'hello_world',
    python_callable = hello_world,
    dag=dag
)

def print_goodbye():
    print("Goodbye World!")
    return "Goodbye World returned!"

goodbye_task = PythonOperator(
    task_id='goodbye_task',
    python_callable=print_goodbye,
    dag=dag,
)

# Set task dependencies
hello_task >> goodbye_task