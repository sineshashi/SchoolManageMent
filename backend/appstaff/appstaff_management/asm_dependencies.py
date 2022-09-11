from auth.auth_config import pwd_context
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from pydantic import BaseModel
from fastapi.exceptions import HTTPException
from typing import Optional

from project.shared.necessities import AppStaffPermissions

'''
Use PermissionReturnDataType at the last of every return data type of auth related dependencies.
'''
class AppStaffPermissionReturnDataType(BaseModel):
    permission: bool
    user_id: Optional[int] = None
    role_instance_id: Optional[int] = None
    permissions_json: Optional[AppStaffPermissions] = None

async def can_add_new_staff(Authorize: AuthJWT=Depends())->AppStaffPermissionReturnDataType:
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    permissions_json = user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
    if permissions_json is not None and (
        permissions_json.get("all_auth") or permissions_json.get("can_add_new_staff")
    ) and user_claims["sub"] == "appstaff":
        return AppStaffPermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
            })
    else:
        raise HTTPException(406, "You are not permitted to add new staff.")

async def can_create_designation(Authorize: AuthJWT=Depends())->AppStaffPermissionReturnDataType:
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    permissions_json = user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
    if permissions_json is not None and (
        not permissions_json.get("all_auth") or not permissions_json.get("can_create_designation")
    ) and user_claims["sub"] == "appstaff":
        return AppStaffPermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
            })
    else:
        raise HTTPException(406, "You are not permitted to create new designation.")
