from bson.objectid import ObjectId
import motor.motor_asyncio

MONGO_DETAILS = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.cpts

cpt_collection = database.get_collection("cpt_collection")


def cpt_helper(cpt) -> dict:
    return {
        "id": str(cpt["_id"]),
        "lat": cpt["lat"],
        "lon": cpt["lon"],
    }


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
    student = await cpt_collection.find_one({"_id": ObjectId(id)})
    if student:
        await cpt_collection.delete_one({"_id": ObjectId(id)})
        return True
