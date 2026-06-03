"""Item business logic layer."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from api.schemas.item import ItemCreate, ItemUpdate
from models.item import Item


class ItemService:
    """Encapsulates item-related business rules and persistence."""

    @staticmethod
    def create(db: Session, payload: ItemCreate) -> Item:
        item = Item(name=payload.name, description=payload.description)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get(db: Session, item_id: UUID) -> Optional[Item]:
        return db.query(Item).filter(Item.id == item_id).one_or_none()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
        if skip < 0:
            raise ValueError("skip must be >= 0")
        if limit <= 0 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        return db.query(Item).order_by(Item.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, item_id: UUID, payload: ItemUpdate) -> Optional[Item]:
        item = ItemService.get(db, item_id)
        if item is None:
            return None
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item_id: UUID) -> bool:
        item = ItemService.get(db, item_id)
        if item is None:
            return False
        db.delete(item)
        db.commit()
        return True
