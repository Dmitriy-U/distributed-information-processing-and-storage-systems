from time import time
from random import randrange
from uuid import uuid4

from cassandra.cluster import Session

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
    session.execute(
        f"CREATE TABLE IF NOT EXISTS {KEYSPACE}.orders (uuid UUID, user_uuid UUID, product_uuid UUID, amount DECIMAL, timestamp TIMESTAMP, PRIMARY KEY ((product_uuid), timestamp, uuid)) WITH CLUSTERING ORDER BY (timestamp DESC)")
    session.execute(
        f"CREATE TABLE IF NOT EXISTS {KEYSPACE}.stats (product_uuid UUID PRIMARY KEY, count INT, total_amount DECIMAL)")


def make_ceed_random(session: Session, ceed_number: int):
    session.set_keyspace(KEYSPACE)
    current_datetime_timestamp_seconds = int(time())
    timestamp_range = current_datetime_timestamp_seconds - ORDER_DATETIME_STARTS_TIMESTAMP_SECONDS

    for i in range(ceed_number):
        user = get_random_user()
        product = get_random_product()
        timestamp = (current_datetime_timestamp_seconds - randrange(timestamp_range)) * 1000
        query = f"INSERT INTO {KEYSPACE}.orders (uuid, user_uuid, product_uuid, amount, timestamp) VALUES ({str(uuid4())}, {user.get('uuid')}, {product.get('uuid')}, {product.get('amount')}, {timestamp})"
        session.execute(query)
        session.execute(
            f"UPDATE {KEYSPACE}.stats SET count =count + 1, total_amount = total_amount + :{product.get('amount')} WHERE product_uuid = :{product.get('uuid')}")  # TODO


def get_amount(session: Session, date_start: int, date_end: int):
    session.set_keyspace(KEYSPACE)
    query = f"SELECT SUM (amount) FROM {KEYSPACE}.orders WHERE timestamp >= {date_start} AND timestamp <= {date_end} ALLOW FILTERING"
    return session.execute(query)


def get_top_rated(session: Session):
    session.set_keyspace(KEYSPACE)
    query = f"SELECT * FROM {KEYSPACE}.stats ORDER BY count"
    return session.execute(query)
