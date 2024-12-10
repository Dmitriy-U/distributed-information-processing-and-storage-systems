from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import os

# Папки для данных
BASE_DIR = "/opt/airflow/data"
INPUT_FILE = os.path.join(BASE_DIR, "input.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "output.json")


def read_json_file(**kwargs):
    """Чтение данных из JSON-файла."""
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
    kwargs['ti'].xcom_push(key='raw_data', value=data)


def process_data(**kwargs):
    """Обработка данных: фильтрация по возрасту."""
    raw_data = kwargs['ti'].xcom_pull(key='raw_data', task_ids='read_json')
    processed_data = [entry for entry in raw_data if entry['age'] > 30]
    kwargs['ti'].xcom_push(key='processed_data', value=processed_data)


def save_json_file(**kwargs):
    """Сохранение обработанных данных в новый JSON-файл."""
    processed_data = kwargs['ti'].xcom_pull(key='processed_data', task_ids='process_data')
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(processed_data, f)


with DAG(
        'process_json_data',
        default_args={'start_date': datetime(2023, 1, 1)},
        schedule_interval=None,
        catchup=False,
        tags=['process_json_data'],
) as dag:
    task_read_json = PythonOperator(
        task_id='read_json',
        python_callable=read_json_file,
    )

    task_process_data = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )

    task_save_json = PythonOperator(
        task_id='save_json',
        python_callable=save_json_file,
    )

    task_read_json >> task_process_data >> task_save_json
