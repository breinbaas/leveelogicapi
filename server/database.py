from bson.objectid import ObjectId
import motor.motor_asyncio

MONGO_DETAILS = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.cpts

cpt_collection = database.get_collection("cpt_collection")
borehole_collection = database.get_collection("borehole_collection")


def borehole_helper(borehole) -> dict:
    return {
        "id": str(borehole["_id"]),
        "name": borehole["name"],
        "date": borehole["date"],
        "location": borehole["location"],
        "lat": borehole["lat"],
        "lon": borehole["lon"],
        "top": borehole["top"],
        "bottom": borehole["bottom"],
        "soillayers": borehole["soillayers"],
    }


def cpt_helper(cpt) -> dict:
    return {
        "id": str(cpt["_id"]),
        "name": cpt["name"],
        "date": cpt["date"],
        "location": cpt["location"],
        "lat": cpt["lat"],
        "lon": cpt["lon"],
        "top": cpt["top"],
        "bottom": cpt["bottom"],
        "pre_excavated_depth": cpt["pre_excavated_depth"],
        "zs": cpt["zs"],
        "qc": cpt["qc"],
        "fs": cpt["fs"],
        "fr": cpt["fr"],
        "u2": cpt["u2"],
    }


#############
# BOREHOLES #
#############

# CREATE #
async def create_borehole(borehole_data: dict) -> dict:
    borehole = await borehole_collection.insert_one(borehole_data)
    new_borehole = await borehole_collection.find_one({"_id": borehole.inserted_id})
    return borehole_helper(new_borehole)


# RETRIEVE
async def retrieve_borehole(id: str) -> dict:
    borehole = await borehole_collection.find_one({"_id": ObjectId(id)})
    if borehole:
        return borehole_helper(borehole)


async def retrieve_boreholes():
    boreholes = []
    async for borehole in borehole_collection.find():
        boreholes.append(borehole_helper(borehole))
    return boreholes


# UPDATE
async def update_borehole(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    borehole = await borehole_collection.find_one({"_id": ObjectId(id)})
    if borehole:
        updated_borehole = await borehole_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_borehole:
            return True
        return False


# DELETE
async def delete_borehole(id: str):
    borehole = await borehole_collection.find_one({"_id": ObjectId(id)})
    if borehole:
        await borehole_collection.delete_one({"_id": ObjectId(id)})
        return True


########
# CPTS #
########

# CREATE #
async def create_cpt(cpt_data: dict) -> dict:
    cpt = await cpt_collection.insert_one(cpt_data)
    new_cpt = await cpt_collection.find_one({"_id": cpt.inserted_id})
    return cpt_helper(new_cpt)


# RETRIEVE
async def retrieve_cpt(id: str) -> dict:
    cpt = await cpt_collection.find_one({"_id": ObjectId(id)})
    if cpt:
        return cpt_helper(cpt)


async def retrieve_cpts():
    cpts = []
    async for cpt in cpt_collection.find():
        cpts.append(cpt_helper(cpt))
    return cpts


# UPDATE
async def update_cpt(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    cpt = await cpt_collection.find_one({"_id": ObjectId(id)})
    if cpt:
        updated_cpt = await cpt_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_cpt:
            return True
        return False


# DELETE
async def delete_cpt(id: str):
    cpt = await cpt_collection.find_one({"_id": ObjectId(id)})
    if cpt:
        await cpt_collection.delete_one({"_id": ObjectId(id)})
        return True
