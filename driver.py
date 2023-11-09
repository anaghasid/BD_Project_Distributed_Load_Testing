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

@app.route('/consume_load_test_commands', methods=['GET'])
def consume_load_test_commands():
    for message in consumer:
        handle_load_test_command(message.value)

    return jsonify({"message": "Load test commands consumed"})

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
    app.run(port=5001)


