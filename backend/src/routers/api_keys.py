"""API key management router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src import schemas, crud
from src.utils.api_key_generator import generate_api_key, hash_api_key

router = APIRouter(prefix="/api/v1/api-keys", tags=["API Keys"])


@router.post("", response_model=schemas.ApiKeyResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    key_data: schemas.ApiKeyCreate,
    db: Session = Depends(get_db)
):
    """
    Generate a new SDK API key.

    Creates a new API key with the provided name.
    The API key will be returned in the response. Store it safely
    as it won't be shown again.
    """
    # Generate the API key
    plain_api_key = generate_api_key()
    hashed_api_key = hash_api_key(plain_api_key)

    # Create API key in database
    db_key = crud.create_api_key(
        db=db,
        key_name=key_data.key_name,
        api_key=hashed_api_key
    )

    # Return response with the plain API key (only time it's shown)
    return schemas.ApiKeyResponse(
        id=db_key.id,
        name=db_key.name,
        api_key=plain_api_key,  # Return plain key for user to save
        is_active=db_key.is_active,
        created_at=db_key.created_at
    )


@router.get("", response_model=List[schemas.ApiKeyResponse])
def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all API keys.

    Returns a paginated list of all API keys in the system.
    Note: This does not return the actual API keys, only metadata.
    """
    keys = crud.get_all_api_keys(db, skip=skip, limit=limit)

    # Return without actual API keys for security
    return [
        schemas.ApiKeyResponse(
            id=key.id,
            name=key.name,
            api_key=key.api_key,  # Never return actual keys
            is_active=key.is_active,
            created_at=key.created_at
        )
        for key in keys
    ]


@router.delete("/{key_id}", response_model=schemas.SuccessResponse)
def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an API key.

    Permanently deletes an API key from the system.
    Any SDK using this key will no longer be able to authenticate.
    """
    success = crud.delete_api_key(db, key_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {key_id} not found"
        )

    return schemas.SuccessResponse(status="success", message="API key deleted successfully")


@router.patch("/{key_id}/status", response_model=schemas.ApiKeyResponse)
def update_api_key_status(
    key_id: str,
    is_active: bool,
    db: Session = Depends(get_db)
):
    """
    Enable or disable an API key.

    Updates the active status of an API key without deleting it.
    Disabled keys cannot be used for SDK authentication.
    """
    db_key = crud.update_api_key_active(db, key_id, is_active)

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {key_id} not found"
        )

    return schemas.ApiKeyResponse(
        id=db_key.id,
        name=db_key.name,
        api_key="db_key.",
        is_active=db_key.is_active,
        created_at=db_key.created_at
    )
