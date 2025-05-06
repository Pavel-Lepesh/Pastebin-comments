from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from loguru import logger

from app.config import settings
from app.exceptions.exceptions import CredentialsException

auth_scheme = HTTPBearer()


async def get_user_id(
    token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
):
    try:
        token_without_bearer = token.credentials.split()[1]
        payload = jwt.decode(
            token_without_bearer,
            settings.JWT_ACCESS_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("user_id")

        if user_id is None:
            logger.error("JWT error: User couldn't be None")
            raise CredentialsException
        return user_id
    except InvalidTokenError:
        logger.error("Invalid JWT token")
        raise CredentialsException
