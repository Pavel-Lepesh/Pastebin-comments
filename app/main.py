from fastapi import FastAPI
from app.comments.router import router as comments_router
from contextlib import asynccontextmanager
from app.db.mongo import init_mongo
from app.exceptions.handlers import register_exception_handlers
from app.logger import setup_logger
from app.logger_intercept import InterceptHandler
from app.middleware.middleware import AuthMiddleware
import logging


def configure_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongo()
    yield


app = FastAPI(lifespan=lifespan)
app_v1 = FastAPI()


app.add_middleware(AuthMiddleware)


setup_logger()
configure_logging()


register_exception_handlers(app)
register_exception_handlers(app_v1)


app_v1.include_router(comments_router)
app.mount("/v1", app_v1)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_config=None, use_colors=True)
