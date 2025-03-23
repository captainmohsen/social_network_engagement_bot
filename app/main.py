import json
from typing import Any
import asyncio

from app.api.api_v1.api import api_router
from app.core.config import settings
from fastapi import BackgroundTasks, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from app.tasks.background_task import run_follower_check


class OwnDefaultResponse(JSONResponse):
    def __init__(
            self,
            content: Any = None,
            status_code: int = 200,
            headers: dict = None,
            media_type: str = None,
            background: BackgroundTasks = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        return json.dumps(
            {
                "statusCode": self.status_code,
                "data": content if self.status_code < 400 else {},
                "error": jsonable_encoder(content) if self.status_code >= 400 else {},
            },
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    default_response_class=OwnDefaultResponse,
)




@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_follower_check())


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("@app.exception_handler(RequestValidationError)-----------------", exc)
    return OwnDefaultResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.exception_handler(StarletteHTTPException)
async def req_erorr(request: Request, exc: StarletteHTTPException):
    print("@app.exception_handler(RequestValidationError)------------------", exc)
    return OwnDefaultResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"detail": exc.detail}),
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
