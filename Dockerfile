# Dockerfile
FROM prefecthq/prefect:2.18.3-python3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "Kafka_to_elasticsearch.py"]
