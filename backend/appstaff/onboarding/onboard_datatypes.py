from typing import Union
from pydantic import BaseModel
from typing import Union
from project.shared.necessities import AdminPermissions, SuperAdminPermissions
from project.models import RolesEnum

class CreategAdminDesignationTypeIn(BaseModel):
    designation: str
    permissions_json: AdminPermissions

class CreateSuperAdminDesignationTypeIN(BaseModel):
    designation:str
    permissions_json: SuperAdminPermissions