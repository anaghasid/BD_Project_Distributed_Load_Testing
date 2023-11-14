from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from kafka import KafkaProducer,KafkaConsumer
import requests
import json
from threading import Thread
import time

app = Flask(__name__)
CORS(app)
producer_config = {
    'bootstrap.servers': 'localhost:9092',
}
conumer_hearbeat_conf = {
    'bootstrap.servers': 'localhost:9092',
}
# Global variables for test ID and test configuration
current_test_id = 0
current_test_configuration = {}

# Kafka topic to send load test commands
load_test_commands_topic = "test_config"
trigger_test_command_topic = "trigger"
heartbeat_topic = "heartbeat"

producer = KafkaProducer(**producer_config)
server_heartbeats = {}

def send_load_test_command(command_data, topic):
    # Simulate sending load test command to Kafka
    # ALSO write produce part
    print(f"Sending load test command: {command_data} to topic: {topic}")
    producer.send(topic, key=None, value=command_data)
    producer.flush()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_configure', methods=['POST'])
def configure_test():
    global current_test_id, current_test_configuration
    # Increment the test ID
    current_test_id += 1

    # Get load test parameters from the form
    test_type = request.form.get('test_type')
    test_message_delay = request.form.get('test_message_delay')

    # Save the current test configuration
    current_test_configuration = {
        "test_id": current_test_id,
        "test_type": test_type,
        "test_message_delay": test_message_delay
    }
    if current_test_configuration:
        send_load_test_command(json.dumps(current_test_configuration), load_test_commands_topic)

    return render_template('index.html', message=f"Test configured with ID: {current_test_id}")

@app.route('/trigger_test')
def trigger_test():
    global current_test_configuration
    if not current_test_configuration:
        return render_template('index.html', error="Test configuration is not set. Please configure a test first.")

    # Send load test command to Driver Node via Kafka
    send_load_test_command(json.dumps(current_test_configuration), trigger_test_command_topic)

    return render_template('index.html', message="Test triggered successfully")

def heart_beat_consumer(heartbeat_topic):
    consumer = KafkaConsumer(conumer_hearbeat_conf)
    consumer.subscribe([heartbeat_topic])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(msg.error())
                break
            # Update server heartbeat in the list
            json_beat = msg.decode('utf-8')

            server_heartbeats[json_beat.get("node_id")] = time.time()
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def check_server_heartbeats():
    while True:
        # Check heartbeats every 0.1 seconds
        time.sleep(0.005)
        current_time = time.time()
        
        # Check each server's heartbeat
        for server, heartbeat_time in server_heartbeats.items():
            if current_time - heartbeat_time > 0.01:
                print(f"Server {server} is not responding!")


@app.before_request
def heart_beat_function():
    # Start Kafka consumer thread
    kafka_consumer_thread = Thread(target=heart_beat_consumer,args=heartbeat_topic)
    kafka_consumer_thread.start()   

    # Start heartbeat checker thread
    heartbeat_checker_thread = Thread(target=check_server_heartbeats)
    heartbeat_checker_thread.start()


if __name__ == '__main__':
    app.run(port=5000,debug=True)
