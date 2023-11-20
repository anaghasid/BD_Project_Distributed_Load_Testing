from kafka import KafkaConsumer
import json

consumer_conf = {'bootstrap_servers': 'bd_project_distributed_load_testing-kafka_node-1:9092'}
register_topic = 'register'


def get_registration_consumer():
    return KafkaConsumer(register_topic,**consumer_conf)

def get_node_info(registration_information,socketio):
    # registration_information=[]
    try:
        registration_consumer=get_registration_consumer()
        for message in registration_consumer:
            msg=json.loads(message.value.decode("utf-8"))
            print(f"message received {msg}")
            registration_information[msg['node_ID']]=msg['node_IP']
            socketio.emit('register_driver', msg, namespace='/')

    except Exception as e:
        print("Couldnt connect to kafka",e)
    finally:
        if registration_consumer:
            registration_consumer.close()

def initialize_registration_consumer(driver_information,socketio):
    get_node_info(driver_information,socketio)

