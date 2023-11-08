

from flask import Flask, request, jsonify
import requests
from kafka import KafkaProducer

app = Flask(__name__)

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',
}

# Kafka topic to send load test commands
load_test_commands_topic = 'load_test_commands'

producer = KafkaProducer(**producer_config)

def send_load_test_command(command_data):
    producer.send(load_test_commands_topic, key=None, value=command_data)
    producer.flush()

@app.route('/trigger_load_test', methods=['POST'])
def trigger_load_test():
    # Get load test parameters from the request
    test_params = request.json

    # Send load test command to Driver Node via Kafka
    send_load_test_command(test_params)

    return jsonify({"message": "Load test triggered"})

if __name__ == '__main__':
    app.run(port=5000)
