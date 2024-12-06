# kafka_producer.py

from kafka import KafkaProducer
import json
import time
import os

# Configurar el productor Kafka
producer = KafkaProducer(
    bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'kafka')}:9092"],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_event(user_id, event_type, message):
    event = {
        'user_id': user_id,
        'event_type': event_type,
        'message': message,
        'timestamp': time.time()
    }
    producer.send('user_events', value=event)
    print(f"Evento enviado: {event}")

if __name__ == "__main__":
    # Enviar algunos eventos de ejemplo
    for i in range(5):
        send_event(user_id=i + 1, event_type='INFO', message=f'Este es el evento {i + 1}')
        time.sleep(1)  # Espera de 1 segundo entre eventos
    
    producer.flush()
    producer.close()
