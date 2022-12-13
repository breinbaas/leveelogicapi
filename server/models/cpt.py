from pydantic import BaseModel, Field
from typing import Optional


class CptSchema(BaseModel):
    lat: float = Field(..., ge=0.0, le=90.0)
    lon: float = Field(..., ge=0.0, le=90.0)

    class Config:
        schema_extra = {
            "example": {
                "lat": 52.37,
                "lon": 4.90,
            }
        }


class UpdateCptModel(BaseModel):
    lat: Optional[float]
    lon: Optional[float]

    class Config:
        schema_extra = {
            "example": {
                "lat": 52.37,
                "lon": 4.90,
            }
        }
