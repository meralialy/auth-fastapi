from __future__ import annotations

from typing import TypedDict


class UserRecord(TypedDict):
    firstName: str
    lastName: str
    hashed_password: str


# In-memory user database placeholder
db_users: dict[str, UserRecord] = {}
revoked_tokens: set[str] = set()
