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
    exclude_ids: List[str] = []


class CptsAlongLatLonLineResponse(BaseModel):
    cpt_strings: List[str] = []
    cpts: List[Cpt] = []


class CptMetadatasAlongLatLonLineRequest(BaseModel):
    points: List[Tuple[float, float]] = []
    exclude_ids: List[str] = []


class CptMetadatasAlongLatLonLineResponse(BaseModel):
    bro_ids: List[str] = []


class CptMetadatasAlongXYLineRequest(BaseModel):
    points: List[Tuple[float, float]] = []
    exclude_ids: List[str] = []
    max_distance: float = 25.0


class CptMetadatasAlongXYLineResponse(BaseModel):
    bro_ids: List[str] = []


class CptFromBRORequest(BaseModel):
    bro_id: str


class CptFromBROResponse(BaseModel):
    cpt_string: str
    cpt: Cpt


@router.post("/cpts_along_latlon_line")
async def cpts_along_latlon_line(
    input: CptsAlongLatLonLineRequest,
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    api = BROAPI()
    try:
        cpt_strings, cpts = api.get_cpts_along_line_latlon(
            points=input.points, exclude_bro_ids=input.exclude_ids
        )
        return CptsAlongLatLonLineResponse(
            cpt_strings=cpt_strings,
            cpts=cpts,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting BRO cpts; '{e}'",
        )


@router.post("/cpt_metadatas_along_latlon_line")
async def cpt_metadatas_along_latlon_line(
    input: CptMetadatasAlongLatLonLineRequest,
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    api = BROAPI()
    try:
        cpt_mds = api.get_cpts_meta_data_along_line_latlon(
            points=input.points, exclude_bro_ids=input.exclude_ids
        )
        return CptMetadatasAlongLatLonLineResponse(bro_ids=[c.bro_id for c in cpt_mds])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting BRO cpts ids; '{e}'",
        )


@router.post("/cpt_metadatas_along_xy_line")
async def cpt_metadatas_along_xy_line(
    input: CptMetadatasAlongXYLineRequest,
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    api = BROAPI()
    try:
        cpt_mds = api.get_cpts_meta_data_along_line_xy(
            points=input.points,
            exclude_bro_ids=input.exclude_ids,
            max_distance=input.max_distance,
        )
        return CptMetadatasAlongXYLineResponse(bro_ids=[c.bro_id for c in cpt_mds])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting BRO cpts ids; '{e}'",
        )


@router.post("/cpt_from_bro_id")
async def cpt_from_bro_id(
    input: CptFromBRORequest,
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    api = BROAPI()
    try:
        cpt_string, cpt = api.get_cpt_from_bro_id(bro_id=input.bro_id)
        return CptFromBROResponse(cpt_string=cpt_string, cpt=cpt)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting BRO cpt with id '{input.bro_id}'; '{e}'",
        )
