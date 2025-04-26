from kafka import KafkaConsumer
from report_pb2 import Report

# Kafka configuration
broker = "localhost:9092"
topic_name = "temperatures"
group_id = "debug"

# Initialize consumer
consumer = KafkaConsumer(topic_name, 
                         group_id=group_id, 
                         bootstrap_servers=[broker])

# Create protobuf message object for reuse
report = Report()

# Main processing loop
while True:
    # Poll for messages
    batch = consumer.poll(1000)
    
    # Process each partition and message
    for partition, messages in batch.items():
        for message in messages:
            # Parse protobuf message
            report.ParseFromString(message.value)
            
            # Print message information
            print({
                'station_id': report.station_id,
                'date': report.date,
                'degrees': report.degrees,
                'partition': message.partition
            })
