from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.rest_models import (
    Item,
    ItemCreate, 
    ItemUpdate,
    NotFoundError,
)
from src.operations import (
    db_create_item,
    db_delete_item,
    db_read_item,
    db_update_item,
)
from src.db import get_db
from src.logging import with_default_logging

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.post("")
@with_default_logging
def create_item(item: ItemCreate, db: Session = Depends(get_db)) -> Item:
    return db_create_item(item, db)

@router.get("/{item_id}")
@with_default_logging
def read_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    try:
        return db_read_item(item_id, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}")
@with_default_logging
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)) -> Item:
    try:
        return db_update_item(item_id, item, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}")
@with_default_logging
def delete_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    try:
        return db_delete_item(item_id, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found") 