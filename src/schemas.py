from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from config import ACCESS_TOKEN_EXPIRE_MINUTES


def _require_non_empty(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Field must not be empty")
    return normalized


class UserRegister(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    firstName: str
    lastName: str
    email: str
    password: str
    confirmPassword: str

    @field_validator("firstName", "lastName")
    @classmethod
    def validate_names(cls, value: str) -> str:
        return _require_non_empty(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = _require_non_empty(value)
        try:
            validated = validate_email(normalized, check_deliverability=False)
            return validated.email
        except EmailNotValidError as exc:
            raise ValueError("Invalid email format") from exc

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        normalized = _require_non_empty(value)
        if len(normalized) < 10:
            raise ValueError("Password must be at least 10 characters long")
        return normalized

    @field_validator("confirmPassword")
    @classmethod
    def validate_confirm_password(cls, value: str, info: ValidationInfo) -> str:
        normalized = _require_non_empty(value)

        password = info.data.get("password")
        if password is not None and normalized != password.strip():
            raise ValueError("Passwords do not match")

        return normalized


class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
