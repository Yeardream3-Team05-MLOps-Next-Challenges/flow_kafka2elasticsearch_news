# import os
# from prefect import flow
# from prefect.deployments import DeploymentImage
# from prefect.client.schemas.schedules import CronSchedule
# from prefect.tasks import task_input_hash
# from Kafka_to_elasticsearch import kafka_to_elasticsearch_flow

# @flow(
#     name="kafka_to_elasticsearch_main_flow",
#     version="0.1.6",
#     description="Main flow to control Kafka to Elasticsearch data transfer",
#     retries=3,
#     retry_delay_seconds=300,
# )
# def main_flow():
#     kafka_to_elasticsearch_flow()

# if __name__ == "__main__":
#     main_flow.deploy(
#         name="jun-kaf2elk",
#         work_pool_name="docker-agent-pool",
#         work_queue_name="docker-agent",
#         image=DeploymentImage(
#             name="jun-kaf2elk",
#             tag="0.1.6",
#             dockerfile="Dockerfile",
#             platform="linux/arm64",
#             buildargs={
#                 "PREFECT_API_URL": os.getenv("PREFECT_API_URL"),
#                 "PREFECT_DEFAULT_DOCKER_BUILD_NAMESPACE": os.getenv("PREFECT_DEFAULT_DOCKER_BUILD_NAMESPACE"),
#                 "SERVER_HOST": os.getenv("SERVER_HOST"),
#                 "KAFKA_TOPIC": os.getenv("KAFKA_TOPIC"),
#                 "KAFKA_URL": os.getenv("KAFKA_URL"),
#             },
#         ),
#         schedule=(CronSchedule(cron="0,10,20,30,40,50 * * * *", timezone="Asia/Seoul")),
#         build=True,
#         job_variables={
#             "PREFECT__FLOW_SETTINGS__concurrency_limit": 1,
#             "PREFECT__FLOW_SETTINGS__concurrency_queue": "jun-kaf2elk-queue",
#         },
#     )




#========== 
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
                        "PREFECT_DEFAULT_DOCKER_BUILD_NAMESPACE": os.getenv("PREFECT_DEFAULT_DOCKER_BUILD_NAMESPACE"),
                        "SERVER_HOST": os.getenv("SERVER_HOST"),
                        "KAFKA_TOPIC": os.getenv("KAFKA_TOPIC"),
                        "KAFKA_URL": os.getenv("KAFKA_URL"),
                        },
        ),
        schedule=(CronSchedule(cron="0 13 * * *", timezone="Asia/Seoul")),
        build=True,
        job_variables={
            "PREFECT__FLOW_SETTINGS__concurrency_limit": 1,
            "PREFECT__FLOW_SETTINGS__concurrency_queue": "jun-kaf2elk-queue",
        }
    )







# =============
# import os
# from prefect import flow
# from prefect.deployments import Deployment
# from prefect.client.schemas.schedules import CronSchedule
# from prefect.client import get_client
# from Kafka_to_elasticsearch import kafka_to_elasticsearch_flow

# async def update_or_create_deployment():
#     async with get_client() as client:
#         deployment_name = "jun-kaf2elk"
        
#         deployment_args = dict(
#             name=deployment_name,
#             flow=kafka_to_elasticsearch_flow,
#             work_pool_name="docker-agent-pool",
#             work_queue_name="docker-agent",
#             schedule=(CronSchedule(cron="0 * * * *", timezone="Asia/Seoul")),  # 매시간 실행
#         )
        
#         try:
#             # 기존 배포 확인
#             existing_deployment = await client.read_deployment(f"{kafka_to_elasticsearch_flow.name}/{deployment_name}")
#             # 기존 배포 업데이트
#             deployment = await client.update_deployment(existing_deployment.id, **deployment_args)
#             print(f"Updated existing deployment: {deployment.name}")
#         except:
#             # 새 배포 생성
#             deployment = await Deployment.build_from_flow(**deployment_args)
#             await deployment.apply()
#             print(f"Created new deployment: {deployment.name}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(update_or_create_deployment())
