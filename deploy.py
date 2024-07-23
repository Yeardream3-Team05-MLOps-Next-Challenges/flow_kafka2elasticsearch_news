import os
from prefect import flow
from prefect.deployments import DeploymentImage
from prefect.client.schemas.schedules import CronSchedule

from kafka_to_elasticsearch_flow import kafka_to_elasticsearch_flow 



if __name__ == "__main__":
    kafka_to_elasticsearch_flow.deploy(
        name="Kafka to Elasticsearch Deployment",
        work_pool_name="docker-agent-pool",
        work_queue_name="docker-agent",
        image=DeploymentImage(
            name="jun-kafka2elk",
            tag="0.1",
            dockerfile="Dockerfile",
            platform="linux/arm64",
            buildargs={
                       "SERVER_HOST": os.getenv("SERVER_HOST"),
                       "KAFKA_TOPIC": os.getenv("KAFKA_TOPIC"),
                       },
        ),
        schedule=(CronSchedule(cron="0 * * * *", timezone="Asia/Seoul")),
        build=True,
    )
