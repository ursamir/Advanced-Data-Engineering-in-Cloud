import json
import random
import time
from datetime import datetime
from confluent_kafka import Producer

# Read Kafka broker address from kafka.json
with open('kafka.json', 'r') as f:
    data = f.read()
    bootstrap_servers = data.split('"kafkaBroker": "')[1].split('"')[0]

# Kafka producer configuration
producer = Producer({'bootstrap.servers': bootstrap_servers})

# Example data
vehicle_data = {
    "id": "1",
    "deviceId": "device_1",
    "timestamp": str(datetime.utcnow()),
    "location": "Location_1",
    "speed": random.uniform(0, 100),
    "length": random.uniform(2.5, 3.5),
    "elevation": random.uniform(0, 500),
    "make": "Brand_X",
    "model": "Model_Y",
    "year": 2022,
    "fuelType": "Petrol"
}

failures_data = {
    "id": "1",
    "deviceId": "device_1",
    "incidentId": "incident_1",
    "type": "type_1",
    "timestamp": str(datetime.utcnow()),
    "location": "Location_1",
    "description": "Description_1"
}

weather_data = {
    "temperature": random.uniform(-10, 40),
    "weatherCondition": "Clear",
    "windSpeed": random.uniform(0, 20),
    "humidity": random.randint(0, 100),
    "airQualityIndex": random.randint(0, 300),
    "timestamp": str(datetime.utcnow())
}

def produce_message(topic, message):
    producer.produce(topic, value=json.dumps(message).encode('utf-8'))
    producer.flush()

def main():
    while True:
        # Produce vehicle data
        vehicle_data["timestamp"] = str(datetime.utcnow())
        vehicle_data["speed"] = random.uniform(0, 100)
        vehicle_data["length"] = random.uniform(2.5, 3.5)
        vehicle_data["elevation"] = random.uniform(0, 500)
        produce_message('vehicle_data', vehicle_data)
        
        # Produce failures data
        failures_data["timestamp"] = str(datetime.utcnow())
        produce_message('failures_data', failures_data)
        
        # Produce weather data
        weather_data["timestamp"] = str(datetime.utcnow())
        weather_data["temperature"] = random.uniform(-10, 40)
        weather_data["windSpeed"] = random.uniform(0, 20)
        weather_data["humidity"] = random.randint(0, 100)
        weather_data["airQualityIndex"] = random.randint(0, 300)
        produce_message('weather_data', weather_data)
        
        # Wait for a few seconds before producing the next set of messages
        time.sleep(5)

if __name__ == "__main__":
    main()
