from fastapi import APIRouter, Body, UploadFile
from fastapi.encoders import jsonable_encoder
from pathlib import Path
from io import BytesIO
from starlette.responses import StreamingResponse
import requests
import base64

from leveelogic.objects.cpt import Cpt, CptConversionMethod

from ..const import ALLOWED_LOCATIONS


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

# HELPER FUNCTIONS
async def upload_file_to_cpt(file: UploadFile) -> Cpt:
    # get the prefix of the file, we only accept .gef and .xml
    suffix = Path(file.filename).suffix.lower()
    if not suffix in [".gef", ".xml"]:
        raise ValueError(f"Can only handle .gef or .xml cpts")

    # try to make a cpt from the data
    contents = await file.read()
    try:
        cpt_string = contents.decode(errors="ignore")
        cpt = Cpt.from_string(cpt_string, suffix)
    except Exception as e:
        raise ValueError(f"Error reading Cpt file; {str(e)}")
    return cpt


async def cpt_schema_to_cpt(cpt_schema: CptSchema) -> Cpt:
    cpt = Cpt(
        name=cpt_schema["name"],
        startdate=cpt_schema["date"],
        top=cpt_schema["top"],
        bottom=cpt_schema["bottom"],
        pre_excavated_depth=cpt_schema["pre_excavated_depth"],
        z=cpt_schema["zs"],
        qc=cpt_schema["qc"],
        fs=cpt_schema["fs"],
        fr=cpt_schema["fr"],
        u=cpt_schema["u2"],
    )
    cpt.latlon = cpt_schema["lat"], cpt_schema["lon"]
    return cpt


# CREATE
@router.post("/", response_description="Cpt data added into the database")
async def create_cpt_data(cpt: CptSchema = Body(...)):
    cpt = jsonable_encoder(cpt)

    if cpt["location"] not in ALLOWED_LOCATIONS:
        return ErrorResponseModel(
            "An error occurred.",
            404,
            f"Unsupported location '{cpt['location']}' found (options are 'crest', 'polder', 'both')",
        )

    new_cpt = await create_cpt(cpt)
    return ResponseModel(new_cpt, "Cpt added successfully.")


@router.post("/upload/", response_description="Cpt data uploaded into the database")
async def create_upload_file(file: UploadFile, location: str = "both"):
    if location not in ALLOWED_LOCATIONS:
        return ErrorResponseModel(
            "An error occurred.",
            404,
            f"Unsupported location '{location}' found (options are 'crest', 'polder', 'both')",
        )

    try:
        cpt = await upload_file_to_cpt(file)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    # done, create a cpt schema to add to the database
    cpt_schema = CptSchema(
        name=cpt.name,
        date=cpt.date,
        location=location,
        lat=cpt.lat,  # cpt.lat
        lon=cpt.lon,  # cpt.lon
        top=cpt.top,
        bottom=cpt.bottom,
        pre_excavated_depth=cpt.pre_excavated_depth,
        zs=[round(z, 3) for z in cpt.z],
        qc=[round(z, 3) for z in cpt.qc],
        fs=[round(z, 5) for z in cpt.fs],
        fr=[round(z, 3) for z in cpt.fr],
        u2=[round(z, 5) for z in cpt.u],
    )
    cpt_schema = jsonable_encoder(cpt_schema)
    new_cpt = await create_cpt(cpt_schema)
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

    if "location" in req.keys():
        if not req["location"] in ALLOWED_LOCATIONS:
            return ErrorResponseModel(
                "An error occurred.",
                404,
                f"Unsupported location '{req['location']}' found (options are 'crest', 'polder', 'both')",
            )

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


# CLASSIFICATION FROM DATABASE
@router.post(
    "/classify/{id}",
    response_description="Robertson classification of Cpt from database",
)
async def classify_from_database_id(
    id: str,
    minimum_layer_height: float = 0.2,
    peat_friction_ratio: float = 6.0,
):
    try:
        cpt_schema = await retrieve_cpt(id)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    if cpt_schema:
        cpt = await cpt_schema_to_cpt(cpt_schema)
        sp1 = cpt.to_soilprofile1(
            CptConversionMethod.ROBERTSON, minimum_layer_height, peat_friction_ratio
        )
        return ResponseModel(
            [layer.dict() for layer in sp1.soillayers],
            "Cpt converted to soillayers using Robertson",
        )

    return ErrorResponseModel("An error occurred.", 404, "Cpt doesn't exist.")


# CLASSIFICATION FROM UPLOAD
@router.post(
    "/classify/", response_description="Robertson classification of uploaded Cpt data"
)
async def classify_from_upload(
    file: UploadFile,
    minimum_layer_height: float = 0.2,
    peat_friction_ratio: float = 6.0,
):
    try:
        cpt = await upload_file_to_cpt(file)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    sp1 = cpt.to_soilprofile1(
        CptConversionMethod.ROBERTSON, minimum_layer_height, peat_friction_ratio
    )
    return ResponseModel(
        [layer.dict() for layer in sp1.soillayers],
        "Cpt converted to soillayers using Robertson",
    )


# PLOT FROM UPLOAD
@router.post(
    "/plot/",
    response_description="Plot of the uploaded Cpt data with the Robertson correlation",
)
async def plot_from_upload(
    file: UploadFile,
    minimum_layer_height: float = 0.2,
    peat_friction_ratio: float = 6.0,
):
    try:
        cpt = await upload_file_to_cpt(file)
        fig = cpt.plot(
            cptconversionmethod=CptConversionMethod.ROBERTSON,
            minimum_layerheight=minimum_layer_height,
            peat_friction_ratio=peat_friction_ratio,
        )
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    return StreamingResponse(buf, media_type="image/png")


#########
# PECTO #
#########

# PLOT FROM PECTO URL
@router.post(
    "/plot_from_url/",
    response_description="base64 string for the plot of the Cpt data with the Robertson correlation from a given URL",
)
async def plot_from_url(
    url: str,
    minimum_layer_height: float = 0.2,
    peat_friction_ratio: float = 6.0,
):
    try:
        response = requests.get(url)
        data = response.text
        cpt = Cpt.from_string(data, ".gef")
        # cpt = await upload_file_to_cpt(file)
        fig = cpt.plot(
            cptconversionmethod=CptConversionMethod.ROBERTSON,
            minimum_layerheight=minimum_layer_height,
            peat_friction_ratio=peat_friction_ratio,
        )
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        base64png = base64.b64encode(buf.read()).decode()

    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    # return StreamingResponse(buf, media_type="image/png")
    return base64png


# CLASSIFY FROM PECTO URL
@router.post(
    "/classify_from_url/",
    response_description="Robertson classification of Cpt data",
)
async def classify_from_url(
    url: str,
    minimum_layer_height: float = 0.2,
    peat_friction_ratio: float = 6.0,
):
    try:
        response = requests.get(url)
        data = response.text
        cpt = Cpt.from_string(data, ".gef")
        sp1 = cpt.to_soilprofile1(
            CptConversionMethod.ROBERTSON, minimum_layer_height, peat_friction_ratio
        )

    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    return ResponseModel(
        [layer.dict() for layer in sp1.soillayers],
        "Cpt converted to soillayers using Robertson",
    )
