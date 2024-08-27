import json
import os
import logging
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from datetime import datetime
from prefect import flow, task

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_HOST = os.getenv('SERVER_HOST')
KAFKA_TOPIC = 'news_1'
KAFKA_GROUP_ID = 'consumer-group1'
BATCH_SIZE = 100

# Elasticsearch 매핑 설정
news_mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "standard"},
            "date": {"type": "date", "format": "yyyy-MM-dd'T'HH:mm:ss"},
            "content": {"type": "text", "analyzer": "standard"},
            "url": {"type": "keyword"}
        }
    }
}

# 날짜 형식 변환 함수
def convert_date_format(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.isoformat()
    except ValueError as e:
        logging.error(f"Date format error: {e}")
        return None

@task
def consume_kafka_data():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[f'{SERVER_HOST}:19094'],
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        request_timeout_ms=20000,  # 20초
        session_timeout_ms=10000   # 10초
    )
    data = []
    try:
        for message in consumer:
            news_item = message.value
            # 날짜 형식 변환
            if 'date' in news_item:
                news_item['date'] = convert_date_format(news_item['date'])
            data.append(news_item)
            if len(data) >= BATCH_SIZE:
                break
    finally:
        consumer.close()
    return data

@task
def send_to_elasticsearch(data):
    es = Elasticsearch([{'host': SERVER_HOST, 'port': 19200,'scheme': 'http'}])
    
    actions = []
    for record in data:
        actions.append({
            "_index": "news",
            "_source": record
        })
    
    if actions:
        success, _ = bulk(es, actions)
        logging.info(f"Inserted {success} documents into Elasticsearch")

@flow
def kafka_to_elasticsearch_flow():
    data = consume_kafka_data()
    send_to_elasticsearch(data)

if __name__ == "__main__":
    kafka_to_elasticsearch_flow()


# import json
# import os
# from hashlib import sha256
# import logging
# from kafka import KafkaConsumer, errors as kafka_errors
# from elasticsearch import Elasticsearch, exceptions as es_exceptions
# from prefect import flow, task

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SERVER_HOST = os.getenv('SERVER_HOST')
# KAFKA_TOPIC = 'news_1'
# KAFKA_GROUP_ID = 'consumer-group1'
# BATCH_SIZE = 4000

# @task
# def consume_kafka_data():
#     consumer = KafkaConsumer(
#         KAFKA_TOPIC,
#         bootstrap_servers=[f'{SERVER_HOST}:19094'],
#         group_id=KAFKA_GROUP_ID,
#         auto_offset_reset='earliest',
#         value_deserializer=lambda m: json.loads(m.decode('utf-8'))
#     )
#     data = []
#     try:
#         for message in consumer:
#             data.append(message.value)
#             if len(data) >= BATCH_SIZE:
#                 break
#     finally:
#         consumer.close()
#     return data

# @task
# def send_to_elasticsearch(data):
#     es = Elasticsearch([{'host': SERVER_HOST, 'port': 19200}])
#     for record in data:
#         record_id = sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
#         if not es.exists(index="news", id=record_id):
#             es.index(index="news", id=record_id, body=record)

# @flow
# def kafka_to_elasticsearch_flow():
#     data = consume_kafka_data()
#     send_to_elasticsearch(data)

# if __name__ == "__main__":
#     kafka_to_elasticsearch_flow()
