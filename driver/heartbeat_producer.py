from kafka import KafkaProducer
import socket
import time
import json

heartbeat_producer_conf = {'bootstrap_servers':"bd_project_distributed_load_testing-kafka_node-1:9092"}
heartbeat_topic='heartbeat'

def get_heartbeat_producer():
    return KafkaProducer(**heartbeat_producer_conf)

def produce_heartbeats():
    heartbeat_producer=get_heartbeat_producer()
    heartbeat_interval = 0.5
    hostname = socket.gethostname()

    heartbeat_message = {
        "node_id": hostname,
        "heartbeat": "YES",
        "timestamp": time.time()
    }
    heartbeat_message=json.dumps(heartbeat_message)

    try:
        while True:
            time.sleep(heartbeat_interval)
            heartbeat_producer.send(heartbeat_topic, value=heartbeat_message.encode('utf-8'))
            heartbeat_producer.flush()  # Ensure the message is sent immediately
    except KeyboardInterrupt:
        pass

def heartbeat_producer():
    produce_heartbeats()
