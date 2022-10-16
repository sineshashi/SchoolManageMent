from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.exceptions import HTTPException
from db_management.designations import AppStaffDesignations
from permission_management.base_permission import PermissionReturnDataType

async def is_app_admin(Authorize: AuthJWT=Depends())->PermissionReturnDataType:
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    role_dict = user_claims["user_claims"]["role_and_permissions"]
    if role_dict is not None and role_dict["designation"] == AppStaffDesignations.app_admin and user_claims["sub"] == "appstaff":
        return PermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"],
            "role": user_claims["sub"]
            })
    else:
        raise HTTPException(406, "You are not permitted to add new staff.")

async def is_appstaff(Authorize: AuthJWT=Depends())->PermissionReturnDataType:
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    role_dict = user_claims["user_claims"]["role_and_permissions"]
    if role_dict is not None and user_claims["sub"] == "appstaff":
        return PermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"],
            "role": user_claims["sub"]
            })
    else:
        raise HTTPException(406, "You are not permitted to add new staff.")