import json
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from cassandra.cluster import Cluster
from fastapi.responses import Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from cassandra.auth import PlainTextAuthProvider
from fastapi.middleware.cors import CORSMiddleware

from .helpers import init_db, make_ceed_random, get_amount, get_top_rated

CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", "laboratory-1-db-1")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", 9042))

auth_provider = PlainTextAuthProvider(username='cassandra', password='password')
cluster = Cluster(CASSANDRA_HOSTS.split(' '), port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect()


@asynccontextmanager
async def lifespan(app):
    init_db(session)
    yield
    pass


app = FastAPI(
    title="Лабораторная работа 1",
    summary="Децентрализованное хранение данных",
    version="1.0.0",
    contact={"test": "test"},
    separate_input_output_schemas=False,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


class OrdersRequestBody(BaseModel):
    count: int


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.post("/api/v1/orders/ceed")
async def ceed_orders(orders_request_body: OrdersRequestBody):
    make_ceed_random(session, orders_request_body.count)
    return Response(status_code=201)


@app.get("/api/v1/orders/amount")
async def read_amount(date_start: int = 0, date_end: int = 10):
    amount = get_amount(session, date_start, date_end)
    amount = amount.one()[0]
    return Response(json.dumps({
        "amount": amount
    }), status_code=200)


@app.get("/api/v1/orders/top-rated")
async def read_amount():
    top_rated = get_top_rated(session)
    return Response(json.dumps({
        "top": top_rated
    }), status_code=200)
