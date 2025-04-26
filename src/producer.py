from kafka import KafkaAdminClient, KafkaProducer, KafkaConsumer
from kafka.admin import NewTopic
from sqlalchemy import create_engine, text
import time
import pandas as pd
from report_pb2 import Report

# Kafka configuration
broker = "localhost:9092"
admin = KafkaAdminClient(bootstrap_servers=[broker])
admin.list_topics()

# Delete existing topic if it exists
try:
    admin.delete_topics(["temperatures"])
    time.sleep(3)
except:
    pass

# Create new topic with 4 partitions
admin.create_topics([NewTopic("temperatures", replication_factor=1, num_partitions=4)])

# Database connection
engine = create_engine("mysql+mysqlconnector://root:abc@mysql:3306/CS544")
conn = engine.connect()

# Initialize producer
producer = KafkaProducer(bootstrap_servers=[broker], acks="all", retries=10)

# Track the highest ID we've processed
last_id = 0
while True:
    # Query for new records
    query = text(f"""SELECT * FROM temperatures WHERE id > :id""")
    result = conn.execute(query, {"id": last_id})
    records = result.fetchall()
    conn.commit()
    
    # Update the last ID if we have records
    if len(records) > 0:
        last_id = records[-1][0]
    
    # Process and send each record
    for row in records:
        date = str(row[2])
        degrees = row[3]
        station_id = row[1]
        
        # Create and serialize message
        value = Report(date=date, degrees=degrees, station_id=station_id).SerializeToString()
        producer.send("temperatures", value=value, key=station_id.encode('utf-8'))
    
    # Small delay to prevent high CPU usage
    if len(records) == 0:
        time.sleep(0.1)
