from kafka import KafkaProducer,KafkaConsumer
import uuid
import time
import json
import requests

consumer_conf = {
        'bootstrap_servers': "bd_project_distributed_load_testing-kafka_node-1:9092",
    }
topic_metrics  = 'metrics'

def publish_metrics(node_info,test_id,responses):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    ascending_responses = sorted(responses)
    metrics = {
        "mean_latency": sum(responses) / len(responses),
        "median_latency": ascending_responses[int(len(responses)/2)],
        "min_latency": ascending_responses[0],
        "max_latency": ascending_responses[len(responses) - 1]
    }
    metrics_message = {
        "node_id": node_info["node_id"],
        "test_id": test_id,
        "report_id": str(uuid.uuid4()),
        "num_requests":len(responses),
        "metrics": metrics
    }
    with open(f'driver_storage_{node_info["node_id"]}.json','a') as f:
        f.append(json.dumps(metrics_message,indent=4))
    print("Metrics message sending",metrics_message)
    producer.send(topic_metrics, value=json.dumps(metrics_message).encode('utf-8'))
    producer.flush()

def perform_load_test(node_info,test_id, test_type, delay, total_req):
    global topic_metrics
    target_url = 'http://localhost:5003:/metrics'
    response_times = []
    if test_type == 'tsunami':
        metrics_start = time.time()
        for i in range(int(total_req)):
            start = time.time()
            response = requests.get(target_url)
            end = time.time()
            latency = float((end - start))
            print("Latency is",latency)
            response_times.append(latency)


            print("time passed=",time.time() - metrics_start)
            if time.time() - metrics_start >= 0.5:
                publish_metrics(test_id,response_times)
                response_times = []
                metrics_start = time.time()

            # doing this to take out the time taken for one respone
            # pray to god that delay > latency
            # also pray to god that delay << 1s
            time.sleep((int(delay)-latency)/1000)
        publish_metrics(node_info,test_id,response_times)

    if test_type=='avalanche':
        metrics_start = time.time()
        for i in range(int(total_req)):
            print("request number:", i)
            start = time.time()
            response = requests.get(target_url)
            end = time.time()
            latency = float((end - start) * 1000)
            response_times.append(latency)

            print("time passed=",time.time() - metrics_start)
            if time.time() - metrics_start >= 0.5:          
                publish_metrics(test_id,response_times)
                response_times = []
                metrics_start = time.time()

        publish_metrics(test_id,response_times)


def consume_commands(node_info):
    global consumer_config,topic_config,topic_trig
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
                print(f"Test ID: {test_id}, Test type: {test_type}, Interval: {interval_seconds} seconds\n")


            elif msg_topic == "trigger":
                print("Received Trigger Message. Starting Load Test...")
                perform_load_test(node_info,test_id, test_type, interval_seconds, total_requests)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def initialize_produce_metrics(node_info):
    consume_commands(node_info)