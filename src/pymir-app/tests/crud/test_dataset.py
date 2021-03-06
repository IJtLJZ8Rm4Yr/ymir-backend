from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas.dataset import DatasetCreate
from tests.utils.utils import random_hash, random_lower_string


def test_create_dataset(db: Session) -> None:
    dataset_name = random_lower_string(10)
    dataset_hash = random_hash("dataset")
    commit_id = randint(1000, 9999)
    commit_hash = random_hash("commit")
    dataset_in = DatasetCreate(
        db=db,
        name=dataset_name,
        hash=dataset_hash,
        type=1,
        user_id=1,
        task_id=1,
    )
    dataset = crud.dataset.create(db=db, obj_in=dataset_in)
    assert dataset.hash == dataset_hash
    assert dataset.name == dataset_name


def test_get_dataset(db: Session) -> None:
    dataset_name = random_lower_string(10)
    dataset_hash = random_hash("dataset")
    commit_id = randint(1000, 9999)
    commit_hash = random_hash("commit")
    dataset_in = DatasetCreate(
        db=db,
        name=dataset_name,
        hash=dataset_hash,
        type=1,
        user_id=1,
        task_id=1,
    )
    dataset = crud.dataset.create(db=db, obj_in=dataset_in)
    stored_dataset = crud.dataset.get_by_hash(db=db, hash_=dataset_hash)

    assert dataset.hash == stored_dataset.hash
    assert dataset.name == stored_dataset.name
