"""Demo backend endpoints — simulate a real API that the SDK intercepts."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/demo", tags=["Demo"])

_users = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob Smith",    "email": "bob@example.com",   "role": "user"},
    {"id": 3, "name": "Carol White",  "email": "carol@example.com", "role": "user"},
]
_next_id = 4


class UserCreate(BaseModel):
    name: str
    email: str
    role: Optional[str] = "user"


@router.get("/users")
def list_users():
    return {"users": _users, "total": len(_users), "source": "real-backend"}


@router.get("/users/{user_id}")
def get_user(user_id: int):
    user = next((u for u in _users if u["id"] == user_id), None)
    if user is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return {**user, "source": "real-backend"}


@router.post("/users", status_code=201)
def create_user(body: UserCreate):
    global _next_id
    new_user = {"id": _next_id, "name": body.name, "email": body.email, "role": body.role, "source": "real-backend"}
    _users.append(new_user)
    _next_id += 1
    return new_user
