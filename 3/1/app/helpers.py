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
        f"CREATE TABLE IF NOT EXISTS {KEYSPACE}.orders (uuid UUID PRIMARY KEY, user_uuid UUID, product_uuid UUID, amount int, timestamp timestamp)")


def make_ceed_random(session: Session, ceed_number: int):
    session.set_keyspace(KEYSPACE)
    current_datetime_timestamp_seconds = int(time())
    timestamp_range = current_datetime_timestamp_seconds - ORDER_DATETIME_STARTS_TIMESTAMP_SECONDS

    for i in range(ceed_number):
        user = get_random_user()
        product = get_random_product()
        timestamp = current_datetime_timestamp_seconds - randrange(timestamp_range)
        query = f"INSERT INTO {KEYSPACE}.orders (uuid, user_uuid, product_uuid, amount, timestamp) VALUES ({str(uuid4())}, {user.get('uuid')}, {product.get('uuid')}, {product.get('amount')}, {timestamp})"
        session.execute(query)


def get_from_db(session: Session):
    rows = session.execute(f"SELECT uuid FROM {KEYSPACE}.orders")
    list = [str(row[0]) for row in rows]
    print(list)
