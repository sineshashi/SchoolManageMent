from optparse import Option
from pydantic import BaseModel
from typing import List, Optional, Union
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.exceptions import HTTPException
from db_management.designations import DesignationManager
from pydantic import validator

from db_management.models import RolesEnum

'''
Use PermissionReturnDataType at the last of every return data type of auth related dependencies.
'''


class PermissionReturnDataType(BaseModel):
    user_id: Optional[int] = None
    role_instance_id: Optional[int] = None
    role: Optional[str] = None
    designation: Optional[str] = None
    designation_id: Optional[int] = None
    other_data: dict = {}


class AppStaffPermissionReturnDataType(PermissionReturnDataType):
    permissions_json = {}


class SuperAdminPermissionReturnDataType(PermissionReturnDataType):
    permissions_json = {}
    admin_ids: List[int] = []


class AdminPermissionReturnDataType(PermissionReturnDataType):
    permissions_json = {}
    super_admin_id: int


class InstituteStaffPermissionJsonType(BaseModel):
    is_db_manager: bool = False
    is_teacher: bool = False
    head_of_subject_groupids: List[int]=[]
    vice_head_of_subject_groupids: List[int]=[]
    head_of_subject_ids: List[int]=[]
    vice_head_of_subject_ids: List[int]=[]
    head_of_class_groupids: List[int]=[]
    vice_head_of_class_groupids: List[int]=[]
    head_of_class_ids: List[int]=[]
    vice_head_of_class_ids: List[int]= []

class InstituteStaffPermissionReturnType(PermissionReturnDataType):
    permissions_json: InstituteStaffPermissionJsonType
    admin_id: int
    super_admin_id: int
    super_admin_level: bool = False


union_of_all_permission_types = Union[AppStaffPermissionReturnDataType, AdminPermissionReturnDataType,
                                      SuperAdminPermissionReturnDataType, PermissionReturnDataType, InstituteStaffPermissionReturnType]


class PermissionManager:
    @staticmethod
    def validate_token_and_return_token_data(Authorize: AuthJWT, token: str = "access", optional: bool = False) -> union_of_all_permission_types:
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

        role = user_claims["user_claims"]["role"]
        if role == RolesEnum.appstaff:
            return AppStaffPermissionReturnDataType(**user_claims["user_claims"])
        if role == RolesEnum.superadmin:
            return SuperAdminPermissionReturnDataType(**user_claims["user_claims"])
        if role == RolesEnum.admin:
            return AdminPermissionReturnDataType(**user_claims["user_claims"])
        if role == RolesEnum.institutestaff:
            return InstituteStaffPermissionReturnType(**user_claims["user_claims"])

    @staticmethod
    def validate(optional: bool = False, token: str = "access"):
        def external_wrapper(func):
            def validate_condition_and_return_permission_data(Authorize: AuthJWT = Depends()):
                permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
                    Authorize=Authorize, token=token, optional=optional)
                if func(permission_data):
                    return permission_data
                raise HTTPException(
                    406, "You are not allowed for this action.")
            return validate_condition_and_return_permission_data
        return external_wrapper


@PermissionManager.validate()
def is_app_admin(permission_data: union_of_all_permission_types):
    return permission_data.role == "appstaff" and permission_data.designation == DesignationManager.role_designation_map["appstaff"].app_admin


@PermissionManager.validate()
def is_app_staff(permission_data: union_of_all_permission_types):
    return permission_data.role == "appstaff"


@PermissionManager.validate(optional=True)
def is_app_staff_or_none(permission_data: union_of_all_permission_types):
    return permission_data.role == "appstaff" or permission_data.role is None


@PermissionManager.validate()
def is_super_admin(permission_data: union_of_all_permission_types):
    return permission_data.role == "superadmin"


@PermissionManager.validate()
def is_admin(permission_data: union_of_all_permission_types):
    return permission_data.role == "admin"


def is_app_staff_or_super_admin(super_admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if permission_data.role == RolesEnum.appstaff or (permission_data.role == RolesEnum.superadmin and super_admin_id == permission_data.role_instance_id):
        return permission_data
    else:
        raise HTTPException(406, "Not authorized for the action.")


def is_app_staff_or_admin(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if permission_data.role == RolesEnum.appstaff or (permission_data.role == RolesEnum.admin and admin_id == permission_data.role_instance_id):
        return permission_data
    else:
        raise HTTPException(406, "Not authorized for the action.")


@PermissionManager.validate(token="fresh")
def is_fresh_appstaff(permission_data: union_of_all_permission_types):
    return permission_data.role == "appstaff"


def is_app_staff_or_admin_under_super_admin(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if permission_data.role == RolesEnum.appstaff or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id):
        return permission_data
    else:
        raise HTTPException(406, "Not authorized for the action.")
