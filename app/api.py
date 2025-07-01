from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routers.personal_website import personal_website_router
import os

from motor.motor_asyncio import (
    AsyncIOMotorClient,
)

load_dotenv()

app = FastAPI()

origins = ["*"]


@app.on_event("startup")
async def startup_db_client():
    mongodbURI = os.getenv("MONGODB_URI")
    mongodbName = os.getenv("MONGODB_NAME")
    print(f"Connecting to MongoDB at {mongodbURI} with database {mongodbName}")
    app.state.mongo_client = AsyncIOMotorClient(mongodbURI)  # Async MongoDB client
    app.state.mongo_db = app.state.mongo_client[mongodbName]  # Database
    app.state.users_coll = app.state.mongo_db["users"]


app.include_router(personal_website_router, tags=["Users"], prefix="/jimmy_website")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_client.close()
