import os
from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from datetime import timedelta
from Kafka_to_elasticsearch import kafka_to_elasticsearch_flow

DeploymentSpec(
    flow=kafka_to_elasticsearch_flow,
    name="Kafka to Elasticsearch Deployment",
    schedule=CronSchedule(cron="0 * * * *", timezone="Asia/Seoul"),
    work_queue_name="default",
    tags=["kafka", "elasticsearch"],
    image={
        "name": "team5/kafka-to-elasticsearch",
        "tag": "0.1",
        "dockerfile": "Dockerfile"
    }
)
