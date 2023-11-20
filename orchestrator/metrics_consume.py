from kafka import KafkaConsumer
import json 
import time
import csv
import os
import pandas as pd


metrics_consumer_conf = {'bootstrap_servers': 'bd_project_distributed_load_testing-kafka_node-1:9092'}
metrics_topic = 'metrics'

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

def aggregated_driver(socketio):
    df = pd.read_json('dashboard.json',orient="index")
    print(df)
    aggregated_driver = df.groupby(['test_id','node_id']).apply(weighted_metrics).reset_index()


    with open('agg_driver','a') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows([aggregated_driver])
    
    total_aggregate = df.groupby('test_id').apply(weighted_metrics)

    socketio.emit('driver_aggregate',aggregated_driver)
    socketio.emit('total_aggregate',total_aggregate)


def store_metric(metrics,socketio):
    print("hi in metrics store")
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
    "mean": mean,
    "median": median,
    "min_latency": mini,
    "max_latency": maxi,
    }
    print(metrics_data,"is here")

    # Dump the JSON object to a file
    with open("dashboard.json", "a") as json_file:   
        json.dump(metrics_data, json_file,indent=4)


def metrics_consumer(socketio):
    consumer = KafkaConsumer("metrics",**metrics_consumer_conf)
    try:
        st = time.time()
        for message in consumer:
            json_metric = json.loads(message.value.decode('utf-8'))
            print(json_metric,"in metrics_consumer")
            store_metric(json_metric,socketio)
            print("here")
            if time.time() - st >=1:
                aggregated_driver(socketio)
                st = time.time()
            
            socketio.emit('metric_update', json_metric)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def initialize_metrics_consumer(socketio):
    metrics_consumer(socketio)