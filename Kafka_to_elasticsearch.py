# import json
# import os
# import logging
# from kafka import KafkaConsumer
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
# from datetime import datetime
# from prefect import flow, task

# # 로깅 설정
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SERVER_HOST = os.getenv('SERVER_HOST')
# KAFKA_TOPIC = 'news_1'
# KAFKA_GROUP_ID = 'consumer-group1'
# BATCH_SIZE = 100

# # Elasticsearch 매핑 설정
# news_mapping = {
#     "mappings": {
#         "properties": {
#             "title": {"type": "text", "analyzer": "standard"},
#             "date": {"type": "date", "format": "yyyy-MM-dd'T'HH:mm:ss"},
#             "content": {"type": "text", "analyzer": "standard"},
#             "url": {"type": "keyword"}
#         }
#     }
# }

# # 날짜 형식 변환 함수
# def convert_date_format(date_str):
#     try:
#         dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
#         return dt.isoformat()
#     except ValueError as e:
#         logging.error(f"Date format error: {e}")
#         return None

# @task
# def consume_kafka_data():
#     consumer = KafkaConsumer(
#         KAFKA_TOPIC,
#         bootstrap_servers=[f'{SERVER_HOST}:19094'],
#         group_id=KAFKA_GROUP_ID,
#         auto_offset_reset='earliest',
#         value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#         request_timeout_ms=20000,  # 20초
#         session_timeout_ms=10000
#         #max_poll_interval_ms=300000
#     )
#     data = []
#     try:
#         for message in consumer:
#             news_item = message.value
#             # 날짜 형식 변환
#             if 'date' in news_item:
#                 news_item['date'] = convert_date_format(news_item['date'])
#             data.append(news_item)
#             if len(data) >= BATCH_SIZE:
#                 break
#     finally:
#         consumer.close()
#     return data

# @task
# def send_to_elasticsearch(data):
#     es = Elasticsearch([{'host': SERVER_HOST, 'port': 19200,'scheme': 'http'}])

#     if not es.indices.exists(index="news"):
#         es.indices.create(index="news", body=news_mapping)
    
#     actions = []
#     for record in data:
#         actions.append({
#             "_op_type": "index",
#             "_index": "news",
#             "_id": record['url'],
#             "_source": record
#         })
    
#     if actions:
#         try:
#             success, failed = bulk(es, actions)
#             logging.info(f"Inserted {success} documents into Elasticsearch, Failed {failed} documents")
#         except Exception as e:
#             logging.error(f"Error during bulk operation: {e}")
#     es.close()

# @flow
# def kafka_to_elasticsearch_flow():
#     data = consume_kafka_data()
#     if data:
#         send_to_elasticsearch(data)
#     else:
#         logging.info("No new data to process")

# if __name__ == "__main__":
#     kafka_to_elasticsearch_flow()
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from prefect import flow, task
from prefect.schedules import CronSchedule
import json
import os
import logging
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 환경 변수 설정
SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')  # 기본값으로 'localhost' 설정
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'news_1')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'consumer-group1')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
RETRY_COUNT = int(os.getenv('RETRY_COUNT', 3))

# Elasticsearch 설정
es = Elasticsearch([{'host': SERVER_HOST, 'port': 19200, 'scheme': 'http'}])

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

@task
def consume_kafka_data():
    """
    Kafka Consumer에서 데이터를 가져오는 함수.
    """
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[f'{SERVER_HOST}:19094'],
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='earliest',
        enable_auto_commit=False,  # 수동으로 오프셋 커밋
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        max_poll_records=BATCH_SIZE  # 한 번에 가져올 최대 레코드 수
    )

    messages = consumer.poll(timeout_ms=1000, max_records=BATCH_SIZE)
    data = [message.value for record_list in messages.values() for message in record_list]
    consumer.close()
    return data

@task
def send_to_elasticsearch(data):
    """
    데이터를 Elasticsearch로 전송하고 성공 시 오프셋을 커밋하는 함수.
    """
    if not data:
        return

    if not es.indices.exists(index="news"):
        es.indices.create(index="news", body=news_mapping)

    actions = [
        {
            "_op_type": "index",
            "_index": "news",
            "_id": record['url'],
            "_source": record
        }
        for record in data
    ]

    for attempt in range(RETRY_COUNT):
        try:
            success, failed = bulk(es, actions)
            logging.info(f"Inserted {success} documents into Elasticsearch, Failed {failed} documents")
            break
        except Exception as e:
            logging.error(f"Error during bulk operation: {e}, Attempt {attempt + 1} of {RETRY_COUNT}")
            time.sleep(2 ** attempt)

# Cron 스케줄 설정: 1시간마다 작업 실행
schedule = CronSchedule(cron="0 */1 * * *", timezone="Asia/Seoul")

@flow(name="Kafka to Elasticsearch Flow")
def kafka_to_elasticsearch_flow():
    data = consume_kafka_data()
    if data:
        send_to_elasticsearch(data)

if __name__ == "__main__":
    kafka_to_elasticsearch_flow()
