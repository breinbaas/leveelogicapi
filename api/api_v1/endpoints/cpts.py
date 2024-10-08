from fastapi import APIRouter, Depends
from typing import Annotated
from ...security import User, get_current_active_user

router = APIRouter()


@router.get("/ping")
async def pong(current_user: Annotated[User, Depends(get_current_active_user)],):
    return {"ping": "pong from cpts!"}