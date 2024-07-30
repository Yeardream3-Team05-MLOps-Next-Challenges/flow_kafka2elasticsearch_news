# Dockerfile
FROM prefecthq/prefect:2.18.3-python3.10

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    && python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY . /opt/prefect/flows

WORKDIR /opt/prefect/flows

CMD ["python", "Kafka_to_elasticsearch.py"]
