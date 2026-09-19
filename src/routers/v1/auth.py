import traceback
from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from database import db_users, revoked_tokens
from schemas import Token, UserLogin, UserRegister
from security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth")
security_bearer = HTTPBearer(
    auto_error=False
)  # Allow optional bearer token for refresh endpoint


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _raise_bad_credentials() -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    email = _normalize_email(user.email)

    if email in db_users:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = hash_password(user.password)
        db_users[email] = {
            "firstName": user.firstName,
            "lastName": user.lastName,
            "hashed_password": hashed_password,
        }
        return {"message": "User registered successfully"}
    except Exception:
        error_traceback = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_traceback,
        ) from None


@router.post("/login", response_model=Token)
def login(response: Response, credentials: UserLogin):
    email = _normalize_email(credentials.email)
    user = db_users.get(email)

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        _raise_bad_credentials()

    access_token = create_access_token(data={"sub": email, "type": "access"})
    refresh_token = create_access_token(
        data={"sub": email, "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Set refresh token in an HttpOnly cookie for React browser clients
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Set to True in production (HTTPS)
        samesite="none",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
):
    # Support both HttpOnly cookie (React) and
    # Authorization Bearer header (External clients)
    token = request.cookies.get("refresh_token")
    if not token and credentials:
        token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token or token in revoked_tokens:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    if payload.get("type") != "refresh":
        raise credentials_exception

    email = payload.get("sub")
    if not email or email not in db_users:
        raise credentials_exception

    # Token rotation: revoke old refresh token
    revoked_tokens.add(token)

    new_access_token = create_access_token(data={"sub": email, "type": "access"})
    new_refresh_token = create_access_token(
        data={"sub": email, "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Update HttpOnly cookie with new refresh token
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
):
    # Optional bearer token revocation
    if credentials:
        revoked_tokens.add(credentials.credentials)

    # Clear the HttpOnly refresh_token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Successfully logged out"}
