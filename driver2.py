import threading
from kafka import KafkaConsumer, KafkaProducer
import time
import requests
import uuid
import json

producer_config = {
    'bootstrap_servers': 'your_kafka_broker(s)',
    # Other producer configuration options
}

producer = KafkaProducer(**producer_config)


heartbeat_message = "Heartbeat Message"
heartbeat_topic = "heartbeat_topic"

def send_heartbeat(producer, heartbeat_topic, registration_info):
    heartbeat_interval = 0.01
    heartbeat_message = {
        "node_id": registration_info['node_ID'],
        "heartbeat": "YES"
    }
    try:
        while True:
            producer.send(heartbeat_topic, value=heartbeat_message.encode('utf-8'))
            producer.flush()  # Ensure the message is sent immediately
            time.sleep(heartbeat_interval)
    except KeyboardInterrupt:
        pass

def consume_messages(consumer, topic_name):
    for message in consumer:
        print(f"Received message from {topic_name}: {message.value.decode('utf-8')}")





def send_request_to_target_server():
    target_server_url = 'http://target_server:8000/test_endpoint'
    response = requests.get(target_server_url)

    # Process the response if needed
    print(f"Request sent to Target Server. Response: {response.text}")



# ---------------------------------------------------------------------------------------
# Kafka configuration
kafka_bootstrap_servers = 'your_kafka_bootstrap_servers'
orchestrator_topic = 'orchestrator_topic'
metrics_topic = 'metrics_topic'

# Unique identifier for the driver node
node_id = str(uuid.uuid4())

# Function to send HTTP requests to the target web server
def send_http_request(url):
    # Implement your HTTP request logic here
    target_server_url = 'http://target_server:8000/test_endpoint'
    response = requests.get(target_server_url)
    # Process the response if needed
    print(f"Request sent to Target Server. Response: {response.text}")
    response_time = 100  # Replace with the actual response time
    return response_time

# Function to publish metrics to the metrics topic
def publish_metrics(test_id, report_id, metrics):
    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    metrics_message = {
        "node_id": node_id,
        "test_id": test_id,
        "report_id": report_id,
        "metrics": metrics
    }

    producer.send(metrics_topic, key=node_id, value=metrics_message)
    producer.flush()

# Function to perform load testing
def perform_load_test(test_id, target_url, interval_seconds):
    while True:
        # Send HTTP request to the target web server
        response_time = send_http_request(target_url)

        # Record metrics
        metrics = {
            "mean_latency": "",  # Replace with actual mean latency
            "median_latency": "",  # Replace with actual median latency
            "min_latency": "",  # Replace with actual min latency
            "max_latency": ""   # Replace with actual max latency
        }

        # Publish metrics to the metrics topic
        report_id = str(uuid.uuid4())
        publish_metrics(test_id, report_id, metrics)

        # Wait for the specified interval before sending the next request
        time.sleep(interval_seconds)

# Function to consume commands from the orchestrator
def consume_commands():
    consumer = KafkaConsumer(
        orchestrator_topic,
        group_id='driver_group',
        bootstrap_servers=kafka_bootstrap_servers,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for msg in consumer:
        # Extract relevant information from the received message
        command = msg.value

        test_id = command.get("test_id")
        target_url = command.get("target_url")
        interval_seconds = command.get("interval_seconds")

        # Perform load test with the provided parameters
        perform_load_test(test_id, target_url, interval_seconds)

if __name__ == '__main__':
    # Start the consumer for receiving commands from the orchestrator
    consume_commands()



    

topic_config = 'test_config'
topic_trig = 'trigger'
topic_heartbeat = 'heartbeat'
# Create and start consumer threads
thread1 = threading.Thread(target=consume_messages, args=(topic_config, 'topic1'))
thread2 = threading.Thread(target=consume_messages, args=(topic_trig, 'topic2'))
thread3 = threading.Thread(target=send_heartbeat, args=(producer, topic_heartbeat, ''))

# Start the threads
thread1.start()
thread2.start()

# Wait for the threads to finish
thread1.join()
thread2.join()
