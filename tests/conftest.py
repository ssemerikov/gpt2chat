import pytest
import tempfile
import shutil
from pathlib import Path
from app import create_app
from services.storage_service import StorageService
from config import Config


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage_service(temp_data_dir):
    """Create a StorageService with temporary directory"""
    return StorageService(temp_data_dir)


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def test_config():
    """Create test configuration"""
    return Config
