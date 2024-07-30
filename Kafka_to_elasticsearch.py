import json
import os
from hashlib import sha256
import logging
from kafka import KafkaConsumer, errors as kafka_errors
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from prefect import flow, task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@task
def consume_kafka_data(server_host, kafka_topic, group_id):
    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=[f'{server_host}:19094'],
        group_id=group_id,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    data = []
    try:
        for message in consumer:
            data.append(message.value)
            if len(data) >= 100:  # BATCH_SIZE
                break
    finally:
        consumer.close()
    return data

@task
def send_to_elasticsearch(data, server_host):
    es = Elasticsearch([{'host': server_host, 'port': 19200}])
    for record in data:
        record_id = sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        if not es.exists(index="news", id=record_id):
            es.index(index="news", id=record_id, body=record)

@flow
def kafka_to_elasticsearch_flow(server_host, kafka_topic, group_id):
    data = consume_kafka_data(server_host, kafka_topic, group_id)
    send_to_elasticsearch(data, server_host)

if __name__ == "__main__":
    kafka_to_elasticsearch_flow(os.getenv('SERVER_HOST'), 'news_1', 'consumer-group1')
