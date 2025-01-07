from airflow import DAG
from airflow.providers.apache.cassandra.hooks.cassandra import CassandraHook
from airflow.operators.python_operator import PythonOperator
from datetime import datetime


def read_from_cassandra():
    hook = CassandraHook(cassandra_conn_id='cassandra_default')
    session = hook.get_conn()  # FIXME
    session.set_keyspace('laboratory_1')
    rows = session.execute("SELECT uuid FROM orders")
    return [{"id": row.id, "value": row.value} for row in rows]


def transform_data(**context):
    data = context['ti'].xcom_pull(task_ids='read_data')
    transformed = [{"id": str(row['id']), "updated_value": row['value'].upper()} for row in data]
    return transformed


def write_to_cassandra(**context):
    transformed_data = context['ti'].xcom_pull(task_ids='transform_data')
    # hook = CassandraHook(cassandra_conn_id='cassandra_default')
    # session = hook.get_conn()

    # for row in transformed_data:
    #     session.execute(
    #         """
    #         INSERT INTO target_table (id, updated_value) VALUES (%s, %s)
    #         """,
    #         (uuid.UUID(row['id']), row['updated_value'])
    #     )
    pass


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

with DAG(
        'fulfilling_orders',
        default_args=default_args,
        description='Laboratory 2. Fulfilling orders',
        schedule_interval=None,
        start_date=datetime(2023, 1, 1),
        catchup=False,
        tags=['example'],
) as dag:
    read_data = PythonOperator(
        task_id='read_data',
        python_callable=read_from_cassandra,
    )

    transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )

    write_data = PythonOperator(
        task_id='write_data',
        python_callable=write_to_cassandra,
        provide_context=True,
    )

    read_data >> transform_data >> write_data
