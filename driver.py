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


from kafka import KafkaProducer
import requests

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',
}

producer = KafkaProducer(producer_config)

# Kafka topic to send test requests
topic = 'test_requests'

# Send test requests to the Kafka topic
def send_test_request(request_data):
    producer.send(topic, key=None, value=request_data)
    producer.flush()

# Implement request execution and measurement here
# ...

if __name__ == '__main__':
    # Start Kafka producer
    app.run(port=5000)

'''

from flask import Flask, jsonify
from kafka import KafkaConsumer
import requests

app = Flask(__name__)

# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'load_test_group',
    'auto.offset.reset': 'earliest',
}

# Kafka topic to receive load test commands
load_test_commands_topic = 'load_test_commands'

consumer = KafkaConsumer(load_test_commands_topic, **consumer_config)

def consume_load_test_commands():
    for message in consumer:
        handle_load_test_command(message.value)

def handle_load_test_command(command_data):
    # Perform orchestration to start the load test
    # ...

    # Simulate sending requests to Target Server
    send_request_to_target_server()

def send_request_to_target_server():
    # Modify this function to send actual requests to the Target Server
    target_server_url = 'http://target_server:8000/test_endpoint'
    response = requests.get(target_server_url)

    # Process the response if needed
    print(f"Request sent to Target Server. Response: {response.text}")

if __name__ == '__main__':
    # Start Kafka consumer in a separate thread
    from threading import Thread
    kafka_consumer_thread = Thread(target=consume_load_test_commands)
    kafka_consumer_thread.start()

    # Start Flask app
    app.run(port=5001)
