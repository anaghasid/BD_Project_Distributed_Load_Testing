import threading
from kafka import KafkaConsumer, KafkaProducer
import time


producer_config = {
    'bootstrap_servers': 'your_kafka_broker(s)',
    # Other producer configuration options
}

producer = KafkaProducer(**producer_config)

heartbeat_message = "Heartbeat Message"
heartbeat_topic = "heartbeat_topic"
heartbeat_interval = 10

def send_heartbeat(producer, heartbeat_topic, heartbeat_message, heartbeat_interval)
    try:
        while True:
            producer.send(heartbeat_topic, value=heartbeat_message.encode('utf-8'))
            producer.flush()  # Ensure the message is sent immediately
            time.sleep(heartbeat_interval)
    except KeyboardInterrupt:
        pass

def consume_messages(consumer, topic_name):
    for message in consumer:
        print(f"Received message from {topic_name}: {message.value.decode('utf-8')}")


topic_config = 'test_config'
topic_trig = 'trigger'

# Create and start consumer threads
thread1 = threading.Thread(target=consume_messages, args=(topic_config, 'topic1'))
thread2 = threading.Thread(target=consume_messages, args=(topic_trig, 'topic2'))

# Start the threads
thread1.start()
thread2.start()

# Wait for the threads to finish
thread1.join()
thread2.join()
