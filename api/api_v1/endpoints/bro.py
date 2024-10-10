from fastapi import APIRouter, Depends, UploadFile, HTTPException
from typing import Annotated, List, Tuple
from leveelogic.objects.cpt import Cpt
from pathlib import Path
from pydantic import BaseModel

from leveelogic.api.bro_api import BROAPI

from ...security import User, get_current_active_user

router = APIRouter()


class CptsAlongLatLonLineRequest(BaseModel):
    points: List[Tuple[float, float]] = []


class CptsAlongLatLonLineResponse(BaseModel):
    cpt_strings: List[str] = []
    cpts: List[Cpt] = []


@router.post("/cpts_along_latlon_line")
async def cpts_along_latlon_line(
    input: CptsAlongLatLonLineRequest,
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    api = BROAPI()
    try:
        cpt_strings, cpts = api.get_cpts_along_line_latlon(input.points)
        return CptsAlongLatLonLineResponse(
            cpt_strings=cpt_strings,
            cpts=cpts,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting BRO cpts; '{e}'",
        )
