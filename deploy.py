import os
from prefect import flow
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule
from kafka_to_elasticsearch_flow import kafka_to_elasticsearch_flow

if __name__ == "__main__":
    schedule = CronSchedule(
        cron="0 * * * *",
        timezone="Asia/Seoul"
    )

    deployment = Deployment.build_from_flow(
        flow=kafka_to_elasticsearch_flow,
        name="Kafka to Elasticsearch Deployment",
        work_queue_name="default",
        schedule=schedule,
        tags=["kafka", "elasticsearch"]
    )

    deployment.apply()
    print("Deployment created successfully.")
