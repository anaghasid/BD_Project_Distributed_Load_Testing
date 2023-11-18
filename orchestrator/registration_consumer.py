from kafka import KafkaConsumer
import json

consumer_conf = {'bootstrap_servers': 'bd_project_distributed_load_testing-kafka_node-1:9092'}
register_topic = 'register'


def get_registration_consumer():
    return KafkaConsumer(register_topic,**consumer_conf)

def get_node_info(registration_information):
    # registration_information=[]
    try:
        registration_consumer=get_registration_consumer()
        driver_count=3
        for message in registration_consumer:
            driver_count-=1
            msg=message.value.decode("utf-8")
            print(f"message received {msg}")
            registration_information.append(json.loads(msg))
            if(driver_count<=0):
                break 
    except Exception as e:
        print("Couldnt connect to kafka")
    finally:
        if registration_consumer:
            registration_consumer.close()

def initialize_registration_consumer(driver_information):
    get_node_info(driver_information)

