# TransitGraph: Real-Time Transit Relationship Graph

A real-time distributed graph system inspired by Netflix's architecture, ingesting live vehicle position data from Digitransit's MQTT stream.

## Project Goals

- **Ingest** live vehicle position data from Digitransit MQTT feed
- **Build** dynamic relationships:
  - Vehicle ↔ Route ↔ Stop ↔ Time Window
  - Co-located vehicles (same area within 1 min)
- **Support** real-time queries:
  - "Which buses are near Helsinki Central now?"
  - "Which vehicles are following similar routes?"
  - "Which routes have delays or anomalies?"

## Architecture

```
┌──────────────────────┐
│ Digitransit MQTT Feed│
└──────────┬───────────┘
           │
    (stream ingestion)
           ▼
┌──────────────────────┐
│ Kafka (Event Broker) │  ← durable queue
└──────────┬───────────┘
           │
    (stream processing)
           ▼
┌──────────────────────┐
│ Flink / Spark Stream │
│ - parse JSON payload │
│ - enrich / dedup     │
│ - compute relations  │
└──────────┬───────────┘
           │
     (graph storage)
           ▼
┌──────────────────────┐
│ Neo4j / Memgraph /   │
│  TigerGraph          │
└──────────────────────┘
```

## Project Structure

```
travel_graph/
├── src/
│   ├── ingestion/      # MQTT stream ingestion
│   ├── processing/     # Stream processing logic
│   ├── storage/        # Graph database operations
│   └── api/            # Query API
├── config/             # Configuration files
├── tests/              # Unit and integration tests
└── notebooks/          # Exploratory analysis
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the MQTT ingestion client:
```bash
python src/ingestion/mqtt_client.py
```

## Data Source

Using [Digitransit MQTT API](https://digitransit.fi/en/developers/apis/5-realtime-api/vehicle-positions/digitransit-mqtt/) for real-time vehicle positions.

## Tech Stack

- **Ingestion**: Paho MQTT, Python
- **Message Queue**: Apache Kafka
- **Stream Processing**: Apache Flink / Spark Streaming
- **Graph Database**: Neo4j / Memgraph
- **API**: FastAPI


