import json
import os
from hashlib import sha256
import logging
from kafka import KafkaConsumer, errors as kafka_errors
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from prefect import task, flow
from prefect.orion.schemas.schedules import IntervalSchedule
from datetime import timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_HOST = os.getenv('SERVER_HOST')
KAFKA_TOPIC = 'news_1'
KAFKA_GROUP_ID = 'consumer-group1'
BATCH_SIZE = 100  # Number of messages to process per batch

@task
def consume_kafka_data():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[f'{SERVER_HOST}:19094'],
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    data = []
    try:
        for message in consumer:
            data.append(message.value)
            if len(data) >= BATCH_SIZE:
                break
    except kafka_errors.KafkaError as e:
        logging.error(f"Error consuming Kafka data: {e}")
    finally:
        consumer.close()
    return data

@task
def send_to_elasticsearch(data):
    es = Elasticsearch([{'host': SERVER_HOST, 'port': 19200}])
    for record in data:
        record_id = sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        if not es.exists(index="news", id=record_id):
            es.index(index="news", id=record_id, body=record)

@flow(schedule=IntervalSchedule(interval=timedelta(hours=1)))
def kafka_to_elasticsearch_flow():
    data = consume_kafka_data()
    send_to_elasticsearch(data)

if __name__ == "__main__":
    kafka_to_elasticsearch_flow()
