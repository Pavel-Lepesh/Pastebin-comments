from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import FastAPI, Request
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    # will be developed fully later (with JWT decoding)
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.user_id = 1
        response = await call_next(request)

        return response
