# kafka_consumer.py

from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json
import os

# Configurar el consumidor Kafka
consumer = KafkaConsumer(
    'user_events',
    bootstrap_servers=[os.getenv('KAFKA_HOST', 'kafka')+":9092"],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Conectar a Elasticsearch
es = Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST', 'elasticsearch'), 'port': 9200}])

def index_event(event):
    # Indexar el evento en Elasticsearch
    res = es.index(index='user_events', body=event)
    print(f"Evento indexado: {res['result']}")

if __name__ == "__main__":
    print("Iniciando el consumidor Kafka para Elasticsearch...")
    for message in consumer:
        event = message.value
        print(f"Evento recibido: {event}")
        index_event(event)
