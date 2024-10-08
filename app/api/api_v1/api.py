from fastapi import APIRouter

from .endpoints import cpts

router = APIRouter()
router.include_router(cpts.router, prefix="/cpts", tags=["Cpts"])