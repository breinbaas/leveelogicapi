from fastapi import APIRouter, Depends, UploadFile, HTTPException
from typing import Annotated
from leveelogic.objects.cpt import Cpt, CptInterpretationMethod
from leveelogic.objects.soilprofile import SoilProfile
from pathlib import Path
from pydantic import BaseModel

from ...security import User, get_current_active_user

router = APIRouter()


class CptToJSONRequest(BaseModel):
    file_content: str
    suffix: str
    minimum_layerheight: float = 0.2
    peat_friction_ratio: float = 5.0  

class CptToJSONResponse(BaseModel):
    cpt_string: str
    cpt: Cpt
    cpt_interpretation: SoilProfile

@router.get("/ping")
async def pong(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return {"ping": "pong from cpts!"}


@router.post("/to_json")
async def cpt_to_json(
    input: CptToJSONRequest
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        cpt = Cpt.from_string(input.file_content, suffix=input.suffix.lower())
        cpt_interpretation = cpt.to_soilprofile(
            cpt_interpretation_method=CptInterpretationMethod.ROBERTSON,
            minimum_layerheight=input.minimum_layerheight,
            peat_friction_ratio=input.peat_friction_ratio,
        )
        return CptToJSONResponse(
            cpt_string = input.file_content,
            cpt = cpt,
            cpt_interpretation = cpt_interpretation    
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading file '{e}'",
        )
