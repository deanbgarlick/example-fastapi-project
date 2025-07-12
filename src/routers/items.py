from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.models.rest_models import (
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
from src.rate_limiter import rate_limiter

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.post("")
@with_default_logging
@rate_limiter.limit("10/second")
def create_item(request: Request, item: ItemCreate, db: Session = Depends(get_db)) -> Item:
    return db_create_item(item, db)

@router.get("/{item_id}")
@with_default_logging
@rate_limiter.limit("10/second")
def read_item(request: Request, item_id: int, db: Session = Depends(get_db)) -> Item:
    try:
        return db_read_item(item_id, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}")
@with_default_logging
@rate_limiter.limit("10/second")
def update_item(request: Request, item_id: int, item: ItemUpdate, db: Session = Depends(get_db)) -> Item:
    try:
        return db_update_item(item_id, item, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}")
@with_default_logging
@rate_limiter.limit("10/second")
def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)) -> Item:
    try:
        return db_delete_item(item_id, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found") 