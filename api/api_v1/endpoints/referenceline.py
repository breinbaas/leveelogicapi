from fastapi import APIRouter, Depends, UploadFile, HTTPException
from typing import Annotated, List
from leveelogic.objects.cpt import Cpt
from pathlib import Path
import tempfile
from leveelogic.objects.referenceline import ReferenceLine

from ...security import User, get_current_active_user

router = APIRouter()


@router.post("/to_json")
async def referenceline_shapefile_to_json(
    files: List[UploadFile],
    # current_user: Annotated[User, Depends(get_current_active_user)],
):
    # write to temp location
    with tempfile.TemporaryDirectory() as temp_dir:
        shp_filename = ""
        for file in files:
            # write the file (lowercase)
            temp_file_path = Path(temp_dir) / file.filename.lower()
            with open(temp_file_path, "wb") as temp_file:
                if temp_file_path.suffix == ".shp":
                    shp_filename = temp_file_path
                contents = await file.read()
                temp_file.write(contents)

        if shp_filename == "":
            raise HTTPException(
                status_code=400,
                detail="No .shp file found",
            )

        try:
            rl = ReferenceLine.from_shape(shp_filename)
            return rl
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading file '{e}'",
            )
