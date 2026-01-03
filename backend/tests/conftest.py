"""Pytest configuration and fixtures"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.database import Base, get_db
import app.database as database_module
import app.config as config_module


# Test database URL (local file)
TEST_DATABASE_URL = "sqlite:///./test_home_finance.db"


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function"""
    # Clean up any existing test database
    if os.path.exists("./test_home_finance.db"):
        os.remove("./test_home_finance.db")
    
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        # Clean up test database file
        if os.path.exists("./test_home_finance.db"):
            os.remove("./test_home_finance.db")


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database"""
    # Create a test engine
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Mock the init_db function to do nothing (tables are already created)
    def mock_init_db():
        pass
    
    # Patch the settings and database module before creating the TestClient
    with patch.object(config_module.settings, 'database_url', TEST_DATABASE_URL):
        with patch('app.main.init_db', side_effect=mock_init_db):
            with patch.object(database_module, 'engine', test_engine):
                with patch.object(database_module, 'SessionLocal', TestingSessionLocal):
                    # Create TestClient - this will trigger app startup
                    with TestClient(app) as test_client:
                        yield test_client
    
    app.dependency_overrides.clear()
