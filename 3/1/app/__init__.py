from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.responses import Response
from cassandra.cluster import Cluster
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .helpers import init_db, make_ceed_random

cluster = Cluster(['127.0.0.1'])
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
async def read_amount(dateFrom: int = 0, dateTo: int = 10):
    return Response(status_code=200)


@app.get("/api/v1/orders/top-rated")
async def read_amount():
    return Response(status_code=200)
