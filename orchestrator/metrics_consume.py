from kafka import KafkaConsumer
import json 
import time
import csv
import os
import pandas as pd
import socket
from threading import Thread

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

    # print(df['test_id'][1:])
    agg_driver = aggregated_driver.to_json(orient="records")
    print("agg driver = ",agg_driver)
    
    total_aggregate = df.groupby('test_id').apply(weighted_metrics)
    total_agg_json = total_aggregate.to_json(orient="records")

    socketio.emit('aggregate_update',agg_driver)
    socketio.emit('total_aggregate',total_agg_json)

def thread_aggr(socketio):
    curr_time = time.time()
    while(True):
        if time.time()-curr_time >=0.5:
            aggregated_driver(socketio)
            curr_time = time.time()

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

def metrics_consumer(socketio,aggr_thread):
    # global aggr_thread
    consumer = KafkaConsumer("metrics",**metrics_consumer_conf)
    print(f"metrics consumer in {socket.gethostname()} is now active")
    try:
        st = time.time()
        ct = False
        for message in consumer:
            json_metric = json.loads(message.value.decode('utf-8'))
            # print(json_metric,"in metrics_consumer")
            store_metric(json_metric,socketio)
            print(socket)
            if(not ct):
               aggr_thread.start()
               ct = True
            print(json_metric)
            socketio.emit('metric_update', json_metric)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
def initialize_metrics_consumer(socketio):
    aggr_thread  = Thread(target = thread_aggr,args  = (socketio,))
    metrics_consumer(socketio,aggr_thread)