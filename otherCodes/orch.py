#!/usr/bin/env python3

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from kafka import KafkaProducer, KafkaConsumer
import json
from threading import Thread
import time
from flask_socketio import SocketIO
import uuid
import csv
import pandas as pd
import os
app = Flask(__name__)
socketio = SocketIO(app)

# do not move this line, because all threads need to wait for kafka brokers to start up completely
CORS(app)

load_test_commands_topic = "test_config"
trigger_test_command_topic = "trigger"
heartbeat_topic = "heartbeat"
metrics_topic = "metrics"

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
    global current_test_configuration
    current_test_id = uuid.uuid4()

    test_type = request.form.get('test_type')
    test_message_delay = request.form.get('test_message_delay')
    if test_type == "AVALANCHE":
        test_message_delay = 0

    req_per_driver = request.form.get("request_per_driver")

    current_test_configuration = {
        "test_id": str(current_test_id),
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
    kafka_consumer_thread = Thread(target=heart_beat_consumer)
    kafka_consumer_thread.start()

    heartbeat_checker_thread = Thread(target=check_server_heartbeats)
    heartbeat_checker_thread.start()

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
            if current_time - heartbeat_time > 1.0 and heartbeat_time != 0:
                print(f"Server {server} is not responding!")


def weighted_metrics(df):
    test_id = df["test_id"]
    # Aggregate metrics
    total_requests = df['number_of_requests'].sum()
    latency_mean = (df['mean_latency'] * df['number_of_requests']).sum() / total_requests
    latency_min = (df['min_latency']).min()
    latency_median = (df['median_latency']).median()
    latency_max = (df['max_latency']).max() 
    return pd.Series({
        'test_id': test_id,
        'mean_Latency': latency_mean,
        'min_Latency': latency_min,
        'max_Latency': latency_max,
        'median_latency': latency_median,
        'number_of_request':total_requests
    })

def aggregated_driver():
    df = pd.read_csv('dashboard.csv')
   
    aggregated_driver = df.groupby(['test_id','node_id']).apply(weighted_metrics).reset_index()


    with open('agg_driver','a') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows([aggregated_driver])
    
    total_aggregate = df.groupby('test_id').apply(weighted_metrics)

    socketio.emit('driver_aggregate',aggregated_driver)
    socketio.emit('total_aggregate',total_aggregate)


def store_metric(metrics):
    is_new_file = os.path.exists('dashboard.csv')

    with open('dashboard.csv','a') as f:
        node_id = metrics["node_id"]
        test_id = metrics["test_id"]
        report_id = metrics["report_id"]
        num_requests = metrics["num_requests"]
        mean = metrics["metrics"]["mean_latency"]
        median = metrics["metrics"]["median_latency"]
        mini = metrics["metrics"]["min_latency"]
        maxi = metrics["metrics"]["max_latency"]
        csv_writer = csv.writer(f)
        if is_new_file:
            # Add headers if the file is new
            csv_writer.writerow(["node_id", "test_id", "num_requests", "mean_latency", "median_latency", "min_latency", "max_latency"])
        csv_writer.writerow([node_id,test_id,report_id,num_requests,mean,median,mini,maxi])

def metrics_consumer():
    consumer = KafkaConsumer(metrics_topic, bootstrap_servers='localhost:9092')
    try:
        st = time.time()
        for message in consumer:
            json_metric = json.loads(message.value.decode('utf-8'))
            print(json_metric)
            store_metric(json_metric)
            print()
            if time.time() - st >=1:
                aggregated_driver()
                st = time.time()
            
            socketio.emit('metric_update', json_metric)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


get_driver_info()


metrics_consumer_thread = Thread(target=metrics_consumer)
metrics_consumer_thread.start()

if __name__ == "__main__":
    app.run(debug=True, port=6500)
    print("Running")
