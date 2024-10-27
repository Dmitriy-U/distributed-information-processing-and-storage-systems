from typing import TypedDict


class User(TypedDict):
    uuid: str
    login: str


class Product(TypedDict):
    uuid: str
    title: str
    amount: int


USER_LIST: list[User] = [
    {'uuid': '166e1431-02d7-44aa-a6a2-4276f4d059e9', 'login': 'john'},
    {'uuid': 'da5452b7-a53e-4f68-afb2-1a83678afdc2', 'login': 'will'},
    {'uuid': '04bead4d-24d6-4311-b6f8-2cb3f4d7e7b5', 'login': 'poll'},
]

USER_LIST_LEN = len(USER_LIST)

PRODUCT_LIST: list[Product] = [
    {'uuid': '533f2909-053d-4c02-93ab-079a73d3bd66', 'title': 'foo', 'amount': 1},
    {'uuid': 'b787a96b-c1b9-4707-8d85-e54797c9fdc4', 'title': 'bar', 'amount': 10},
    {'uuid': '8881a424-d3de-4869-8529-7536481a9642', 'title': 'bas', 'amount': 100},
]

PRODUCT_LIST_LEN = len(PRODUCT_LIST)

KEYSPACE = 'laboratory_1'

REPLICATION_NUMBER = 3

ORDER_DATETIME_STARTS_TIMESTAMP_SECONDS = 1704067200
