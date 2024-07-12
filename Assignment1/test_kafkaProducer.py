# test_kafkaProducer.py
from confluent_kafka import Producer

# read the Kafka broker address from the environment.json file
with open('environment.json', 'r') as f:
    data = f.read()
    bootstrap_servers = data.split('"kafkaBroker": "')[1].split('"')[0]

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_messages(topic, messages):
    producer = Producer({'bootstrap.servers': bootstrap_servers})

    for message in messages:
        producer.produce(topic, message.encode('utf-8'), callback=delivery_report)

    producer.flush()
    # producer.close()

if __name__ == '__main__':
    topic = 'test-topic'  # Replace with your Kafka topic name
    messages = [
        'Message 1',
        'Message 2',
        'Message 3'
    ]

    produce_messages(topic, messages)
