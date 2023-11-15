from flask import Flask
from kafka import KafkaProducer
import socket,json,time
from flask_socketio import SocketIO

app = Flask(__name__)

registration_producer = KafkaProducer(bootstrap_servers="bd_project_distributed_load_testing-kafka_node-1:9092")

def register_with_kafka():
    time.sleep(15) #give some time for kafka to start up completely


    # Fetch IP of container
    hostname = socket.gethostname()
    node_IP = socket.gethostbyname(hostname)

    # Set node_id to the hostname of the container,will be unique!!
    node_ID = hostname

    registration_info = {"node_IP": node_IP, "node_ID": node_ID, "message_type": "TARGET_SERVER_NODE_REGISTER"}

    registration_producer.send("register", json.dumps(registration_info).encode("utf-8"))
    print("send driver info", registration_info)
    registration_producer.flush()
    registration_producer.close()

register_with_kafka()

# view this at http://localhost:5003
@app.route("/")
def hello_world():
    return "<p>Hello, World from target server</p>"

@app.route("/test_endpoint")

def get_message():
    data = json.loads({"message":"hiiiii this is message from target server"})
    return data

if __name__ == "__main__":
    app.run(debug=True)



