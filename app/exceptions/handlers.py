from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.exceptions.exceptions import ParentCommentNotFoundError
from loguru import logger


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ParentCommentNotFoundError)
    async def parent_comment_not_found_handler(request: Request, exc: ParentCommentNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.critical("Unexpected error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
