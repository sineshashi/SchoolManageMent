from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi import Body
from db_management.models import RolesEnum
from db_management.designations import DesignationManager
from .base_permission import union_of_all_permission_types, PermissionManager


def can_change_leave_config(
    admin_id: int = Body(embed=True),
    Authorize: AuthJWT = Depends()
):
    permission_data=PermissionManager.validate_token_and_return_token_data(Authorize)
    if (
        permission_data.role==RolesEnum.appstaff and
        permission_data.designation==DesignationManager.role_designation_map[RolesEnum.appstaff].app_admin
    ) or (
        permission_data.role==RolesEnum.superadmin and admin_id in permission_data.admin_ids
    ) or (
        permission_data.role==RolesEnum.admin and admin_id==permission_data.admin_id
    ) or (
        permission_data.role==RolesEnum.institutestaff and admin_id==permission_data.admin_id \
            and permission_data.permissions_json.is_db_manager
    ):
        return permission_data
    raise HTTPException(406, "You are not authorized for this action.")

def can_view_leave_config(
    Authorize: AuthJWT=Depends()
):
    permission_data = PermissionManager.validate_token_and_return_token_data(Authorize)
    return permission_data