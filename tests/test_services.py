"""Service layer tests."""
from uuid import uuid4

import pytest

from api.schemas.item import ItemCreate, ItemUpdate
from services.item_service import ItemService


def test_create_and_get(db_session) -> None:
    payload = ItemCreate(name="svc-item", description="from service")
    created = ItemService.create(db=db_session, payload=payload)
    assert created.id is not None
    assert created.name == "svc-item"

    fetched = ItemService.get(db=db_session, item_id=created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_list_pagination_validates(db_session) -> None:
    with pytest.raises(ValueError):
        ItemService.list(db=db_session, skip=-1)

    with pytest.raises(ValueError):
        ItemService.list(db=db_session, limit=0)

    with pytest.raises(ValueError):
        ItemService.list(db=db_session, limit=10_000)


def test_update_partial(db_session) -> None:
    created = ItemService.create(db=db_session, payload=ItemCreate(name="before"))
    updated = ItemService.update(
        db=db_session, item_id=created.id, payload=ItemUpdate(description="added")
    )
    assert updated is not None
    assert updated.name == "before"
    assert updated.description == "added"


def test_update_missing_returns_none(db_session) -> None:
    result = ItemService.update(
        db=db_session, item_id=uuid4(), payload=ItemUpdate(name="x")
    )
    assert result is None


def test_delete_returns_bool(db_session) -> None:
    created = ItemService.create(db=db_session, payload=ItemCreate(name="x"))
    assert ItemService.delete(db=db_session, item_id=created.id) is True
    assert ItemService.delete(db=db_session, item_id=created.id) is False
