from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import requests
import json


def get_account():
    url = "https://data.cityofnewyork.us/resource/rc75-m7u3.json"
    response = requests.get(url)

    df = pd.DataFrame(json.loads(response.content))
    quantity = len(df.index)

    return quantity


def is_valid(ti):
    quantity = ti.xcom_pull(task_ids = 'get_account')

    if (quantity == 1000):
        return 'valid'
    return 'not_valid'


with DAG('tutorial_dag',
         start_date = datetime(2024, 1, 23),
         schedule_interval = '30 * * * *',
         catchup = False) as dag:

    get_account = PythonOperator(
        task_id = 'get_account',
        python_callable = get_account
    )
    is_valid = BranchPythonOperator(
        task_id = 'is_valid',
        python_callable = is_valid
    )

    valid = BashOperator(
        task_id = 'valid',
        bash_command = "echo 'Quantity OK'"
    )

    not_valid = BashOperator(
        task_id = 'not_valid',
        bash_command = "echo 'Quantity NOT OK'"
    )

    get_account >> is_valid >> [valid, not_valid]
