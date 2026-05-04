"""
Tests for config_loader module.
"""

import pytest
import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.config_loader import (
    Config,
    load_config,
    MQTTConfig,
    KafkaConfig,
    Neo4jConfig,
    ProcessingConfig
)


class TestConfigLoader:
    """Test suite for Config class."""
    
    def test_load_config_from_default_path(self):
        """Test loading config from default config/config.yaml path."""
        config = load_config()
        
        assert config is not None
        assert isinstance(config, Config)
        assert config.mqtt.broker == 'mqtt.hsl.fi'
        assert config.kafka.bootstrap_servers == 'localhost:9092'
    
    def test_load_config_from_custom_path(self, temp_config_file, sample_config_dict):
        """Test loading config from a custom file path."""
        with temp_config_file(sample_config_dict) as config_path:
            config = load_config(str(config_path))
            
            assert config.mqtt.broker == 'mqtt.hsl.fi'
            assert config.mqtt.port == 1883
            assert config.kafka.topic == 'test_topic'
    
    def test_config_file_not_found(self):
        """Test error handling when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config('/nonexistent/path/config.yaml')
    
    def test_invalid_yaml(self):
        """Test error handling for invalid YAML."""
        # Create a file with invalid YAML
        with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [unclosed')
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Error parsing YAML"):
                load_config(str(temp_path))
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_missing_required_section(self, temp_config_file):
        """Test error handling when required sections are missing."""
        incomplete_config = {
            'mqtt': {
                'broker': 'mqtt.hsl.fi',
                'port': 1883
            }
            # Missing 'kafka' section
        }
        
        with temp_config_file(incomplete_config) as config_path:
            with pytest.raises(ValueError, match="Missing required configuration sections"):
                load_config(str(config_path))
    
    def test_mqtt_config_loading(self, temp_config_file, sample_config_dict):
        """Test MQTT configuration is loaded correctly."""
        with temp_config_file(sample_config_dict) as config_path:
            config = load_config(str(config_path))
            
            assert isinstance(config.mqtt, MQTTConfig)
            assert config.mqtt.broker == 'mqtt.hsl.fi'
            assert config.mqtt.port == 1883
            assert config.mqtt.topics == ['/hfp/v2/journey/ongoing/vp/metro/#']
            assert config.mqtt.client_id == 'test_client'
            assert config.mqtt.keepalive == 60
            assert config.mqtt.qos == 1
    
    def test_kafka_config_loading(self, temp_config_file, sample_config_dict):
        """Test Kafka configuration is loaded correctly."""
        with temp_config_file(sample_config_dict) as config_path:
            config = load_config(str(config_path))
            
            assert isinstance(config.kafka, KafkaConfig)
            assert config.kafka.bootstrap_servers == 'localhost:9092'
            assert config.kafka.topic == 'test_topic'
    
    def test_neo4j_config_loading(self, temp_config_file, sample_config_dict):
        """Test Neo4j configuration is loaded correctly."""
        with temp_config_file(sample_config_dict) as config_path:
            config = load_config(str(config_path))
            
            assert isinstance(config.neo4j, Neo4jConfig)
            assert config.neo4j.uri == 'bolt://localhost:7687'
            assert config.neo4j.user == 'neo4j'
            assert config.neo4j.password == 'test_password'
            assert config.neo4j.database == 'test_db'
    
    def test_processing_config_loading(self, temp_config_file, sample_config_dict):
        """Test processing configuration is loaded correctly."""
        with temp_config_file(sample_config_dict) as config_path:
            config = load_config(str(config_path))
            
            assert isinstance(config.processing, ProcessingConfig)
            assert config.processing.batch_size == 100
            assert config.processing.batch_timeout_ms == 1000
            assert config.processing.co_location_distance_m == 100.0
            assert config.processing.co_location_time_window_s == 60
    
    def test_default_values(self, temp_config_file, minimal_config_dict):
        """Test that default values are used when optional fields are missing."""
        with temp_config_file(minimal_config_dict) as config_path:
            config = load_config(str(config_path))
            
            # Neo4j should have defaults
            assert config.neo4j.uri == 'bolt://localhost:7687'
            assert config.neo4j.user == 'neo4j'
            assert config.neo4j.password == 'password'
            assert config.neo4j.database == 'transitgraph'
            
            # Processing should have defaults
            assert config.processing.batch_size == 100
            assert config.processing.batch_timeout_ms == 1000
    
    def test_multiple_mqtt_topics(self, temp_config_file):
        """Test loading multiple MQTT topics."""
        config_dict = {
            'mqtt': {
                'broker': 'mqtt.hsl.fi',
                'port': 1883,
                'topics': [
                    '/hfp/v2/journey/ongoing/vp/metro/#',
                    '/hfp/v2/journey/ongoing/vp/bus/#'
                ],
                'client_id': 'test_client',
                'keepalive': 60,
                'qos': 1
            },
            'kafka': {
                'bootstrap_servers': 'localhost:9092',
                'topic': 'test_topic'
            }
        }
        
        with temp_config_file(config_dict) as config_path:
            config = load_config(str(config_path))
            
            assert len(config.mqtt.topics) == 2
            assert '/hfp/v2/journey/ongoing/vp/metro/#' in config.mqtt.topics
            assert '/hfp/v2/journey/ongoing/vp/bus/#' in config.mqtt.topics
    
    def test_config_repr(self, temp_config_file, sample_config_dict):
        """Test Config string representation."""
        with temp_config_file(sample_config_dict) as config_path:
            config = load_config(str(config_path))
            
            repr_str = repr(config)
            assert 'Config' in repr_str
            assert str(config_path) in repr_str or 'config' in repr_str.lower()


class TestConfigDataclasses:
    """Test suite for config dataclasses."""
    
    def test_mqtt_config_creation(self):
        """Test MQTTConfig dataclass creation."""
        mqtt_config = MQTTConfig(
            broker='test.broker.com',
            port=1883,
            topics=['/test/topic'],
            client_id='test_client',
            keepalive=60,
            qos=1
        )
        
        assert mqtt_config.broker == 'test.broker.com'
        assert mqtt_config.port == 1883
        assert mqtt_config.topics == ['/test/topic']
    
    def test_kafka_config_creation(self):
        """Test KafkaConfig dataclass creation."""
        kafka_config = KafkaConfig(
            bootstrap_servers='localhost:9092',
            topic='test_topic'
        )
        
        assert kafka_config.bootstrap_servers == 'localhost:9092'
        assert kafka_config.topic == 'test_topic'
    
    def test_neo4j_config_creation(self):
        """Test Neo4jConfig dataclass creation."""
        neo4j_config = Neo4jConfig(
            uri='bolt://localhost:7687',
            user='neo4j',
            password='test_pass',
            database='test_db'
        )
        
        assert neo4j_config.uri == 'bolt://localhost:7687'
        assert neo4j_config.user == 'neo4j'
        assert neo4j_config.password == 'test_pass'
        assert neo4j_config.database == 'test_db'
    
    def test_processing_config_creation(self):
        """Test ProcessingConfig dataclass creation."""
        proc_config = ProcessingConfig(
            batch_size=50,
            batch_timeout_ms=500,
            co_location_distance_m=200.0,
            co_location_time_window_s=120
        )
        
        assert proc_config.batch_size == 50
        assert proc_config.batch_timeout_ms == 500
        assert proc_config.co_location_distance_m == 200.0
        assert proc_config.co_location_time_window_s == 120

