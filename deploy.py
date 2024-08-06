import os

from prefect import flow
from prefect.deployments import DeploymentImage
from prefect.client.schemas.schedules import CronSchedule

from Kafka_to_elasticsearch import kafka_to_elasticsearch_flow

if __name__ == "__main__":
    kafka_to_elasticsearch_flow.deploy(
        name="jun-kaf2elk",
        work_pool_name="docker-agent-pool",
        work_queue_name="docker-agent",
        image=DeploymentImage(
            name="jun-kaf2elk",
            tag="0.1.6",
            dockerfile="Dockerfile",
            platform="linux/arm64",
            buildargs={
                        "PREFECT_API_URL": os.getenv("PREFECT_API_URL"),
                        "DOCKER_NAMESPACE": os.getenv("DOCKER_NAMESPACE"),
                        "SERVER_HOST": os.getenv("SERVER_HOST"),
                        "KAFKA_TOPIC": os.getenv("KAFKA_TOPIC"),
                        "KAFKA_URL": os.getenv("KAFKA_URL"),
                        },
        ),
        schedule=(CronSchedule(cron="0 8 * * *", timezone="Asia/Seoul")),
        build=True,
    )
