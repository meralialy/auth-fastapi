from fastapi import APIRouter, Security

from database import db_users
from dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users")


@router.get("/me")
def me(email: str = Security(get_current_user)):
    user = db_users.get(email)
    if not user:
        return {"email": email, "firstName": None, "lastName": None}

    return {
        "email": email,
        "firstName": user.get("firstName"),
        "lastName": user.get("lastName"),
    }
