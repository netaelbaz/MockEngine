"""Pytest configuration and fixtures for MockEngine backend tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import Base, get_db
from src import models, crud
from src.utils.api_key_generator import generate_api_key, hash_api_key


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test function.

    Yields a database session and cleans up after the test.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with a database session override.

    Overrides the get_db dependency to use the test database.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_api_key(db):
    """
    Create a sample API key for testing.

    Returns the API key object and the plain key string.
    """
    plain_key = generate_api_key()
    hashed_key = hash_api_key(plain_key)

    db_key = crud.create_api_key(
        db=db,
        key_name="Test API Key",
        api_key=hashed_key
    )

    return db_key, plain_key


@pytest.fixture
def sample_rule(db):
    """
    Create a sample rule for testing.
    """
    from src.schemas import RuleCreate

    rule_data = RuleCreate(
        name="Test Rule",
        url_pattern="/api/test",
        status_code=200,
        delay_ms=0,
        mode="always",
        mock_data={"message": "Test response"}
    )

    return crud.create_rule(db, rule_data)


@pytest.fixture
def sample_device(db, sample_api_key):
    """
    Create a sample device for testing.
    """
    api_key_obj, _ = sample_api_key

    device = crud.register_device(
        db=db,
        device_id="test_device_123",
        api_key_id=api_key_obj.id,
        app_version="1.0.0",
        android_version="10",
        internet_mode="wifi"
    )

    return device
