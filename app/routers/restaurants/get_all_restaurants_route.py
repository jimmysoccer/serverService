from fastapi import Depends
from ...database import get_db
from .restaurant_router import restaurant_router
from ...models.restaurants.restaurant_models import RestaurantModel
from sqlalchemy.orm import Session


@restaurant_router.get('/get_all_restaurants')
async def get_all_restaurants(db: Session = Depends(get_db)):
    return db.query(RestaurantModel).all()
