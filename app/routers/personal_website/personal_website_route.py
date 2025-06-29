from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...models.users.use_models import User
from .personal_website_router import personal_website_router
from fastapi.responses import JSONResponse
import bcrypt


@personal_website_router.post("/createUser")
async def create_user(user: User, request: Request):
    username = user.username
    password = user.password
    # Check if the username already exists
    if await request.app.state.users_coll.find_one({"username": username}):
        raise JSONResponse(
            status_code=400, content={"message": "Username already exists"}
        )

    # Hash the password before storing
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    # Store the user in the database
    try:
        result = await request.app.state.users_coll.insert_one(
            {"username": username, "password": hashed_password}
        )
        if result.acknowledged:
            return JSONResponse(
                status_code=200, content={"message": "successfully create a new user"}
            )
        else:
            return JSONResponse(
                status_code=404, content={"message": "create new user failed"}
            )
    except:
        return JSONResponse(
            status_code=404, content={"message": "exception create user failed"}
        )


@personal_website_router.post("/login")
async def login(user: User, request: Request):
    username = user.username
    password = user.password

    try:
        # Retrieve the user document by username
        db_user = await request.app.state.users_coll.find_one({"username": username})

        # If the user doesn't exist, raise an error
        if not db_user:
            return JSONResponse(
                status_code=404, content={"message": "Invalid credentials"}
            )

        # Check if the provided password matches the stored hashed password
        if not bcrypt.checkpw(
            password.encode("utf-8"), db_user["password"].encode("utf-8")
        ):
            return JSONResponse(
                status_code=404, content={"message": "Invalid credentials"}
            )

        return JSONResponse(status_code=200, content={"message": "login successfully!"})

    except:
        return JSONResponse(
            status_code=404, content={"message": "exception login failed"}
        )
