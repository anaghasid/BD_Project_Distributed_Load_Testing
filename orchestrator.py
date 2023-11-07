from kafka import KafkaConsumer

def consume_messages(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='kafka:9093',  # Replace with your Kafka bootstrap servers
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    try:
        for message in consumer:
            print(f"Received message: {message.value}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if _name_ == "_main_":
    consume_messages('load_test_metrics')