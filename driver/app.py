# driver app.py

from flask import Flask
from kafka import KafkaProducer
import socket,json,time
from heartbeat_producer import heartbeat_producer
from threading import Thread
import pandas as pd
from produce_metrics import initialize_produce_metrics


app = Flask(__name__)

response_times = []
def register_with_kafka():
    time.sleep(15) #give some time for kafka to start up completely

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

# @app.before_first_request
# def do_something_only_once():
node_info = register_with_kafka()

heartbeat_thread = Thread(target=heartbeat_producer)
heartbeat_thread.start()

metrics_produce_thread = Thread(target=initialize_produce_metrics,args=(node_info,))
metrics_produce_thread.start()



# view this at http://localhost:5000
@app.route("/")
def hello_world():
    return "<p>Hello, World from Driver</p>"

if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)