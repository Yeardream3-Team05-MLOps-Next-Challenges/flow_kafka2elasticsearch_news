import os
from prefect import flow
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

from kafka_to_elasticsearch_flow import kafka_to_elasticsearch_flow 

if __name__ == "__main__":
    Deployment.create(
        flow=kafka_to_elasticsearch_flow,
        name="Kafka to Elasticsearch Deployment",
        work_queue_name="default",
        schedule=CronSchedule(cron="0 * * * *", timezone="Asia/Seoul"),
        image={
            "name": "team5/kafka-to-elasticsearch",
            "tag": "latest",
            "pull_policy": "ALWAYS"
        }
    )
