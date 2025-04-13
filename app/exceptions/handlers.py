from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.exceptions.exceptions import ParentCommentNotFoundError, ParentConflict, ObjectNotFound
from loguru import logger


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ParentCommentNotFoundError)
    async def parent_comment_not_found_handler(request: Request, exc: ParentCommentNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Parent comment wasn't found"}
        )

    @app.exception_handler(ParentConflict)
    async def parent_conflict(request: Request, exc: ParentConflict):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Invalid hash link. There is no such a parent with the link"}
        )

    @app.exception_handler(ObjectNotFound)
    async def object_not_found(request: Request, exc: ObjectNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Searching object not found"}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.critical("Unexpected error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
