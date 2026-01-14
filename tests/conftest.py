"""
Pytest configuration and shared fixtures.
"""

import pytest
import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile
from contextlib import contextmanager


@contextmanager
def _temp_config_file_helper(config_dict: dict):
    """Helper function to create a temporary YAML config file."""
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_dict, f)
        temp_path = Path(f.name)
    
    try:
        yield temp_path
    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    return _temp_config_file_helper


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary for testing."""
    return {
        'mqtt': {
            'broker': 'mqtt.hsl.fi',
            'port': 1883,
            'topics': ['/hfp/v2/journey/ongoing/vp/metro/#'],
            'client_id': 'test_client',
            'keepalive': 60,
            'qos': 1
        },
        'kafka': {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'test_topic'
        },
        'neo4j': {
            'uri': 'bolt://localhost:7687',
            'user': 'neo4j',
            'password': 'test_password',
            'database': 'test_db'
        },
        'processing': {
            'batch_size': 100,
            'batch_timeout_ms': 1000,
            'co_location_distance_m': 100.0,
            'co_location_time_window_s': 60
        }
    }


@pytest.fixture
def minimal_config_dict():
    """Minimal configuration with only required sections."""
    return {
        'mqtt': {
            'broker': 'mqtt.hsl.fi',
            'port': 1883,
            'topics': ['/test/topic'],
            'client_id': 'test_client',
            'keepalive': 60,
            'qos': 1
        },
        'kafka': {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'test_topic'
        }
    }

