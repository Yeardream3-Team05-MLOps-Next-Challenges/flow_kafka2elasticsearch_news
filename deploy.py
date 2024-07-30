import os

from prefect import flow
from prefect.deployments import DeploymentImage
from prefect.client.schemas.schedules import CronSchedule

from Kafka_to_elasticsearch import kafka_to_elasticsearch_flow

if __name__ == "__main__":
    kafka_to_elasticsearch_flow.deploy(
        name="jun_kaf2elk_deploy",
        work_pool_name="docker-agent-pool",
        work_queue_name="docker-agent",
        image=DeploymentImage(
            name="jun-kaf2elk",
            tag="0.2",
            dockerfile="Dockerfile",
            platform="linux/arm64",
        ),
        schedule=(CronSchedule(cron="0 1 * * *", timezone="Asia/Seoul")),
        build=True,
    )
