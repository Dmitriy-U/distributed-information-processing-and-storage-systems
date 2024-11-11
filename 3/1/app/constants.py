from typing import TypedDict


class User(TypedDict):
    uuid: str
    login: str


class Product(TypedDict):
    uuid: str
    title: str
    amount: int


PRODUCTS: dict[str, Product] = {
    '533f2909-053d-4c02-93ab-079a73d3bd66': {
        'uuid': '533f2909-053d-4c02-93ab-079a73d3bd66',
        'title': 'foo',
        'amount': 1
    },
    'b787a96b-c1b9-4707-8d85-e54797c9fdc4': {
        'uuid': 'b787a96b-c1b9-4707-8d85-e54797c9fdc4',
        'title': 'bar',
        'amount': 10
    },
    '8881a424-d3de-4869-8529-7536481a9642': {
        'uuid': '8881a424-d3de-4869-8529-7536481a9642',
        'title': 'bas',
        'amount': 100
    },
}

PRODUCT_LIST: list[Product] = list(PRODUCTS.values())

PRODUCT_LIST_LEN = len(PRODUCT_LIST)

KEYSPACE = 'laboratory_1'

REPLICATION_NUMBER = 3

ORDER_DATETIME_STARTS_TIMESTAMP_SECONDS = 1704067200
