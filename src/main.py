import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import CORS_ORIGINS
from routers import system
from routers.v1 import api_v1_router

app = FastAPI(title="FastAPI Auth", version="0.0.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        field = error["loc"][-1]
        message = error["msg"]
        if message.startswith("Value error, "):
            message = message[len("Value error, ") :]
        errors[field] = message

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ORIGINS),
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(api_v1_router)

try:
    from workers import asgi

    Default = asgi.entrypoint(app)
except ImportError:
    pass
