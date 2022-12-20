from http.client import HTTPException
from typing import Optional
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi import Body
from db_management.models import RolesEnum
from .base_permission import union_of_all_permission_types, PermissionManager


def can_create_subject_group_department(admin_id: int=Body(embed=True), Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize, token="fresh")
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role == RolesEnum.institutestaff and permission_data.admin_id == admin_id and permission_data.permissions_json.is_db_manager):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_view_subject_group_department(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role == RolesEnum.institutestaff and permission_data.admin_id == admin_id):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_create_subject(admin_id: int=Body(embed=True), group_id: int=Body(embed=True), Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and admin_id == permission_data.admin_id) or (permission_data.role == RolesEnum.institutestaff and (group_id in permission_data.permissions_json.head_of_subject_groupids or permission_data.permissions_json.is_db_manager)):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_view_subject(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role == RolesEnum.institutestaff and permission_data.admin_id == admin_id):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_create_class_group(admin_id: int=Body(embed=True), Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize, token="fresh")
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role == RolesEnum.institutestaff and permission_data.admin_id == admin_id and permission_data.permissions_json.is_db_manager):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_view_class_group(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role == RolesEnum.institutestaff and permission_data.admin_id == admin_id):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_create_class(admin_id: int=Body(embed=True), class_group_id: int=Body(embed=True), Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and admin_id == permission_data.admin_id) or (permission_data.role == RolesEnum.institutestaff and (class_group_id in permission_data.permissions_json.head_of_class_groupids or permission_data.permissions_json.is_db_manager)):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_view_class(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role == RolesEnum.institutestaff and permission_data.admin_id == admin_id):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")

def can_create_academic_session(admin_id: int=Body(embed=True), Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and admin_id == permission_data.admin_id) or (permission_data.role == RolesEnum.institutestaff and (permission_data.permissions_json.is_db_manager)):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")


def can_view_academic_session(admin_id: int, Authorize: AuthJWT = Depends()):
    permission_data: union_of_all_permission_types = PermissionManager.validate_token_and_return_token_data(
        Authorize=Authorize)
    if (permission_data.role == RolesEnum.appstaff) or (permission_data.role == RolesEnum.superadmin and admin_id in permission_data.admin_ids) or (permission_data.role == RolesEnum.admin and permission_data.role_instance_id == admin_id) or (permission_data.role == RolesEnum.institutestaff and permission_data.admin_id == admin_id):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")