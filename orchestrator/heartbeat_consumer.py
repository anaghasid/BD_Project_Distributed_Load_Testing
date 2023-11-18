from kafka import KafkaConsumer
import json 
import time

heartbeat_consumer_conf = {'bootstrap_servers': 'bd_project_distributed_load_testing-kafka_node-1:9092'}
heartbeat_topic = 'heartbeat'

def get_heartbeat_consumer():
    return KafkaConsumer(heartbeat_topic,**heartbeat_consumer_conf)

def get_heartbeats(server_heartbeats,socketio):
    count=0
    try:
        heartbeat_consumer=get_heartbeat_consumer()
        for message in heartbeat_consumer:
            msg=message.value.decode('utf-8')
            # if msg is None:
            #     continue
            # if msg.error():
            #     break
            # Update server heartbeat in the list
            if(count<50): 
                print("received heartbeat")
                count+=1
            json_beat = json.loads(msg)
            server_heartbeats[json_beat.get("node_id")] = time.time()
            socketio.emit('update_server_heartbeats', server_heartbeats, namespace='/')

    except KeyboardInterrupt:
        pass
    finally:
        heartbeat_consumer.close()

def initialize_heartbeat_consumer(server_heartbeats,socketio):
    get_heartbeats(server_heartbeats,socketio)