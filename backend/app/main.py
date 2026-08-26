from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.routes.chat import router as chat_router
from app.database import DatabaseUnavailableError
from app.providers.base import LLMProviderError
from app.providers.ollama import OllamaResponseError, OllamaTimeoutError
from app.services import SessionNotFoundError


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)
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
