from ast import Str
from typing import Optional, Union
from tortoise.contrib.pydantic import pydantic_model_creator
from db_management.designations import AppStaffDesignations
from db_management.models import AppStaff, Designation
from pydantic import BaseModel, validator
from project.shared.necessities import AppStaffPermissions
from db_management.models import RolesEnum

appstaffDataTypeIn = pydantic_model_creator(AppStaff, exclude_readonly=True)
appstaffDataTypeOut = pydantic_model_creator(AppStaff)
designationDataTypeOut = pydantic_model_creator(Designation)

class NewAppLevelDesignationIn(BaseModel):
    role: str = RolesEnum.appstaff
    designation: str
    permissions_json: AppStaffPermissions

    @validator('role')
    def validate_role(cls, v):
        assert v == RolesEnum.appstaff
        return v

    @validator('designation')
    def validate_designation(cls, v):
        assert v in AppStaffDesignations.__dict__
        return v