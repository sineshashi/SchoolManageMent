from db_management.models import Designation, UserDB, SuperAdmin, Admin
from pydantic import BaseModel, validator
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import Optional

userDataTypeIn = pydantic_model_creator(UserDB, exclude_readonly=True)

DesignationDataTypeIn = pydantic_model_creator(
    Designation, exclude_readonly=True)

class SuccessReponse(BaseModel):
    success: Optional[bool]=True