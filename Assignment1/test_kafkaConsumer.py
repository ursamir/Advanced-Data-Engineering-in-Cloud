# test_kafkaConsumer.py

from confluent_kafka import Consumer, KafkaException
import sys

# read the Kafka broker address from the environment.json file
with open('environment.json', 'r') as f:
    data = f.read()
    bootstrap_servers = data.split('"kafkaBroker": "')[1].split('"')[0]

group_id = 'test-consumer-group'  # Consumer group id

def consume_messages(topic):
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)

    try:
        consumer.subscribe([topic])

        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            print(f"Received message: {msg.value().decode('utf-8')}")

    except KeyboardInterrupt:
        sys.stderr.write('Aborted by user\n')

    finally:
        consumer.close()

if __name__ == '__main__':
    topic = 'test-topic'  # Replace with your Kafka topic name
    consume_messages(topic)
