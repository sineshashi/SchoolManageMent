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
        permissions_json.get("all_auth") or permissions_json.get("can_create_designation")
    ) and user_claims["sub"] == "appstaff":
        return AppStaffPermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
            })
    else:
        raise HTTPException(406, "You are not permitted to create new designation.")

async def can_get_data_for_appstaff(user_id: int, Authorize: AuthJWT=Depends())->AppStaffPermissionReturnDataType:
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    permissions_json = user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
    if permissions_json is not None and (
        permissions_json.get("all_auth") or permissions_json.get("can_get_other_app_staff_data") or user_id == user_claims["user_claims"]["user_id"]
    ) and user_claims["sub"] == "appstaff":
        return AppStaffPermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
            })
    else:
        raise HTTPException(406, "You are not permitted to access data for this user.")

async def is_valid_staff(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    if user_claims["sub"] == "appstaff":
        return AppStaffPermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
            })
    else:
        raise HTTPException(406, "You are not appstaff.")

async def can_onboard(Authorize: AuthJWT = Depends()):
    Authorize.jwt_optional()
    user_claims = Authorize.get_raw_jwt()
    if user_claims is not None:
        if user_claims["sub"] == "appstaff" and (user_claims["user_claims"]["role_and_permissions"]["permissions_json"]["all_auth"] or user_claims["user_claims"]["role_and_permissions"]["permissions_json"]["can_onboard"]):
            return AppStaffPermissionReturnDataType(**{
                "permission": True,
                "user_id": user_claims["user_claims"]["user_id"],
                "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
                "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
                })
        else:
            raise HTTPException(406, "You are not appstaff.")
    else:
        return AppStaffPermissionReturnDataType(**{
            "permission": True,
            "user_id": None,
            "role_instance_id":None,
            "permissions_json": None
        })

async def can_onboard_admin(Authorize: AuthJWT = Depends()):
    Authorize.jwt_optional()
    user_claims = Authorize.get_raw_jwt()
    if user_claims is not None:
        if user_claims["sub"] == "appstaff" and (user_claims["user_claims"]["role_and_permissions"]["permissions_json"]["all_auth"] or user_claims["user_claims"]["role_and_permissions"]["permissions_json"]["can_onboard"]):
            return AppStaffPermissionReturnDataType(**{
                "permission": True,
                "user_id": user_claims["user_claims"]["user_id"],
                "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
                "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
                })
        elif user_claims['sub'] == "superadmin":
            return AppStaffPermissionReturnDataType(**{
                "permission": True,
                "user_id": user_claims["user_claims"]["user_id"],
                "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
                "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"]
                })
        else:
            raise HTTPException(406, "You are not appstaff.")
    else:
        return AppStaffPermissionReturnDataType(**{
            "permission": True,
            "user_id": None,
            "role_instance_id":None,
            "permissions_json": None
        })

