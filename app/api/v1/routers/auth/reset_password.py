from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from typing import Annotated

from app.infrastructure.db.crud.user import authenticate
from ...schemas import Token, UserNotFound

router = APIRouter(tags=["auth"])

async def forgot_password():
    pass

async def reset_password():
    pass