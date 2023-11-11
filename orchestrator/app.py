from flask import Flask, render_template
from kafka import KafkaConsumer
import json,time

app = Flask(__name__)

driver_information = []
def get_driver_info():
    time.sleep(10)
    def get_registration_consumer():
        return KafkaConsumer("register", bootstrap_servers="bd_project_distributed_load_testing-kafka_node-1:9092")

    registration_consumer = get_registration_consumer()
    try:
        driver_count=3
        for message in registration_consumer:
            print("Received a message")
            driver = json.loads(message.value.decode("utf-8"))
            driver_information.append(driver)
            driver_count-=1
            if(driver_count<=0): break 
        registration_consumer.close()
    except Exception as e:
        print(f"Error processing registration_consumers: {str(e)}")
    print(driver_information)


get_driver_info()

@app.route("/")
def get_registration_info():
    return render_template("driver_info.html", driver_info_list=driver_information)

if __name__ == "__main__":
    app.run(debug=True)
