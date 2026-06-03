"""Item CRUD endpoints."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.item import ItemCreate, ItemRead, ItemUpdate
from services.item_service import ItemService

router = APIRouter()


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> ItemRead:
    """Create a new item."""
    return ItemService.create(db=db, payload=payload)


@router.get("/", response_model=List[ItemRead])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[ItemRead]:
    """List items with pagination."""
    return ItemService.list(db=db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: UUID, db: Session = Depends(get_db)) -> ItemRead:
    """Fetch a single item by id."""
    item = ItemService.get(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: UUID, payload: ItemUpdate, db: Session = Depends(get_db)) -> ItemRead:
    """Update an existing item."""
    item = ItemService.update(db=db, item_id=item_id, payload=payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: UUID, db: Session = Depends(get_db)) -> None:
    """Delete an item."""
    deleted = ItemService.delete(db=db, item_id=item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
