from fastapi import APIRouter, Depends, UploadFile, HTTPException
from typing import Annotated
from leveelogic.objects.cpt import Cpt
from pathlib import Path

from ...security import User, get_current_active_user

router = APIRouter()


@router.get("/ping")
async def pong(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return {"ping": "pong from cpts!"}


@router.post("/to_json")
async def cpt_to_json(file: UploadFile):
    contents = await file.read()
    suffix = Path(file.filename).suffix.lower()
    try:
        s_utf8 = contents.decode("utf-8", errors="ignore")
        cpt = Cpt.from_string(s_utf8, suffix=suffix)
        return cpt
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file '{e}'")
