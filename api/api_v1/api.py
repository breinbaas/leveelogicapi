from fastapi import APIRouter

from .endpoints import cpts, referenceline, bro

router = APIRouter()
router.include_router(cpts.router, prefix="/cpts", tags=["Cpts"])
router.include_router(
    referenceline.router, prefix="/referenceline", tags=["Referencelines"]
)
router.include_router(bro.router, prefix="/bro", tags=["BRO"])
