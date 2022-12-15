from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from fastapi import APIRouter

from leveelogic.models.calculationmodel import CalculationModel
from leveelogic.calculations.bishop import BishopSearchMethod
from leveelogic.calculations.bishopM import BishopM

from ..models.bishop import BishopResultResponse
from ..models.general import ErrorResponseModel

router = APIRouter()


@router.post(
    "/brute_force", response_description="Calculation result for Bishop brute force"
)
async def bishop_brute_force(calculation_model_dict: Dict):
    try:
        bishop_brute_force = BishopM(
            calculation_model=CalculationModel(**calculation_model_dict),
            method=BishopSearchMethod.BRUTE_FORCE_SMART,
        )
    except Exception as e:
        return ErrorResponseModel(
            "An error occurred.",
            404,
            f"Could not convert the given dictionary to a valid calculation model; '{str(e)}'",
        )

    sf_result = bishop_brute_force.execute()

    if len(sf_result) > 0:
        sf_result = sf_result[0]
        return BishopResultResponse(
            mx=sf_result[0],
            mz=sf_result[1],
            radius=sf_result[1] - sf_result[2],
            fos=sf_result[3],
        )
    else:
        return ErrorResponseModel(
            "An error occurred.",
            404,
            "No valid slope circles found.",
        )
