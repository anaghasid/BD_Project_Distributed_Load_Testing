from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

request_count = 0
response_count = 0

@app.route('/test_endpoint/<id>', methods=['GET'])
def test_endpoint(id):
    print(id)
    global request_count, response_count
    request_count += 1
    # Simulate some processing
    response_time = random.uniform(0.1, 0.5)
    response = {
        "message": "Test response",
        "mes_id":int(id),
        "response_time": response_time
    }
    time.sleep(2)
    response_count += 1
    return jsonify(response)

@app.route('/metrics', methods=['GET'])
def metrics():
    global request_count, response_count

    metrics_data = {
        "requests_sent": request_count,
        "responses_sent": response_count
    }
    
    return jsonify(metrics_data)

if __name__ == '__main__':
    app.run(port=8000,debug=True)
