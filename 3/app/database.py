from sqlalchemy import create_engine, AsyncAdaptedQueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "sqlite:///db_app.sqlite3",
    connect_args={"check_same_thread": False},
    future=True
)

SessionLocal = sessionmaker(engine, future=True)

Base = declarative_base()
