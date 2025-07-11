from sqlalchemy.orm import Session
from src.rest_models import (
    Item,
    ItemCreate,
    ItemUpdate,
    NotFoundError,
)
from src.db_models import (
    DBItem,
)

def db_find_item(item_id: int, db: Session) -> DBItem:
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise NotFoundError()
    return db_item


def db_create_item(item: ItemCreate, session: Session) -> Item:
    db_item = DBItem(**item.model_dump())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return Item(**db_item.__dict__)


def db_read_item(item_id: int, session: Session) -> Item:
    db_item = db_find_item(item_id, session)
    return Item(**db_item.__dict__)


def db_update_item(item_id: int, item: ItemUpdate, session: Session) -> Item:
    db_item = db_find_item(item_id, session)
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    session.commit()
    session.refresh(db_item)

    return Item(**db_item.__dict__)


def db_delete_item(item_id: int, session: Session) -> Item:
    db_item = db_find_item(item_id, session)
    session.delete(db_item)
    session.commit()
    return Item(**db_item.__dict__)