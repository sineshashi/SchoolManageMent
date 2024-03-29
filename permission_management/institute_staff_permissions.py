from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi import Body
from db_management.models import RolesEnum
from .base_permission import union_of_all_permission_types, PermissionManager

def can_add_insititute_staff(admin_id: int=Body(embed=True), Authorize: AuthJWT=Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(Authorize=Authorize)
    if (permission_data.role==RolesEnum.appstaff) or (permission_data.role==RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role==RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role==RolesEnum.institutestaff and permission_data.admin_id == admin_id and permission_data.permissions_json.is_db_manager):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")

def can_view_institute_staff(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(Authorize=Authorize)
    if (permission_data.role==RolesEnum.appstaff) or (permission_data.role==RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role==RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role==RolesEnum.institutestaff and permission_data.admin_id == admin_id):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")

def can_delete_institute_staff(admin_id:int=Body(embed=True), Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(Authorize=Authorize, token="fresh")
    if (permission_data.role==RolesEnum.appstaff) or (permission_data.role==RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role==RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role==RolesEnum.institutestaff and permission_data.admin_id == admin_id and permission_data.permissions_json.is_db_manager):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")

def can_add_education_details_for_staff(admin_id: int=Body(embed=True), Authorize: AuthJWT=Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(Authorize=Authorize)
    if (permission_data.role==RolesEnum.appstaff) or (permission_data.role==RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role==RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role==RolesEnum.institutestaff and permission_data.admin_id == admin_id and permission_data.permissions_json.is_db_manager):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")

def can_view_education_details_of_institute_staff(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(Authorize=Authorize)
    if (permission_data.role==RolesEnum.appstaff) or (permission_data.role==RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role==RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role==RolesEnum.institutestaff and permission_data.admin_id == admin_id):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")

def can_disable_education_details_for_staff(admin_id: int=Body(embed=True), Authorize: AuthJWT=Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(Authorize=Authorize, token = "fresh")
    if (permission_data.role==RolesEnum.appstaff) or (permission_data.role==RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role==RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role==RolesEnum.institutestaff and permission_data.admin_id == admin_id and permission_data.permissions_json.is_db_manager):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")
