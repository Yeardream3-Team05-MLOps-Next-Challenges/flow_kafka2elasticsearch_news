# Dockerfile
FROM prefecthq/prefect:2.18.3-python3.10

# 환경 변수 설정
ARG PREFECT_API_URL
ARG PREFECT_DEFAULT_DOCKER_BUILD_NAMESPACE
ARG SERVER_HOST
ARG KAFKA_TOPIC
ARG KAFKA_URL

ENV PREFECT_API_URL=${PREFECT_API_URL}
ENV PREFECT_DEFAULT_DOCKER_BUILD_NAMESPACE=${PREFECT_DEFAULT_DOCKER_BUILD_NAMESPACE}
ENV SERVER_HOST=${SERVER_HOST}
ENV KAFKA_TOPIC=${KAFKA_TOPIC}
ENV KAFKA_URL=${KAFKA_URL}

# 작업 디렉토리 설정 및 의존성 설치
WORKDIR /opt/prefect/flows
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 컨테이너 실행 시 커맨드
CMD ["python", "Kafka_to_elasticsearch.py"]
