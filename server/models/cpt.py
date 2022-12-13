from pydantic import BaseModel, Field
from typing import Optional, List


class CptSchema(BaseModel):
    lat: float = Field(..., ge=0.0, le=90.0)
    lon: float = Field(..., ge=0.0, le=90.0)
    top: float = Field(...)
    bottom: float = Field(...)
    pre_excavated_depth: float = Field(..., ge=0.0)
    zs: List[float] = Field(...)
    qc: List[float] = Field(...)
    fs: List[float] = Field(...)
    fr: List[float] = Field(...)
    u2: List[float] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "lat": 52.37,
                "lon": 4.90,
                "top": 0.0,
                "bottom": 0.0,
                "pre_excavated_depth": 0.0,
                "zs": [],
                "qc": [],
                "fs": [],
                "fr": [],
                "u2": [],
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
