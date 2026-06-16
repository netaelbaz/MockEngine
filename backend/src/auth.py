"""API key authentication middleware for FastAPI."""

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.crud import validate_api_key
from src.utils.api_key_generator import hash_api_key


# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> str:
    """
    Validate API key from X-API-KEY header.

    Args:
        api_key: API key from request header
        db: Database session

    Returns:
        str: Validated API key string

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Please provide X-API-KEY header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Validate the key against database
    validated_key = validate_api_key(db, api_key)
    if not validated_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


async def get_api_key_optional(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[str]:
    """
    Optionally validate API key from X-API-KEY header.

    Returns None if key is missing, raises exception if invalid.

    Args:
        api_key: API key from request header
        db: Database session

    Returns:
        Optional[str]: Validated API key string or None
    """
    if not api_key:
        return None

    # Validate the key against database
    validated_key = validate_api_key(db, api_key)
    if not validated_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key
