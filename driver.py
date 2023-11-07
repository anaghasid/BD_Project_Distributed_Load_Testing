'''
from kafka import KafkaProducer
import json
import time
import random

def produce_message(topic, message):
    producer = KafkaProducer(
        bootstrap_servers='kafka:9093',  # Replace with your Kafka bootstrap servers
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    producer.send(topic, value=message)
    producer.flush()

def simulate_load_test(driver_id):
    for _ in range(5):  # Simulate 5 requests
        latency = random.uniform(1, 10)  # Simulate response latency
        message = {
            "driver_id": driver_id,
            "latency": latency,
        }
        produce_message('load_test_metrics', message)
        time.sleep(2)  # Simulate a delay between requests

if __name__ == "__main__":
    driver_id = "driver_1"  # Replace with a unique identifier for each driver node
    while True:
        simulate_load_test(driver_id)
'''

from confluent_kafka import Producer
import requests

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',
}

producer = Producer(producer_config)

# Kafka topic to send test requests
topic = 'test_requests'

# Send test requests to the Kafka topic
def send_test_request(request_data):
    producer.produce(topic, key=None, value=request_data)
    producer.flush()

# Implement request execution and measurement here
# ...

if __name__ == '__main__':
    # Start Kafka producer
    app.run(port=5000)

