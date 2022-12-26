from tortoise.contrib.pydantic import pydantic_model_creator
from db_management.models import ParentGaurdian, Designation
from pydantic import BaseModel

class ParentGaurdianProfileData(BaseModel):
    pass