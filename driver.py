from flask import Flask, jsonify
from kafka import KafkaConsumer, KafkaProducer
import time
import requests
from flask_socketio import SocketIO
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app)


# IMPORTANT: SEQUENTIAL REQUESTS PER TRIGGER IS DONE HERE
# HANDLE X REQUESTS SIMULATANEOUSLY, AVALANCHE 
# TARGET SERVER URL
# make median latency actually median


# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'load_test_group',
    'auto.offset.reset': 'earliest',
}

topic_config = 'test_config'
topic_trig = 'trigger'
topic_heartbeat = 'heartbeat'
topic_metrics = "metrics"
target_url = "WRITE###**"
response_times = []

# def perform_load_test(test_id, test_type, interval_seconds):
#     if test_type=="AVALANCHE":

def send_http_request(node_id):
    try:
        start_time = time.time()
        response = requests.get(target_url)
        end_time = time.time()

        # Record metrics
        metrics = {
            "node_id": node_id,
            "response_time": float((end_time - start_time) * 1000)  # in milliseconds
        }

        response_times.append(metrics["response_time"]) 

    except Exception as e:
        print(f"Error sending request: {str(e)}")

# Function to publish metrics to the metrics topic
def publish_metrics(responses):
    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    ascending_responses = sorted(responses)
    metrics = {
        "mean_latency" : sum(responses) / len(responses),
        "median_latency" : ascending_responses[int(len(responses)/2)],
        "min_latency" : ascending_responses[0],
        "max_latency" : ascending_responses[len(responses) - 1]
    }


    producer.send(topic_metrics, key=node_id, value=metrics)
    producer.flush()


# Main function to perform load testing
def perform_load_test(requests_per_second, duration_seconds):
    interval = 1.0 / requests_per_second
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        send_http_request()
        time.sleep(interval)
    # send as producer
    publish_metrics(metrics)

    # reset global dict



def consume_commands():
    global consumer_config
    global topic_config
    global topic_trig
    consumer = KafkaConsumer(consumer_config)
    # or **consumer_config?
    consumer.subscribe([topic_config, topic_trig])
    try:
        while True:
            msg = consumer.poll(2.0)
            if msg is None:
                continue
            if msg.error():
                print(msg.error())
                break

            for msg in consumer:
                # Extract relevant information from the received message
                command = msg.value
                msg_topic = msg.topic

                # Check if the message is a test configuration message
                if msg_topic == "test_config":
                    global test_id, test_type, interval_seconds
                    test_id = command.get("test_id")
                    test_type = command.get("test_type")
                    interval_seconds = command.get("interval_seconds")
                    print("Received Test Configuration:")
                    print(f"Test ID: {test_id}, Test type: {test_type}, Interval: {interval_seconds} seconds")

                # Check if the message is a trigger message
                elif msg_topic == "trigger":
                    print("Received Trigger Message. Starting Load Test...")
                    perform_load_test(test_id, test_type, interval_seconds)
        pass
    finally:
        consumer.close()

    

def send_heartbeat(producer, registration_info):
    global topic_heartbeat
    heartbeat_interval = 0.5
    heartbeat_message = {
        "node_id": registration_info['node_ID'],
        "heartbeat": "YES"
    }
    try:
        while True:
            producer.send(topic_heartbeat, value=heartbeat_message.encode('utf-8'))
            producer.flush()  # Ensure the message is sent immediately
            time.sleep(heartbeat_interval)
    except KeyboardInterrupt:
        pass


# ---------------------------
# SOCKET STUFF
'''
@socketio.on('message_from_kafka')
def handle_message(message):
    socketio.emit('kafka_message', message)

def kafka_consumer():
    consumer = KafkaConsumer('your_topic', bootstrap_servers='your_kafka_brokers')
    for message in consumer:
        socketio.emit('kafka_message', message.value.decode('utf-8'))
'''
#  -----------------------------------

# load_test_commands_topic = 'load_test_commands'

# consumer = KafkaConsumer(load_test_commands_topic, **consumer_config)

# @app.route('/consume_load_test_commands', methods=['GET'])
# def consume_load_test_commands():
#     for message in consumer:
#         handle_load_test_command(message.value)

#     return jsonify({"message": "Load test commands consumed"})

# def handle_load_test_command(command_data):
#     # Perform orchestration to start the load test
#     # ...

#     # Simulate sending requests to Target Server
#     send_request_to_target_server()

# def send_request_to_target_server():
#     # Modify this function to send actual requests to the Target Server
#     target_server_url = 'http://target_server:8000/test_endpoint'
#     response = requests.get(target_server_url)

#     # Process the response if needed
#     print(f"Request sent to Target Server. Response: {response.text}")

# if __name__ == '__main__':
#     app.run(port=5001)


