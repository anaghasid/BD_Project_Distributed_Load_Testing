#!/usr/bin/env python3

from flask import Flask
from kafka import KafkaProducer, KafkaConsumer
from threading import Thread
import socket, json, time, requests

app = Flask(__name__)

consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'load_test_group',
    'auto.offset.reset': 'earliest',
}

producer_config = {
    'bootstrap_servers': "localhost:9092",
}

topic_config = "test_config"
topic_trig = "trigger"
topic_heartbeat = "heartbeat"
topic_metrics = "metrics"

target_url = "http://localhost:5003/get_message"
response_times = []

def register_with_kafka():
    registration_producer = KafkaProducer(bootstrap_servers='localhost:9092')

    hostname = socket.gethostname()
    node_IP = socket.gethostbyname(hostname)
    node_ID = hostname + '3'

    registration_info = {"node_IP": node_IP, "node_id": node_ID, "message_type": "DRIVER_NODE_REGISTER"}
    registration_producer.send("register", json.dumps(registration_info).encode("utf-8"))
    print("send driver info", registration_info)
    registration_producer.flush()
    registration_producer.close()
    return registration_info

def send_http_request(node_id):
    try:
        start_time = time.time()
        response = requests.get(target_url)
        end_time = time.time()

        metrics = {
            "node_id": node_id,
            "response_time": float((end_time - start_time) * 1000)  # in milliseconds
        }

        response_times.append(metrics["response_time"])
    except Exception as e:
        print(f"Error sending request: {str(e)}")

def publish_metrics(responses):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    ascending_responses = sorted(responses)
    metrics = {
        "mean_latency": sum(responses) / len(responses),
        "median_latency": ascending_responses[int(len(responses)/2)],
        "min_latency": ascending_responses[0],
        "max_latency": ascending_responses[len(responses) - 1]
    }

    producer.send(topic_metrics, key=node_info["node_id"], value=metrics)
    producer.flush()

def perform_load_test(test_id, test_type, delay, total_req):
    # interval = 1.0 / requests_per_second
    # end_time = time.time() + duration_seconds

    # while time.time() < end_time:
    #     send_http_request(node_info["node_id"])
    #     time.sleep(interval)

    # publish_metrics(response_times)
    pass

def consume_commands():
    global consumer_config, topic_config, topic_trig
    print("hiiii")
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092')
    consumer.subscribe([topic_config, topic_trig])

    try:
        for msg in consumer:
            print(msg)
            command = json.loads(msg.value.decode('utf-8'))
            msg_topic = msg.topic

            if msg_topic == "test_config":
                global test_id, test_type, interval_seconds
                test_id = command.get("test_id")
                test_type = command.get("test_type")
                interval_seconds = command.get("test_message_delay")
                total_requests = command.get("message_count_per_driver")
                print("Received Test Configuration:")
                print(f"Test ID: {test_id}, Test type: {test_type}, Interval: {interval_seconds} seconds")

            elif msg_topic == "trigger":
                print("Received Trigger Message. Starting Load Test...")
                perform_load_test(test_id, test_type, interval_seconds, total_requests)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def send_heartbeat(registration_info):
    producer = KafkaProducer(**producer_config)
    heartbeat_interval = 0.04
    heartbeat_message = {
        "node_id": registration_info,
        "heartbeat": "YES"
    }

    try:
        while True:
            sending = json.dumps(heartbeat_message)
            producer.send(topic_heartbeat, value=sending.encode('utf-8'))
            producer.flush()
            time.sleep(heartbeat_interval)
    except KeyboardInterrupt:
        pass

node_info = register_with_kafka()
kafka_consumer_thread = Thread(target=consume_commands)
kafka_consumer_thread.start()

heartbeat_checker_thread = Thread(target=send_heartbeat, args=(node_info["node_id"],))
heartbeat_checker_thread.start()

@app.route("/")
def hello_world():
    return "<p>Hello, World, Drivers</p>"

if __name__ == "__main__":
    app.run(debug=True, port=5003)
