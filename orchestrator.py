'''
from kafka import KafkaConsumer

def consume_messages(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='kafka:9093',  # Replace with your Kafka bootstrap servers
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    try:
        for message in consumer:
            print(f"Received message: {message.value}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages('load_test_metrics')


from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Stores statistics for load tests
metrics_store = []

@app.route('/trigger_load_test', methods=['POST'])
def trigger_load_test():
    # Get load test parameters from the request
    test_params = request.json

    # Perform orchestration to start driver nodes with test parameters
    # ...

    return jsonify({"message": "Load test triggered"})

@app.route('/get_stats', methods=['GET'])
def get_stats():
    # Provide statistics from the metrics_store
    # ...

    return jsonify({"statistics": metrics_store})

if __name__ == '__main__':
    app.run(port=5000)
'''


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
