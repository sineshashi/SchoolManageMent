from ast import Str
from typing import Optional
from tortoise.contrib.pydantic import pydantic_model_creator
from project.models import AppStaff
from pydantic import BaseModel, validator
from project.shared.necessities import AppStaffPermissions
from project.models import RolesEnum

appstaffDataTypeIn = pydantic_model_creator(AppStaff, exclude_readonly=True)

class NewAppLevelDesignationIn(BaseModel):
    role: str = RolesEnum.appstaff
    designation: str
    permissions_json: AppStaffPermissions

    @validator('role')
    def validate_role(cls, v):
        assert v in RolesEnum.__dict__
        return v