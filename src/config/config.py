import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class PostgresDB:
    user: str
    passw: str
    name: str
    port: str
    host: str
    url: str


@dataclass
class Kafka:
    listener: str


@dataclass
class Config:
    db: PostgresDB
    kafka: Kafka


def load_config(path: str | None = None) -> Config:
    load_dotenv(path)
    db_user = os.getenv("POSTGRES_USER")
    db_pass = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_port = os.getenv("DB_PORT")
    db_host = os.getenv("DB_HOST")
    listener = os.getenv("KAFKA_LISTENERS")

    return Config(db=PostgresDB(
        user=db_user,
        passw=db_pass,
        name=db_name,
        port=db_port,
        host=db_host,
        url=f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    ), kafka=Kafka(
       listener=listener
    )
    )


config = load_config()
