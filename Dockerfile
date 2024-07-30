# Dockerfile
FROM prefecthq/prefect:2.18.3-python3.10

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install -v --no-cache-dir -r requirements.txt

COPY . /opt/prefect/flows

WORKDIR /opt/prefect/flows

CMD ["python", "Kafka_to_elasticsearch.py"]
