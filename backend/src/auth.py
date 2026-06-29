"""Authentication utilities for MockEngine — API key (SDK) and JWT (portal)."""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.database import get_db
from src.crud import validate_api_key
from src import models

# ==================== SDK: API Key auth ====================

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> models.ApiKey:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Please provide X-API-KEY header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    validated_key = validate_api_key(db, api_key)
    if not validated_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return validated_key


async def get_api_key_optional(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[str]:
    if not api_key:
        return None
    validated_key = validate_api_key(db, api_key)
    if not validated_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key


# ==================== Portal: JWT auth ====================

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

bearer_scheme = HTTPBearer()


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
