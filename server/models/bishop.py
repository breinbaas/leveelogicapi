from pydantic import BaseModel


class BishopResultResponse(BaseModel):
    mx: float
    mz: float
    radius: float
    fos: float
