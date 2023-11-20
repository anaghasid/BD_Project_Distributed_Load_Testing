from kafka import KafkaConsumer
import json 
import time
import csv
import os
import pandas as pd
import socket

metrics_consumer_conf = {'bootstrap_servers': 'bd_project_distributed_load_testing-kafka_node-1:9092'}
metrics_topic = 'metrics'

def weighted_metrics(df):
    print(df)
    
    # Aggregate metrics
    total_requests = df['num_requests'].sum()
    latency_mean = (df['mean_latency'] * df['num_requests']).sum() / total_requests
    latency_min = (df['min_latency']).min()
    latency_median = (df['median_latency']).median()
    latency_max = (df['max_latency']).max() 
    return pd.Series({
        'mean_Latency': latency_mean,
        'min_Latency': latency_min,
        'max_Latency': latency_max,
        'median_latency': latency_median,
        'number_of_request':total_requests
    })

def aggregated_driver(socketio):
    with open("dashboard.json", "r") as json_file:
        existing_data = json.load(json_file)

# Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(existing_data)
    aggregated_driver = df.groupby(['test_id','node_id']).apply(weighted_metrics).reset_index()

    with open('dashboard.json', 'r') as json_file:
        data = json.load(json_file)

# Remove the string part and create DataFrame
    df = pd.DataFrame(data)

    # print(df['test_id'][1:])
    aggregated_driver = df.groupby(['test_id','node_id']).apply(weighted_metrics)
    agg_driver = aggregated_driver.to_json(orient="records")
    print(aggregated_driver)

    try:
        with open("aggregated.json", "r") as json_file:
            existing_daxta = json.load(json_file)
    except FileNotFoundError:
        existing_data = []

    existing_data.append(agg_driver)

    with open("dashboard.json", "w") as json_file:
        json.dump(existing_data, json_file, indent=2)
    
    total_aggregate = df.groupby('test_id').apply(weighted_metrics)
    total_agg_json = total_aggregate.to_json(orient="records")
    socketio.emit('driver_aggregate',agg_driver)
    socketio.emit('total_aggregate',total_agg_json)


def store_metric(metrics,socketio):
    # print("hi in metrics store")
    node_id = metrics["node_id"]
    test_id = metrics["test_id"]
    report_id = metrics["report_id"]
    num_requests = metrics["num_requests"]
    mean = metrics["metrics"]["mean_latency"]
    median = metrics["metrics"]["median_latency"]
    mini = metrics["metrics"]["min_latency"]
    maxi = metrics["metrics"]["max_latency"]

    metrics_data = {
    "node_id": node_id,
    "test_id": test_id,
    "report_id": report_id,
    "num_requests": num_requests,
    "mean_latency": mean,
    "median_latency": median,
    "min_latency": mini,
    "max_latency": maxi,
    }
    print(metrics_data,"is here")

    # Dump the JSON object to a file
    try:
        with open("dashboard.json", "r") as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        existing_data = []

# Append new data to the existing data
    existing_data.append(metrics_data)

# Dump the updated data back to the file
    with open("dashboard.json", "w") as json_file:
        json.dump(existing_data, json_file, indent=4)

def metrics_consumer(socketio):
    consumer = KafkaConsumer("metrics",**metrics_consumer_conf)
    print(f"metrics consumer in {socket.gethostname()} is now active")
    try:
        st = time.time()
        for message in consumer:
            json_metric = json.loads(message.value.decode('utf-8'))
            # print(json_metric,"in metrics_consumer")
            store_metric(json_metric,socketio)
            print(socket)
            if time.time() - st >=1:
                aggregated_driver(socketio)
                st = time.time()
            
            print(json_metric)
            socketio.emit('metric_update', json_metric)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def initialize_metrics_consumer(socketio):
    metrics_consumer(socketio)