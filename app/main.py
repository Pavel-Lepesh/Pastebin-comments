import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.comments.router import comments_router, notes_comments_router
from app.config import settings
from app.db.mongo import init_mongo
from app.exceptions.handlers import register_exception_handlers
from app.logger import setup_logger
from app.logger_intercept import InterceptHandler


def configure_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongo()
    yield


app = FastAPI(lifespan=lifespan)
app_v1 = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return JSONResponse(
        content={"status": "OK", "message": "Service is healthy"},
        status_code=status.HTTP_200_OK,
    )


setup_logger()
configure_logging()


register_exception_handlers(app)
register_exception_handlers(app_v1)


app_v1.include_router(comments_router)
app_v1.include_router(notes_comments_router)
app.mount("/v1", app_v1)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
        log_config=None,
        use_colors=True,
    )
