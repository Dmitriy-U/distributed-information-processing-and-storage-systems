import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


def do():
    print('laboratory')


with DAG(
        dag_id="laboratory_2",
        schedule_interval=None,
        tags=['laboratory_2'],
        catchup=False,
):
    # TODO: Доделать
    laboratory_2_1 = PythonOperator(
        task_id='laboratory_2_1',
        python_callable=do,
    )

    laboratory_2_2 = EmptyOperator(task_id="laboratory_2_2")

    laboratory_2_1 >> laboratory_2_2
