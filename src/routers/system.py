import tomllib
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/")
def root():
    return {"status": "ok"}


@router.get("/version")
def version():
    try:
        pyproject_path = (
            Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
        )
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        app_version = data.get("project", {}).get("version", "0.1.0")
    except Exception:
        app_version = "0.0.0"

    return {
        "version": app_version,
        "timestamp": datetime.now(UTC).isoformat(),
    }
