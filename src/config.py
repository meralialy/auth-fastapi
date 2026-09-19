import os
from typing import Final

SECRET_KEY: Final[str] = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM: Final[str] = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)
REFRESH_TOKEN_EXPIRE_DAYS: Final[int] = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
PASSWORD_HASH_ITERATIONS: Final[int] = int(
    os.getenv("PASSWORD_HASH_ITERATIONS", "200000")
)
CORS_ORIGINS: Final[tuple[str, ...]] = tuple(
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:9000,http://localhost:9000,https://auth-react-1a0.pages.dev",
    ).split(",")
    if origin.strip()
)
