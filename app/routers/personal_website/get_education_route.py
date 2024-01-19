
from .personal_website_router import personal_website_router
from fastapi import Depends
from ...database import get_db
from ...models.personal_website.education_models import EducationHistoryModel
from sqlalchemy.orm import Session


@personal_website_router.get("/get_education_history")
async def get_education_history(db: Session = Depends(get_db)):
    response = db.query(EducationHistoryModel).all()
    return response
