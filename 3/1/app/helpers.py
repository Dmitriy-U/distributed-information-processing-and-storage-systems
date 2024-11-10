from time import time
from random import randrange

from cassandra.cluster import Session
from cassandra.concurrent import execute_concurrent_with_args

from .constants import KEYSPACE, REPLICATION_NUMBER, USER_LIST, USER_LIST_LEN, PRODUCT_LIST, PRODUCT_LIST_LEN, \
    ORDER_DATETIME_STARTS_TIMESTAMP_SECONDS


def get_random_user():
    return USER_LIST[randrange(USER_LIST_LEN)]


def get_random_product():
    return PRODUCT_LIST[randrange(PRODUCT_LIST_LEN)]


def init_db(session: Session):
    session.execute(
        f"CREATE KEYSPACE IF NOT EXISTS " + KEYSPACE + " WITH REPLICATION = {'class' : 'NetworkTopologyStrategy', 'laboratory-1-datacenter' : " + str(
            REPLICATION_NUMBER) + "}")
    session.set_keyspace(KEYSPACE)
    session.execute(f"CREATE TABLE IF NOT EXISTS orders (uuid UUID, product_uuid VARCHAR, amount FLOAT, timestamp TIMESTAMP, PRIMARY KEY ((product_uuid), timestamp, uuid)) WITH CLUSTERING ORDER BY (timestamp DESC)")
    session.execute(f"CREATE TABLE IF NOT EXISTS stats (product_uuid VARCHAR, count INT, total_amount FLOAT, PRIMARY KEY (product_uuid))")
    data = [(product['uuid'],) for product in PRODUCT_LIST]

    statement = session.prepare("INSERT INTO stats (product_uuid, count, total_amount) VALUES (?, 0, 0)")
    execute_concurrent_with_args(
        session,
        statement,
        data
    )


def make_ceed_random(session: Session, ceed_number: int):
    current_datetime_timestamp_seconds = int(time())
    timestamp_range = current_datetime_timestamp_seconds - ORDER_DATETIME_STARTS_TIMESTAMP_SECONDS

    for i in range(ceed_number):
        product = get_random_product()
        timestamp = (current_datetime_timestamp_seconds - randrange(timestamp_range)) * 1000
        session.execute(f"INSERT INTO orders (uuid, product_uuid, amount, timestamp) VALUES (uuid(), '{product.get('uuid')}', {product.get('amount')}, {timestamp})")
        result = session.execute(f"SELECT * FROM stats WHERE product_uuid = '{product.get('uuid')}'")
        _, count, total_amount = result.one()
        session.execute(f"UPDATE stats SET count = {count + 1}, total_amount = {float(total_amount) + float(product.get('amount'))} WHERE product_uuid = '{product.get('uuid')}'")


def get_amount(session: Session, date_start: int, date_end: int):
    query = f"SELECT SUM (amount) FROM orders WHERE timestamp >= {date_start} AND timestamp <= {date_end} ALLOW FILTERING"
    return session.execute(query)


def get_top_rated(session: Session):
    return session.execute("SELECT * FROM stats")
