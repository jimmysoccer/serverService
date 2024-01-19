from sqlalchemy import Column, Integer, String, Double

from ...database import Base


class RestaurantModel(Base):
    __tablename__ = "restaurants"

    name = Column(String, unique=True, primary_key=True)
    address = Column(String)
    rating = Column(Double)
    maxCapacity = Column(Integer)
