from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
import pytest
from src.app import app
from src.db import get_db, get_db_builder, DBType
from src.models.db_models import Base, DBItem

# Setup the TestClient
client = TestClient(app)

# Uncomment to setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

# Uncomment to setup the NEON Postgres database for testing
# get_db_func, engine = get_db_builder(DBType.NEON)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup():
    setup_tables()
    yield
    teardown_tables()


def setup_tables():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    db_item = DBItem(id=100, name="Test Item", description="This is a test item")
    session.add(db_item)
    session.commit()
    session.close()


def teardown_tables():
    Base.metadata.drop_all(bind=engine)


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "API is running"


def test_create_item():
    response = client.post(
        "/items/", json={"name": "Test Item", "description": "This is a test item"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert "id" in data


def test_create_improper_item():
    response = client.post("/items/", json={"description": "This is a test item"})
    assert response.status_code == 422, response.text


def test_read_item():
    # Create an item
    response = client.post(
        "/items/", json={"name": "Test Item", "description": "This is a test item"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    item_id = data["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert data["id"] == item_id


def test_update_item():
    item_id = 100
    response = client.put(
        f"/items/{item_id}",
        json={"name": "Updated Item", "description": "This is an updated item"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated Item"
    assert data["description"] == "This is an updated item"
    assert data["id"] == item_id


def test_delete_item():
    item_id = 100
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == item_id
    # Try to get the deleted item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404, response.text
