import os, sys
from kafka import KafkaConsumer, TopicPartition
from subprocess import check_output
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import pyarrow.fs as pafs
from report_pb2 import Report
import json

# Set up HDFS CLASSPATH
os.environ["CLASSPATH"] = str(check_output([os.environ["HADOOP_HOME"]+"/bin/hdfs", "classpath", "--glob"]), "utf-8")

# Configuration
broker = 'localhost:9092'
topic_name = 'temperatures'
hdfs_host = "boss"
hdfs_port = 9000

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python consumer.py <partition_number>")
        sys.exit(1)
    
    partition_id = int(sys.argv[1])
    checkpoint_file = f"../partition-{partition_id}.json"
    
    # Set up consumer with manual partition assignment
    consumer = KafkaConsumer(group_id="debug", bootstrap_servers=[broker])
    consumer.assign([TopicPartition(topic_name, partition_id)])
    
    # Load checkpoint if it exists
    if os.path.exists(checkpoint_file):
        print(consumer.assignment, flush=True)
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
            consumer.seek(data['offset'])
    
    # Set up HDFS connection
    hdfs = pafs.HadoopFileSystem(hdfs_host, hdfs_port)
    
    # Initialize batch number and protobuf message
    batch_no = 0
    report = Report()
    
    # Main processing loop
    while True:
        # Poll for messages
        batch = consumer.poll(1000)
        records = []
        checkpoint_data = []
        
        # Process messages
        for t_partition, messages in batch.items():
            for msg in messages:
                # Parse protobuf message
                report.ParseFromString(msg.value)
                
                # Add record to dataset
                record = {
                    'station_id': report.station_id,
                    'date': report.date,
                    'degrees': report.degrees
                }
                records.append(record)
                
                # Track offset for checkpoint
                checkpoint = {
                    "batch_id": batch_no,
                    "offset": msg.offset
                }
                checkpoint_data.append(checkpoint)
        
        # Write to HDFS if we have records
        if records:
            # Create Parquet table
            table = pa.Table.from_pandas(pd.DataFrame(records))
            
            # Path for Parquet file
            parquet_file = f"partition-{partition_id}-batch-{batch_no}.parquet"
            hdfs_path = f"hdfs://{hdfs_host}:{hdfs_port}/data/{parquet_file}"
            
            # Write to HDFS
            with hdfs.open_output_stream(hdfs_path) as f:
                pq.write_table(table, f)
            
            # Save checkpoint
            with open(checkpoint_file, "w") as f:
                if checkpoint_data:
                    # Save the last checkpoint in the batch
                    json.dump(checkpoint_data[-1], f)
            
            # Increment batch counter
            batch_no += 1

if __name__ == '__main__':
    main()
