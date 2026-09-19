import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    PASSWORD_HASH_ITERATIONS,
    SECRET_KEY,
)


def _hash_password_value(password: str, salt: bytes, iterations: int) -> bytes:
    if hasattr(hashlib, "pbkdf2_hmac"):
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    # Cloudflare/compat runtimes may not expose hashlib.pbkdf2_hmac.
    # Fall back to a deterministic repeated SHA-256 hashing loop so auth still works.
    value = password.encode("utf-8") + salt
    for _ in range(iterations):
        value = hashlib.sha256(value).digest()
    return value


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = _hash_password_value(password, salt, PASSWORD_HASH_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(plain_password: str, stored_password: str) -> bool:
    if not stored_password:
        return False

    try:
        if stored_password.startswith("pbkdf2_sha256$"):
            _, iterations_str, salt_hex, expected_hash = stored_password.split("$", 3)
            iterations = int(iterations_str)
            actual_hash = _hash_password_value(
                plain_password,
                bytes.fromhex(salt_hex),
                iterations,
            )
            return secrets.compare_digest(actual_hash.hex(), expected_hash)

        salt, expected_hash = stored_password.split("$", 1)
        value = (salt + plain_password).encode("utf-8")
        for _ in range(10_000):
            value = hashlib.sha256(value).digest()

        return secrets.compare_digest(value.hex(), expected_hash)
    except (TypeError, ValueError, AttributeError):
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
