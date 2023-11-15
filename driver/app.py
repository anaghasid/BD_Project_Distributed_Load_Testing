from flask import Flask
from kafka import KafkaProducer, KafkaConsumer
from threading import Thread
import socket, json, time
import requests
app = Flask(__name__)

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



def register_with_kafka():
    time.sleep(32) #give some time for kafka to start up completely

    registration_producer = KafkaProducer(bootstrap_servers="bd_project_distributed_load_testing-kafka_node-1:9092")

    # Fetch IP of container
    hostname = socket.gethostname()
    node_IP = socket.gethostbyname(hostname)

    # Set node_id to the hostname of the container,will be unique!!
    node_ID = hostname

    registration_info = {"node_IP": node_IP, "node_ID": node_ID, "message_type": "DRIVER_NODE_REGISTER"}

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
    # responses is a list of all response times.
    # should we handle mean, median etc in orchestrator?
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    ascending_responses = sorted(responses)
    metrics = {
        "mean_latency" : sum(responses) / len(responses),
        "median_latency" : ascending_responses[int(len(responses)/2)],
        "min_latency" : ascending_responses[0],
        "max_latency" : ascending_responses[len(responses) - 1]
    }
    producer.send(topic_metrics, key=node_info["node_id"], value=metrics)
    producer.flush()


# Main function to perform load testing
def perform_load_test(requests_per_second, duration_seconds):
    interval = 1.0 / requests_per_second
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        send_http_request(node_info["node_id"])
        time.sleep(interval)
    # send as producer
    publish_metrics(response_times)
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



# @app.before_first_request
# def do_something_only_once():
node_info = register_with_kafka()
kafka_consumer_thread = Thread(target=consume_commands)


# view this at http://localhost:5000
@app.route("/")
def hello_world():
    return "<p>Hello, World , Drivers</p>"

if __name__ == "__main__":
    app.run(debug=False)