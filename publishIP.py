import socket
from kafka import KafkaProducer
import uuid
import json
import sys
import os
kafka_node_broker=sys.argv[1]+":9092"
orchestrator_node_broker=sys.argv[2]+":5000"

#fetch IP address of container
hostname=socket.gethostname()
node_IP=socket.gethostbyname(hostname)

driver_container_id = os.popen("cat /proc/self/cgroup | grep 'docker' | sed 's/^.*\///' | tail -n1").read().strip()
#generate an id for the node
node_id=f"{uuid.uuid4()}_{driver_container_id}"

registration_info={"node_id":node_id,"node_IP":node_IP,"message_type":"DRIVER_NODE_REGISTER"}
print(registration_info)

registration_producer=KafkaProducer(bootstrap_servers=kafka_node_broker)

registration_producer.send("register",json.dumps(registration_info).encode("utf-8"))