# from flask import Flask, jsonify
# from flask_cors import CORS
# import requests
# import json

# app = Flask(__name__)

# # Global variable for test ID
# current_test_id = 0

# # Kafka producer configuration
# producer_config = {
#     'bootstrap.servers': 'localhost:9092',
# }
# CORS(app)
# # Kafka topic to send load test commands
# load_test_commands_topic = 'test_config'
# topic_trigger_test_command = 'trigger'

# final_test_id = ''
# # producer = KafkaProducer(**producer_config)

# @app.route('/',methods = ['GET'])
# def pp():
#     return jsonify({"test":"i am a test"})


# def send_load_test_command(command_data, topic):
#     print(command_data,topic)
#     # producer.send(topic, key=None, value=command_data)
#     # producer.flush()
#     pass

# @app.route('/test_configure', methods=['GET'])
# def test_config():
#     global current_test_id
#     # Increment the test ID
#     current_test_id += 1
#     global final_test_id
#     final_test_id = f"tsunami_{current_test_id}"
#     # Get load test parameters from the request
#     test_params = json.dumps({"test_id": final_test_id, "test_type": "tsunami", "test_message_delay": 2})

#     # Send load test command to Driver Node via Kafka
#     send_load_test_command(test_params, load_test_commands_topic)

#     return jsonify({"message": "Test successfully started"})

# @app.route('/trigger_test', methods=['GET'])
# def trigger_init():
#     # pass
#     global final_test_id
#     if(final_test_id):
#         trigger_message = json.dumps({"test_id":final_test_id,"trigger":"YES"})
#     else:
#         raise("error")
#     send_load_test_command(trigger_message,topic_trigger_test_command)
#     return jsonify({"message": "Test ID reset"})

# if __name__ == '__main__':
#     app.run(port=5000,debug=True)

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests
import json


app = Flask(__name__)
CORS(app)

# Global variables for test ID and test configuration
current_test_id = 0
current_test_configuration = {}

# Kafka topic to send load test commands
load_test_commands_topic = 'test_config'
trigger_test_command_topic = 'trigger'

def send_load_test_command(command_data, topic):
    # Simulate sending load test command to Kafka
    print(f"Sending load test command: {command_data} to topic: {topic}")
    return

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_configure', methods=['POST'])
def configure_test():
    global current_test_id, current_test_configuration
    # Increment the test ID
    current_test_id += 1

    # Get load test parameters from the form
    test_type = request.form.get('test_type')
    test_message_delay = request.form.get('test_message_delay')

    # Save the current test configuration
    current_test_configuration = {
        "test_id": current_test_id,
        "test_type": test_type,
        "test_message_delay": test_message_delay
    }
    if current_test_configuration:
        send_load_test_command(json.dumps(current_test_configuration), load_test_commands_topic)

    return render_template('index.html', message=f"Test configured with ID: {current_test_id}")

@app.route('/trigger_test')
def trigger_test():
    global current_test_configuration
    if not current_test_configuration:
        return render_template('index.html', error="Test configuration is not set. Please configure a test first.")

    # Send load test command to Driver Node via Kafka
    send_load_test_command(json.dumps(current_test_configuration), trigger_test_command_topic)

    return render_template('index.html', message="Test triggered successfully")

if __name__ == '__main__':
    app.run(port=5000,debug=True)
