# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Data Extraction Demo

This will connect to the Digitransit MQTT feed and collect real-time vehicle positions for 30 seconds:

```bash
python demo_extract_data.py
```

You should see:
- Live connection to the MQTT broker
- Real-time data collection progress
- Statistics about collected vehicles, routes, and relationships
- Saved JSON files in the `data/` directory

### Step 3: View Live Feed (Optional)

To see a live updating table of vehicle positions:

```bash
python src/ingestion/mqtt_client.py
```

Press `Ctrl+C` to stop.

## 📊 Understanding the Data

### MQTT Topic Format

```
/hfp/v2/journey/ongoing/vp/{mode}/{oper_id}/{vehicle_number}/{route_id}/{direction_id}/{headsign}/{start_time}/{next_stop}/{geohash_level}/{geohash}/{sid}
```

Example:
```
/hfp/v2/journey/ongoing/vp/bus/0012/00123/2550/1/Kamppi/1430/1250101/4/u75h/1234567
```

### Message Payload Structure

```json
{
  "VP": {
    "veh": "123",           // Vehicle ID
    "lat": 60.1699,         // Latitude
    "long": 24.9384,        // Longitude
    "hdg": 180,             // Heading (degrees)
    "spd": 35.5,            // Speed (km/h)
    "tst": 1609502400,      // Timestamp (Unix)
    "route": "2550",        // Route ID
    "dir": 1,               // Direction (1 or 2)
    "stop": "1250101",      // Next stop ID
    "geohash": "u75h"       // Geohash
  }
}
```

## 🎯 What You've Built So Far

✅ **MQTT Stream Ingestion**
- Real-time connection to Digitransit feed
- Message parsing and structured data extraction
- Live display with rich formatting

✅ **Data Extraction**
- Vehicle position tracking
- Route and vehicle identification
- Relationship computation (co-located vehicles, same routes)
- JSON export for analysis

## 🔜 Next Steps

### Phase 1: Enhanced Ingestion (Current)
- [x] MQTT client
- [x] Data extraction
- [ ] Error handling and reconnection logic
- [ ] Message buffering

### Phase 2: Event Streaming
- [ ] Set up Kafka locally
- [ ] Publish MQTT messages to Kafka topics
- [ ] Consumer for data validation

### Phase 3: Stream Processing
- [ ] Set up Apache Flink or Spark Streaming
- [ ] Windowed aggregations
- [ ] Real-time relationship detection
- [ ] Anomaly detection

### Phase 4: Graph Storage
- [ ] Set up Neo4j
- [ ] Design graph schema (Vehicle, Route, Stop nodes)
- [ ] Batch insert pipeline
- [ ] Real-time graph updates

### Phase 5: Query API
- [ ] FastAPI endpoints
- [ ] Cypher query wrappers
- [ ] WebSocket for live updates

## 📁 Project Structure

```
travel_graph/
├── src/
│   ├── ingestion/
│   │   ├── mqtt_client.py      # MQTT subscriber
│   │   └── data_extractor.py   # Data parsing & relationships
│   ├── processing/             # [TODO] Stream processing
│   ├── storage/                # [TODO] Graph DB operations
│   └── api/                    # [TODO] Query API
├── config/
│   └── config.yaml             # Configuration
├── data/                       # Collected data (gitignored)
├── demo_extract_data.py        # Demo script
└── requirements.txt            # Dependencies
```

## 🛠 Troubleshooting

### Connection Issues

If you can't connect to the MQTT broker:
1. Check your internet connection
2. Verify the broker is accessible: `mqtt.hsl.fi` on port `1883`
3. Try increasing the keepalive timeout in `config/config.yaml`

### No Data Received

If connected but no messages:
1. The subscription topic might be too specific
2. There may be no active vehicles (check time of day in Helsinki)
3. Try subscribing to `#` (all topics) temporarily for debugging

### Performance Issues

If the script is slow:
1. Reduce the collection duration
2. Limit the number of topics subscribed
3. Disable live display mode

## 💡 Tips

1. **Best Times to Collect Data**: Weekdays during 7-9 AM or 4-6 PM (Helsinki time) for maximum vehicle activity

2. **Data Volume**: You can expect ~100-1000 messages per second during peak hours

3. **Geographic Focus**: Digitransit covers Helsinki, Turku, and other Finnish cities

4. **Vehicle Types**: Look for modes: `bus`, `tram`, `train`, `metro`, `ferry`

## 📚 Resources

- [Digitransit MQTT API](https://digitransit.fi/en/developers/apis/5-realtime-api/vehicle-positions/digitransit-mqtt/)
- [Netflix Graph Blog Post](https://netflixtechblog.com/how-netflix-content-engineering-makes-a-federated-graph-searchable-5c0c1c7d7eaf)
- [Apache Kafka](https://kafka.apache.org/)
- [Apache Flink](https://flink.apache.org/)
- [Neo4j Graph Database](https://neo4j.com/)




