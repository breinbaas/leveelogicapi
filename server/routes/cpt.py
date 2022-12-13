from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.database import (
    create_cpt,
    retrieve_cpts,
    retrieve_cpt,
    update_cpt,
    delete_cpt,
)
from server.models.cpt import (
    CptSchema,
    UpdateCptModel,
)

from server.models.general import (
    ResponseModel,
    ErrorResponseModel,
)

router = APIRouter()

# CREATE
@router.post("/", response_description="Cpt data added into the database")
async def create_cpt_data(cpt: CptSchema = Body(...)):
    cpt = jsonable_encoder(cpt)
    new_cpt = await create_cpt(cpt)
    return ResponseModel(new_cpt, "Cpt added successfully.")


# RETRIEVE
@router.get("/", response_description="Cpts retrieved")
async def get_cpts():
    cpts = await retrieve_cpts()
    if cpts:
        return ResponseModel(cpts, "Cpts data retrieved successfully")
    return ResponseModel(cpts, "Empty list returned")


@router.get("/{id}", response_description="Cpt data retrieved")
async def get_cpt_data(id):
    try:
        cpt = await retrieve_cpt(id)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))
    if cpt:
        return ResponseModel(cpt, "Cpt data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "Cpt doesn't exist.")


# UPDATE
@router.put("/{id}")
async def update_cpt_data(id: str, req: UpdateCptModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    try:
        updated_cpt = await update_cpt(id, req)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))
    if updated_cpt:
        return ResponseModel(
            f"Cpt with ID: {id} name update is successful",
            "Cpt updated successfully",
        )
    return ErrorResponseModel("An error occurred.", 404, "Cpt doesn't exist.")


# DELETE
@router.delete("/{id}", response_description="Cpt data deleted from the database")
async def delete_cpt_data(id: str):
    try:
        deleted_cpt = await delete_cpt(id)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))
    if deleted_cpt:
        return ResponseModel(f"Cpt with ID: {id} removed", "Cpt deleted successfully")
    return ErrorResponseModel(
        "An error occurred", 404, f"Cpt with id {id} doesn't exist"
    )
