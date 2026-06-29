"""API key management router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src import schemas, crud, models
from src.auth import get_current_user
from src.utils.api_key_generator import generate_api_key
from src.utils.encryption import decrypt

router = APIRouter(prefix="/api/v1/api-keys", tags=["API Keys"])


@router.post("", response_model=schemas.ApiKeyResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    key_data: schemas.ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    plain_api_key = generate_api_key()
    db_key = crud.create_api_key(
        db=db,
        key_name=key_data.key_name,
        api_key=plain_api_key,
        user_id=current_user.id,
    )
    return schemas.ApiKeyResponse(
        id=db_key.id,
        name=db_key.name,
        api_key=plain_api_key,
        is_active=db_key.is_active,
        created_at=db_key.created_at,
    )


@router.get("", response_model=List[schemas.ApiKeyResponse])
def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    keys = crud.get_api_keys_by_user(db, current_user.id, skip=skip, limit=limit)
    return keys


@router.delete("/{key_id}", response_model=schemas.SuccessResponse)
def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    success = crud.delete_api_key_for_user(db, key_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"API key {key_id} not found")
    return schemas.SuccessResponse(status="success", message="API key deleted successfully")


@router.patch("/{key_id}/status", response_model=schemas.ApiKeyResponse)
def update_api_key_status(
    key_id: str,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_key = crud.update_api_key_active_for_user(db, key_id, current_user.id, is_active)
    if not db_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"API key {key_id} not found")

    try:
        plain_key = decrypt(db_key.api_key)
    except Exception:
        plain_key = db_key.api_key

    return schemas.ApiKeyResponse(
        id=db_key.id,
        name=db_key.name,
        api_key=plain_key,
        is_active=db_key.is_active,
        created_at=db_key.created_at,
    )
