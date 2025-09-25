import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from api.main_api import app
from core.db.database import Base, engine, get_db

# Create a TestClient instance
client = TestClient(app)

# Use a separate database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup and teardown the database for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def authenticated_client():
    """A TestClient instance with a logged-in user."""
    register_data = {"username": "testuser_auth", "password": "password123"}
    response = client.post("/api/v1/auth/register", json=register_data)
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app, headers=headers)