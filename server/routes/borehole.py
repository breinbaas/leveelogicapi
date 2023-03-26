from fastapi import APIRouter, Body, UploadFile
from fastapi.encoders import jsonable_encoder
from pathlib import Path
from io import BytesIO
from starlette.responses import StreamingResponse
import requests

from leveelogic.objects.borehole import Borehole
from leveelogic.objects.soillayer import SoilLayer
from leveelogic.helpers import soilcode_to_parameters

from ..const import ALLOWED_LOCATIONS


from server.database import (
    create_borehole,
    retrieve_boreholes,
    retrieve_borehole,
    update_borehole,
    delete_borehole,
)
from server.models.borehole import (
    BoreholeSchema,
    UpdateBoreholeModel,
)

from server.models.general import (
    ResponseModel,
    ErrorResponseModel,
)

router = APIRouter()

# HELPER FUNCTIONS
async def upload_file_to_borehole(file: UploadFile) -> Borehole:
    # get the prefix of the file, we only accept .gef and .xml
    suffix = Path(file.filename).suffix.lower()
    if not suffix in [".gef", ".xml"]:
        raise ValueError(f"Can only handle .gef or .xml boreholes")

    # try to make a borehole from the data
    contents = await file.read()
    try:
        borehole_string = contents.decode(errors="ignore")
        borehole = Borehole.from_string(borehole_string, suffix)
    except Exception as e:
        raise ValueError(f"Error reading Borehole file; {str(e)}")
    return borehole


async def borehole_schema_to_borehole(borehole_schema: BoreholeSchema) -> Borehole:
    borehole = Borehole(
        name=borehole_schema["name"],
        startdate=borehole_schema["date"],
        top=borehole_schema["top"],
        bottom=borehole_schema["bottom"],
        soillayers=[
            SoilLayer(top=d["top"], bottom=d["bottom"], soilcode=d["soilcode"])
            for d in borehole_schema["soillayers"]
        ],
    )
    borehole.latlon = borehole_schema["lat"], borehole_schema["lon"]
    return borehole


# # CREATE
# @router.post("/", response_description="Borehole data added into the database")
# async def create_borehole_data(borehole: BoreholeSchema = Body(...)):
#     borehole = jsonable_encoder(borehole)

#     if borehole["location"] not in ALLOWED_LOCATIONS:
#         return ErrorResponseModel(
#             "An error occurred.",
#             404,
#             f"Unsupported location '{borehole['location']}' found (options are 'crest', 'polder', 'both')",
#         )

#     new_borehole = await create_borehole(borehole)
#     return ResponseModel(new_borehole, "Borehole added successfully.")


# @router.post(
#     "/upload/", response_description="Borehole data uploaded into the database"
# )
# async def create_upload_file(file: UploadFile, location: str = "both"):
#     if location not in ALLOWED_LOCATIONS:
#         return ErrorResponseModel(
#             "An error occurred.",
#             404,
#             f"Unsupported location '{location}' found (options are 'crest', 'polder', 'both')",
#         )

#     try:
#         borehole = await upload_file_to_borehole(file)
#     except Exception as e:
#         return ErrorResponseModel("An error occurred.", 404, str(e))

#     # done, create a borehole schema to add to the database
#     borehole_schema = BoreholeSchema(
#         name=borehole.name,
#         date=borehole.date,
#         location=location,
#         lat=borehole.lat,
#         lon=borehole.lon,
#         top=borehole.top,
#         bottom=borehole.bottom,
#         soillayers=[sl.dict() for sl in borehole.soillayers],
#     )
#     borehole_schema = jsonable_encoder(borehole_schema)
#     new_borehole = await create_borehole(borehole_schema)
#     return ResponseModel(new_borehole, "Borehole added successfully.")


# # RETRIEVE
# @router.get("/", response_description="Boreholes retrieved")
# async def get_boreholes():
#     boreholes = await retrieve_boreholes()
#     if boreholes:
#         return ResponseModel(boreholes, "Boreholes data retrieved successfully")
#     return ResponseModel(boreholes, "Empty list returned")


# @router.get("/{id}", response_description="Borehole data retrieved")
# async def get_borehole_data(id):
#     try:
#         borehole = await retrieve_borehole(id)
#     except Exception as e:
#         return ErrorResponseModel("An error occurred.", 404, str(e))
#     if borehole:
#         return ResponseModel(borehole, "Borehole data retrieved successfully")
#     return ErrorResponseModel("An error occurred.", 404, "Borehole doesn't exist.")


# # UPDATE
# @router.put("/{id}")
# async def update_borehole_data(id: str, req: UpdateBoreholeModel = Body(...)):
#     req = {k: v for k, v in req.dict().items() if v is not None}

#     if "location" in req.keys():
#         if not req["location"] in ALLOWED_LOCATIONS:
#             return ErrorResponseModel(
#                 "An error occurred.",
#                 404,
#                 f"Unsupported location '{req['location']}' found (options are 'crest', 'polder', 'both')",
#             )

#     try:
#         updated_borehole = await update_borehole(id, req)
#     except Exception as e:
#         return ErrorResponseModel("An error occurred.", 404, str(e))
#     if updated_borehole:
#         return ResponseModel(
#             f"Borehole with ID: {id} name update is successful",
#             "Borehole updated successfully",
#         )
#     return ErrorResponseModel("An error occurred.", 404, "Borehole doesn't exist.")


# # DELETE
# @router.delete("/{id}", response_description="Borehole data deleted from the database")
# async def delete_borehole_data(id: str):
#     try:
#         deleted_borehole = await delete_borehole(id)
#     except Exception as e:
#         return ErrorResponseModel("An error occurred.", 404, str(e))
#     if deleted_borehole:
#         return ResponseModel(
#             f"Borehole with ID: {id} removed", "Borehole deleted successfully"
#         )
#     return ErrorResponseModel(
#         "An error occurred", 404, f"Borehole with id {id} doesn't exist"
#     )

# PLOT FROM UPLOAD
@router.post(
    "/plot/",
    response_description="Plot of the uploaded Borehole data with the Robertson correlation",
)
async def plot_from_upload(
    file: UploadFile,
):
    try:
        borehole = await upload_file_to_borehole(file)
        fig = borehole.plot()
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    return StreamingResponse(buf, media_type="image/png")


#########
# PECTO #
#########

# CLASSIFY FROM URL
# TEST URL: https://app.pecto.nl/app/static/wsrl/safe/go_safe/totaal_gef/VY095.+004_HB_BIT.gef
@router.post("/classify_from_url/", response_description="Borehole data as soillayers")
async def classify_from_url(url: str, include_color: bool = True):
    try:
        response = requests.get(url)
        data = response.text
        borehole = Borehole.from_string(data, ".gef")

        # compress the layers so layers with the same name are put into one layer
        borehole.compress()

        # use soilcode_to_parameters from helpers
        layer_response = [layer.dict() for layer in borehole.soillayers]

        if include_color:
            for layer_dict in layer_response:
                layer_dict["color"] = soilcode_to_parameters(layer_dict["soilcode"])[
                    "color"
                ]

    except Exception as e:
        return ErrorResponseModel("An error occurred.", 404, str(e))

    return ResponseModel(
        layer_response,
        "Borehole soillayers",
    )
