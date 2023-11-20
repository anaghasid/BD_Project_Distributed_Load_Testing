from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from kafka import KafkaProducer,KafkaConsumer
import json
from threading import Thread
import time
from flask_socketio import SocketIO
import time
import uuid
from registration_consumer import initialize_registration_consumer
from heartbeat_consumer import initialize_heartbeat_consumer
import pandas as pd
from metrics_consume import initialize_metrics_consumer

app = Flask(__name__)
socketio = SocketIO(app)

time.sleep(10)#do not move this line, because all threads need to wait for kafka brokers to start up completely

CORS(app)
# producer_config = {
#      'bootstrap_servers':"bd_project_distributed_load_testing-kafka_node-1:9092",
# }
# consumer_conf = {
#      'bootstrap_servers':"bd_project_distributed_load_testing-kafka_node-1:9092",
# }
load_test_commands_topic = "test_config"
trigger_test_command_topic = "trigger"
heartbeat_topic = "heartbeat"
metrics_topic = "metrics"

# producer = KafkaProducer(**producer_config)

# server_heartbeats = {}
# current_test_configuration={}

driver_information={}
# initialize_registration_consumer(driver_information)
registration_thread=Thread(target=initialize_registration_consumer,args=(driver_information,socketio))
registration_thread.start()


server_heartbeats={}
heartbeat_thread = Thread(target=initialize_heartbeat_consumer, args=(server_heartbeats,socketio))
heartbeat_thread.start()
# heartbeat_check = Thread(target=initiliaze_heartbeat_checker,args=(server_heartbeats,socketio))
metrics_consumer_thread = Thread(target=initialize_metrics_consumer,args=(socketio,))
metrics_consumer_thread.start()

@app.route("/")
def index():
    return render_template("index.html",server_heartbeats=server_heartbeats,socketio=socketio)

def send_load_test_command(command_data, topic):
    producer = KafkaProducer(bootstrap_servers="bd_project_distributed_load_testing-kafka_node-1:9092")
    command_data = command_data.encode('utf-8')
    print(f"Sending load test command: {command_data} to topic: {topic}")
    producer.send(topic, key=None, value=command_data)
    producer.flush()


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
    print("hi")
    global current_test_configuration
    if not current_test_configuration:
        return render_template('index.html', error="Test configuration is not set. Please configure a test first.")
    print("bye")
    trigger_message = {
        "test_id": current_test_configuration["test_id"],
        "trigger": "YES"
    }
    
    # heartbeat_thread.start()

    print(f"sent test command {trigger_message}, {trigger_test_command_topic}")
    send_load_test_command(json.dumps(trigger_message), trigger_test_command_topic)

    return render_template('index.html', message="Test triggered successfully")

if __name__ == "__main__":
    app.run(debug=True)

# def send_load_test_command(command_data, topic):
#     # Simulate sending load test command to Kafka
#     # ALSO write produce part
#     print(f"Sending load test command: {command_data} to topic: {topic}")
#     producer.send(topic, key=None, value=command_data)
#     producer.flush()


# @app.route('/test_configure', methods=['POST'])
# def configure_test():
#     global current_test_id, current_test_configuration
#     # Increment the test ID
#     current_test_id += 1

#     # Get load test parameters from the form
#     test_type = request.form.get('test_type')
#     test_message_delay = request.form.get('test_message_delay')

#     # Save the current test configuration
#     current_test_configuration = {
#         "test_id": current_test_id,
#         "test_type": test_type,
#         "test_message_delay": test_message_delay
#     }
#     if current_test_configuration:
#         send_load_test_command(json.dumps(current_test_configuration), load_test_commands_topic)

#     return render_template('index.html', message=f"Test configured with ID: {current_test_id}")

# @app.route('/trigger_test')
# def trigger_test():
#     global current_test_configuration
#     if not current_test_configuration:
#         return render_template('index.html', error="Test configuration is not set. Please configure a test first.")

#     # Send load test command to Driver Node via Kafka
#     send_load_test_command(json.dumps(current_test_configuration), trigger_test_command_topic)

#     return render_template('index.html', message="Test triggered successfully")

# def heart_beat_consumer():
#     global heartbeat_topic
#     consumer = KafkaConsumer(consumer_conf)
#     consumer.subscribe([heartbeat_topic])

#     try:
#         while True:
#             msg = consumer.poll(1.0)
#             if msg is None:
#                 continue
#             if msg.error():
                
#                 break
#             # Update server heartbeat in the list
#             json_beat = json.loads(msg.value.decode('utf-8'))

#             server_heartbeats[json_beat.get("node_id")] = time.time()
#     except KeyboardInterrupt:
#         pass
#     finally:
#         consumer.close()

# def check_server_heartbeats():
#     while True:
#         # Check heartbeats every 0.1 seconds
#         time.sleep(0.005)
#         current_time = time.time()
        
#         # Check each server's heartbeat
#         for server, heartbeat_time in server_heartbeats.items():
#             if current_time - heartbeat_time > 0.01:
#                 print(f"Server {server} is not responding!")

# def metrics_consumer():
#     global metrics_topic
#     topic =metrics_topic
#     consumer = KafkaConsumer(topic,consumer_conf)
#     try:
#         while True:
#             msg = consumer.poll(1.0)
#             if msg is None:
#                 continue
#             if msg.error():
#                 print(msg.error())
#                 break
#             # Update server heartbeat in the list
#             json_metric = json.loads(msg.value.decode('utf-8'))
#             socketio.emit('metric_update',json_metric)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         consumer.close()




# @app.before_request
# def heart_beat_function():
    # Start Kafka consumer driver registration

# kafka_consumer_thread = Thread(target=heart_beat_consumer)
# kafka_consumer_thread.start()

# # Start heartbeat checker thread
# heartbeat_checker_thread = Thread(target=check_server_heartbeats)
# heartbeat_checker_thread.start()

# # Start metrics consumer thread
# metrics_consumer_thread = Thread(target=metrics_consumer)
# metrics_consumer_thread.start()




if __name__ == "__main__":
    app.run(debug=True)
