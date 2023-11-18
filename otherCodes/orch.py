#!/usr/bin/env python3

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from kafka import KafkaProducer, KafkaConsumer
import json
from threading import Thread
import time
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# do not move this line, because all threads need to wait for kafka brokers to start up completely
CORS(app)

load_test_commands_topic = "test_config"
trigger_test_command_topic = "trigger"
heartbeat_topic = "heartbeat"
metrics_topic = "metrics"
current_test_id = 0

server_heartbeats = {}
driver_information = []


def get_driver_info():
    print("hi in orch")
    register_topic = "register"
    consumer_conf = {
        'bootstrap_servers': "bd_project_distributed_load_testing-kafka_node-1:9092",
    }

    registration_consumer = KafkaConsumer(register_topic, bootstrap_servers='localhost:9092')

    try:
        driver_count = 2
        for message in registration_consumer:
            driver = json.loads(message.value.decode("utf-8"))

            if driver["message_type"] == "DRIVER_NODE_REGISTER":
                if driver.get("node_id") not in server_heartbeats:
                    server_heartbeats[driver.get("node_id")] = 0

            driver_information.append(driver)
            driver_count -= 1
            if driver_count <= 0:
                break
        registration_consumer.close()

    except Exception as e:
        print(f"Error processing registration_consumers: {str(e)}")


@app.route("/driver_info")
def get_registration_info():
    return render_template("driver_info.html", driver_info_list=driver_information)


def send_load_test_command(command_data, topic):
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    command_data = command_data.encode('utf-8')
    print(f"Sending load test command: {command_data} to topic: {topic}")
    producer.send(topic, key=None, value=command_data)
    producer.flush()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test_configure', methods=['POST'])
def configure_test():
    global current_test_id, current_test_configuration
    current_test_id += 1

    test_type = request.form.get('test_type')
    test_message_delay = request.form.get('test_message_delay')
    if test_type == "AVALANCHE":
        test_message_delay = 0

    req_per_driver = request.form.get("request_per_driver")

    current_test_configuration = {
        "test_id": current_test_id,
        "test_type": test_type,
        "test_message_delay": test_message_delay,
        "message_count_per_driver": req_per_driver
    }

    if current_test_configuration:
        send_load_test_command(json.dumps(current_test_configuration), load_test_commands_topic)

    return render_template('index.html', message=f"Test configured with ID: {current_test_id}")


@app.route('/trigger_test')
def trigger_test():
    global current_test_configuration
    if not current_test_configuration:
        return render_template('index.html', error="Test configuration is not set. Please configure a test first.")

    trigger_message = {
        "test_id": current_test_configuration["test_id"],
        "trigger": "YES"
    }
    send_load_test_command(json.dumps(trigger_message), trigger_test_command_topic)

    return render_template('index.html', message="Test triggered successfully")


def heart_beat_consumer():
    consumer = KafkaConsumer(heartbeat_topic, bootstrap_servers='localhost:9092')
    try:
        for message in consumer:
            json_beat = json.loads(message.value.decode('utf-8'))
            server_heartbeats[json_beat.get("node_id")] = time.time()
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


def check_server_heartbeats():
    while True:
        time.sleep(0.008)
        for server, heartbeat_time in server_heartbeats.items():
            current_time = time.time()
            if current_time - heartbeat_time > 0.1 and heartbeat_time != 0:
                print(f"Server {server} is not responding!")


def metrics_consumer():
    consumer = KafkaConsumer(metrics_topic, bootstrap_servers='localhost:9092')
    try:
        for message in consumer:
            json_metric = json.loads(message.decode('utf-8'))
            socketio.emit('metric_update', json_metric)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


get_driver_info()
kafka_consumer_thread = Thread(target=heart_beat_consumer)
kafka_consumer_thread.start()

heartbeat_checker_thread = Thread(target=check_server_heartbeats)
heartbeat_checker_thread.start()

metrics_consumer_thread = Thread(target=metrics_consumer)
metrics_consumer_thread.start()

if __name__ == "__main__":
    app.run(debug=True, port=6500)
    print("Running")
