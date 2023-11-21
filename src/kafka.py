import asyncio
from datetime import datetime

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.config.config import config
from src.database.database import async_session_maker
from src.models import Text
from src.schemas.schemas import TextData

kafka_bootstrap_servers = config.kafka.listener.split('://')[1]
kafka_topic = "baum_topic"


async def consume_item():
    consumer = AIOKafkaConsumer(
        kafka_topic,
        bootstrap_servers=kafka_bootstrap_servers,
        group_id="group1",
        loop=asyncio.get_event_loop(),
    )
    await consumer.start()
    try:
        async for message in consumer:
            data = message.value.decode('utf-8')
            item = TextData.model_validate_json(data)
            await save_result_with_delay(item)
    finally:
        await consumer.stop()


async def produce_item(item: TextData):
    producer = AIOKafkaProducer(
        loop=asyncio.get_event_loop(),
        bootstrap_servers=kafka_bootstrap_servers
    )
    await producer.start()
    try:
        await producer.send_and_wait(kafka_topic, item.model_dump_json().encode('utf-8'))
    finally:
        await producer.stop()


async def save_result(item: TextData):
    async with async_session_maker() as session:
        x_avg_count = round(sum(1 for char in item.text if char in ('х', 'Х')) / len(item.text), 3)
        result = Text(
                datetime=datetime.strptime(item.datetime, "%d.%m.%Y %H:%M:%S.%f"),
                title=item.title,
                x_avg_count_in_line=x_avg_count
            )
        session.add(result)
        await session.commit()


async def save_result_with_delay(item: TextData):
    await asyncio.sleep(3)
    await save_result(item)
