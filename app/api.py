from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routers.personal_website import personal_website_router
from .routers.restaurants import restaurant_router
app = FastAPI()

origins = ['*']


@app.on_event('startup')
async def startup():
    load_dotenv()

app.include_router(personal_website_router, tags=[
                   'Jimmy Website'], prefix='/jimmy_website')
app.include_router(restaurant_router, tags=[
                   'Restaurants'], prefix='/restaurants')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
