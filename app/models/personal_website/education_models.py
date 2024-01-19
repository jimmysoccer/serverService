from sqlalchemy import Boolean, Column, Date, Integer, String, Double
from sqlalchemy.orm import relationship

from ...database import Base


class EducationHistoryModel(Base):
    __tablename__ = "education"

    schoolName = Column(String, primary_key=True)
    location = Column(String)
    degree = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    course = Column(String)
