import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.routes.chat import router as chat_router
from app.database import DatabaseUnavailableError
from app.providers.base import LLMProviderError
from app.providers.ollama import OllamaResponseError, OllamaTimeoutError
from app.services import SessionNotFoundError
from app.start import start as initialize_application

logger = logging.getLogger("lenny_growth_assistant")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json

        payload = {
            "message": record.getMessage(),
            "level": record.levelname,
            "logger": record.name,
        }
        for key in ("method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload)


if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)

    @application.on_event("startup")
    async def initialize_knowledge_base() -> None:
        """Initialize storage and seed a new transcript index for every run mode."""
        await initialize_application()

    @application.middleware("http")
    async def request_logging(request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(chat_router)

    @application.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @application.exception_handler(SessionNotFoundError)
    async def session_not_found(_: Request, error: SessionNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "session_not_found", "message": f"Session {error} does not exist"},
        )

    @application.exception_handler(OllamaTimeoutError)
    async def ollama_timeout(_: Request, error: OllamaTimeoutError) -> JSONResponse:
        return JSONResponse(status_code=504, content={"error": "llm_timeout", "message": str(error)})

    @application.exception_handler(LLMProviderError)
    async def provider_error(_: Request, error: LLMProviderError) -> JSONResponse:
        error_code = "llm_response_error" if isinstance(error, OllamaResponseError) else "llm_unavailable"
        return JSONResponse(status_code=502, content={"error": error_code, "message": str(error)})

    @application.exception_handler(DatabaseUnavailableError)
    async def database_error(_: Request, error: DatabaseUnavailableError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"error": "database_unavailable", "message": "Database operation failed"},
        )

    return application


app = create_app()
