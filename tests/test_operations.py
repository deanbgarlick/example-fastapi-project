import pytest
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db_models import Base
from src.db_models import DBItem
from src.rest_models import ItemCreate, ItemUpdate
from src.operations import db_create_item, db_delete_item, db_read_item, db_update_item

# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()

    # create test items
    db_item = DBItem(id=100, name="Test Item", description="This is a test item")
    db_session.add(db_item)
    db_session.commit()

    yield db_session

    # Close the database and drop the tables in the test database
    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_item(session: Session) -> None:
    item = db_create_item(
        ItemCreate(name="Test Item", description="This is a test item"), session
    )
    assert item.name == "Test Item"
    assert item.description == "This is a test item"


def test_update_item(session: Session) -> None:
    # Create an item
    item = db_create_item(
        ItemCreate(name="Test Item", description="This is a test item"), session
    )
    item_id = item.id

    item = db_update_item(
        item_id, ItemUpdate(name="New Name", description=None), session
    )
    assert item.name == "New Name"


def test_delete_item(session: Session) -> None:
    # Create an item
    item = db_create_item(
        ItemCreate(name="Test Item", description="This is a test item"), session
    )
    item_id = item.id

    item = db_delete_item(item_id, session)
    assert item.name == "Test Item"
    assert item.id == item_id
    # Try to get the deleted item
    with pytest.raises(Exception):
        db_read_item(item_id, session)
