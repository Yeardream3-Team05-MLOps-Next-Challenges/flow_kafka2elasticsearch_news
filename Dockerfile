# Dockerfile
FROM prefecthq/prefect:2.18.3-python3.10

WORKDIR /opt/prefect/flows

# Copy only the requirements.txt initially to leverage Docker cache
COPY requirements.txt .

# Install dependencies with more verbose output
RUN python -m pip install --upgrade pip
RUN pip install -v -r requirements.txt

# Copy the rest of the application
COPY . .

CMD ["python", "Kafka_to_elasticsearch.py"]
