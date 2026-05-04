"""
Configuration loader for TransitGraph project.
Loads and validates configuration from config.yaml file.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class MQTTConfig:
    """MQTT connection configuration."""
    broker: str
    port: int
    topics: List[str]
    client_id: str
    keepalive: int
    qos: int


@dataclass
class KafkaConfig:
    """Kafka connection configuration."""
    bootstrap_servers: str
    topic: str


@dataclass
class Neo4jConfig:
    """Neo4j connection configuration."""
    uri: str
    user: str
    password: str
    database: str


@dataclass
class ProcessingConfig:
    """Stream processing configuration."""
    batch_size: int
    batch_timeout_ms: int
    co_location_distance_m: float
    co_location_time_window_s: int


class Config:
    """Main configuration class that loads and provides access to all config sections."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to config.yaml file. 
                        If None, uses config/config.yaml relative to project root.
        """
        if config_path is None:
            # Default to config/config.yaml relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self._raw_config = self._load_config()
        self._validate_config()
        
        # Load individual config sections
        self.mqtt = self._load_mqtt_config()
        self.kafka = self._load_kafka_config()
        self.neo4j = self._load_neo4j_config()
        self.processing = self._load_processing_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
    
    def _validate_config(self):
        """Validate that required configuration sections exist."""
        required_sections = ['mqtt', 'kafka']
        missing = [section for section in required_sections 
                  if section not in self._raw_config]
        
        if missing:
            raise ValueError(
                f"Missing required configuration sections: {', '.join(missing)}"
            )
    
    def _load_mqtt_config(self) -> MQTTConfig:
        """Load and validate MQTT configuration."""
        mqtt_raw = self._raw_config.get('mqtt', {})
        
        return MQTTConfig(
            broker=mqtt_raw.get('broker', 'mqtt.hsl.fi'),
            port=mqtt_raw.get('port', 1883),
            topics=mqtt_raw.get('topics', []),
            client_id=mqtt_raw.get('client_id', 'transitgraph_client'),
            keepalive=mqtt_raw.get('keepalive', 60),
            qos=mqtt_raw.get('qos', 1)
        )
    
    def _load_kafka_config(self) -> KafkaConfig:
        """Load and validate Kafka configuration."""
        kafka_raw = self._raw_config.get('kafka', {})
        
        return KafkaConfig(
            bootstrap_servers=kafka_raw.get('bootstrap_servers', 'localhost:9092'),
            topic=kafka_raw.get('topic', 'transit_positions')
        )
    
    def _load_neo4j_config(self) -> Neo4jConfig:
        """Load and validate Neo4j configuration."""
        neo4j_raw = self._raw_config.get('neo4j', {})
        
        return Neo4jConfig(
            uri=neo4j_raw.get('uri', 'bolt://localhost:7687'),
            user=neo4j_raw.get('user', 'neo4j'),
            password=neo4j_raw.get('password', 'password'),
            database=neo4j_raw.get('database', 'transitgraph')
        )
    
    def _load_processing_config(self) -> ProcessingConfig:
        """Load and validate processing configuration."""
        proc_raw = self._raw_config.get('processing', {})
        
        return ProcessingConfig(
            batch_size=proc_raw.get('batch_size', 100),
            batch_timeout_ms=proc_raw.get('batch_timeout_ms', 1000),
            co_location_distance_m=proc_raw.get('co_location_distance_m', 100.0),
            co_location_time_window_s=proc_raw.get('co_location_time_window_s', 60)
        )
    
    def __repr__(self):
        return f"Config(loaded from: {self.config_path})"


# Convenience function for easy access
def load_config(config_path: str = None) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file.
    
    Returns:
        Config object with all configuration sections.
    
    Example:
        >>> config = load_config()
        >>> print(config.mqtt.broker)
        >>> print(config.kafka.topic)
    """
    return Config(config_path)

