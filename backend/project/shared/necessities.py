'''
This file contains some necessary regulations to follow through out the project and must be maintained to avoid bugs \n
and filling incorrect data in database.
'''

from typing import List
from ..models import Admin, AppStaff, PermissionLevelEnum, RolesEnum, SuperAdmin
from pydantic import BaseModel, validator
from fastapi.exceptions import HTTPException
from typing import Optional

#Maintain below Role Enum and getRoleModelFuntion for each new class extending User model.

    
def getRoleModel(role: str):
    if role == "appstaff":
        return AppStaff
    elif role == "superadmin":
        return SuperAdmin
    elif role == "admin":
        return Admin

#Below are the permissions defined role wise.

class PermittedRoles(BaseModel):
    create_designation_in_roles: List[RolesEnum]
    authorize_to_create_designation_in_roles: List[RolesEnum]
    authorize_to_permit_others_for_creation_in_roles: List[RolesEnum]
    create_permission_levels: List[PermissionLevelEnum]
    authorize_to_create_permission_levels: List[PermissionLevelEnum]
    authorize_to_permit_others_for_creation_in_levels: List[PermissionLevelEnum]


class AppStaffPermissions(BaseModel):
    all_auth: bool = False
    can_onboard: bool = False
    can_add_new_staff: bool = False
    can_authorize_some_staff_to_onboard: bool = False
    can_authorize_some_staff_to_add_new_one: bool = False
    can_create_designation: bool = False
    can_authorize_someone_to_create_designation: bool = False
    can_authorize_someone_to_permit_other_to_create_designation: bool = False
    permitted_roles_for_designation: Optional[PermittedRoles] = None