from optparse import Option
from pydantic import BaseModel
from typing import Optional, Union
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.exceptions import HTTPException
from db_management.designations import DesignationManager

'''
Use PermissionReturnDataType at the last of every return data type of auth related dependencies.
'''
class PermissionReturnDataType(BaseModel):
    permission: bool
    user_id: Optional[int] = None
    role_instance_id: Optional[int] = None
    permissions_json = {}
    role: Optional[str] = None
    designation: Optional[str] = None

class PermissionManager:
    @staticmethod
    def validate_token_and_return_token_data(Authorize: AuthJWT, token, optional: bool=False)->PermissionReturnDataType:
        '''token will be from access, fresh and refresh. Optional can be passed in case of access token. In other cases, optional does not matter.'''
        if token not in ["access", "fresh", "refresh"]:
            raise ValueError("token param is not valid.")
        if token == "access":
            if optional:
                Authorize.jwt_optional()
                user_claims = None
            else:
                Authorize.jwt_required()
                user_claims = Authorize.get_raw_jwt()
        if token == "refresh":
            Authorize.jwt_refresh_token_required()
            user_claims = Authorize.get_raw_jwt()
        if token == "fresh":
            Authorize.fresh_jwt_required()
            user_claims = Authorize.get_raw_jwt()

        if not user_claims:
            return PermissionReturnDataType(permission=True)
        
        return PermissionReturnDataType(**{
            "permission": True,
            "user_id": user_claims["user_claims"]["user_id"],
            "role_instance_id": user_claims["user_claims"]["role_and_permissions"]["role_instance_id"],
            "permissions_json": user_claims["user_claims"]["role_and_permissions"]["permissions_json"],
            "role": user_claims["sub"],
            "designation": user_claims["user_claims"]["role_and_permissions"]["designation"]
            })

    @staticmethod
    def validate(optional: bool = False, token: str = "access"):
        def external_wrapper(func):
            def validate_condition_and_return_permission_data(Authorize: AuthJWT = Depends()):
                permission_data: PermissionReturnDataType = PermissionManager.validate_token_and_return_token_data(Authorize=Authorize, token=token, optional=optional)
                if func(permission_data):
                    return permission_data
                raise HTTPException(406, "You are not allowed for this action.")
            return validate_condition_and_return_permission_data
        return external_wrapper

@PermissionManager.validate()
def is_app_admin(permission_data: PermissionReturnDataType):
    return permission_data.role == "appstaff" and permission_data.designation == DesignationManager.role_designation_map["appstaff"].app_admin

@PermissionManager.validate()
def is_app_staff(permission_data: PermissionReturnDataType):
    return permission_data.role == "appstaff"