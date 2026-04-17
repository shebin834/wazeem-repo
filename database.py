from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["ultimate_bot"]

async def get_user(user_id):
    return await db.users.find_one({"_id": user_id}) or {}

async def update_user(user_id, data):
    await db.users.update_one({"_id": user_id}, {"$set": data}, upsert=True)

async def get_counter():
    data = await db.counter.find_one({"_id": "main"})
    return data["value"] if data else 1

async def update_counter(v):
    await db.counter.update_one({"_id": "main"}, {"$set": {"value": v}}, upsert=True)
