from fastapi import APIRouter

from .endpoints import cpts, referenceline

router = APIRouter()
router.include_router(cpts.router, prefix="/cpts", tags=["Cpts"])
router.include_router(
    referenceline.router, prefix="/referenceline", tags=["Referencelines"]
)
