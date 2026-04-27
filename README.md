# 🌩️ Event-Driven Weather Pipeline

[![Kafka](https://img.shields.io/badge/Streaming-Apache%20Kafka-231F20.svg?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Protobuf](https://img.shields.io/badge/Networking-Protobuf-044F88.svg?logo=google&logoColor=white)](https://protobuf.dev/)
[![MySQL](https://img.shields.io/badge/Sink-MySQL-4479A1.svg?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![HDFS](https://img.shields.io/badge/Sink-HDFS-FFCC01.svg?logo=apache&logoColor=black)](https://hadoop.apache.org/)
[![Python](https://img.shields.io/badge/Language-Python%203.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)

> A highly resilient, distributed streaming architecture simulating real-time ingest and automated consumption of climate telemetry. Leverages Apache Kafka as the backbone message broker paired with persistent relational and analytic storage systems to achieve massive parallel stream processing.

## 📖 Overview

Modern data platforms rely on event-driven streaming to decouple data producers (like IoT weather sensors) from slow, restrictive consumer databases. Passing events through a distributed message log ensures that immense traffic spikes never overload downstream systems.

This project mocks a real-time climate telemetry network. A python daemon continuously generates chaotic atmospheric data, which is immediately serialized as Protocol Buffers and shot into an Apache Kafka topic. Concurrent backend consumers subscribe to these topic streams, decrypt the payload, and securely drain the data into localized HDFS instances and MySQL analytics nodes concurrently.

## ✨ Key Features

- **Decoupled Architecture**: Producers have zero visibility into consumers. If the MySQL database crashes, Kafka buffers the inbound weather records perfectly until the database restarts.
- **Optimized Binary Serialization:** Sensor strings take immense amounts of network overhead. By enforcing `report.proto`, raw sensor logs are compressed into pure binaries before hitting Kafka, improving throughput geometrically.
- **Multiple Data Sinks:** Consumers are programmed to filter metrics. Massive blob data is piped sequentially to Hadoop nodes, while highly specific alerts are mirrored into strict relational SQL schemas.
- **Broker Resiliency**: Leveraging Zookeeper and Kafka containers guarantees exact-once or at-least-once delivery mechanisms avoiding data duplication during network stutters.

## 🏗️ Technical Architecture

1. **Weather Generator (`weather_generator.py`)**: A localized telemetry mocking daemon triggering random climate phenomena.
2. **Kafka Producer (`producer.py`)**: Subscribes to the mockup daemon, serializes events cleanly into `protobufs`, and routes them onto a dedicated Kafka partitioning scheme.
3. **Kafka Consumer (`consumer.py`)**: The dedicated backend process listening continuously to the partitions, expanding the binaries, and committing the final records to persistent sinks.
4. **Broker Grid (`Dockerfile.kafka`)**: Defines the streaming node requirements, mapped with HDFS and SQL in the master docker network file.

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose**
- `pip install kafka-python protobuf`

### Execution

1. **Launch Enterprise Subnets**
   Initiate the DataNode, NameNode, MySQL sink, and Kafka Zookeeper ring:
   ```bash
   docker-compose up -d
   ```

2. **Commence Telemetry Mock**
   In terminal *A*, begin generating records and pipe them dynamically into the active Producer module:
   ```bash
   cd src/
   python weather_generator.py | python producer.py
   ```

3. **Activate Pipeline Consumers**
   In terminal *B*, execute the listener which will actively begin draining Kafka into the databases:
   ```bash
   cd src/
   python consumer.py
   ```

## 📂 Project Structure

```text
.
├── Dockerfile.datanode       # Hadoop storage worker layer
├── Dockerfile.namenode       # Hadoop storage index layer
├── Dockerfile.kafka          # Broker streaming node layer
├── Dockerfile.mysql          # Relational sink database layer
├── docker-compose.yml        # Inter-service DNS coordination
├── src/                      #
│   ├── weather_generator.py  # IoT mockup script
│   ├── producer.py           # Ingest router to Kafka
│   ├── consumer.py           # Stream drainer to Data Sinks
│   ├── report.proto          # Payload compression definition
│   └── requirements.txt      #
└── README.md
```
