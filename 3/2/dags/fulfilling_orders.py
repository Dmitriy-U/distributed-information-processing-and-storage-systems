import uuid

from airflow import DAG
from airflow.providers.apache.cassandra.hooks.cassandra import CassandraHook
from airflow.operators.python_operator import PythonOperator
from datetime import datetime


def read_unfulfilled_orders():
    hook = CassandraHook(cassandra_conn_id='cassandra_default')
    session = hook.get_conn()
    session.set_keyspace('laboratory_1')
    res = session.execute("SELECT uuid, product_uuid, timestamp FROM orders WHERE fulfilled = false ALLOW FILTERING")
    rows = res.all()
    return {"orders": [(str(row.uuid), row.product_uuid, row.timestamp) for row in rows]}


def update_orders_to_fulfilled(**context):
    unfulfilled_orders_data = context['ti'].xcom_pull(task_ids='read_unfulfilled_orders')
    hook = CassandraHook(cassandra_conn_id='cassandra_default')
    session = hook.get_conn()
    session.set_keyspace('laboratory_1')

    for order_uuid, product_uuid, timestamp in unfulfilled_orders_data["orders"]:
        session.execute(
            'UPDATE orders SET fulfilled = true WHERE product_uuid = %s AND uuid = %s AND timestamp = %s',
            (product_uuid, uuid.UUID(order_uuid), timestamp,)
        )


with DAG(
        'fulfilling_orders',
        default_args={
            'owner': 'airflow',
            'depends_on_past': False,
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
        },
        description='Laboratory 2. Fulfilling orders',
        schedule_interval=None,
        start_date=datetime(2023, 1, 1),
        catchup=False,
        tags=['laboratory_2'],
) as dag:
    read_unfulfilled_orders = PythonOperator(
        task_id='read_unfulfilled_orders',
        python_callable=read_unfulfilled_orders,
    )

    update_orders_to_fulfilled = PythonOperator(
        task_id='update_orders_to_fulfilled',
        python_callable=update_orders_to_fulfilled,
        provide_context=True,
    )

    read_unfulfilled_orders >> update_orders_to_fulfilled
