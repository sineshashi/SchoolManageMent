from fastapi.routing import APIRouter
from auth.permissions_validation import validate_app_staff_permissions
from project.models import UserDB, Designation, Permission, AppStaff
from project.shared.common_datatypes import UserCreateDataTypeIn
from .asm_dependencies import can_add_new_staff, AppStaffPermissionReturnDataType, can_create_designation
from .asm_datatypes import NewAppLevelDesignationIn, appstaffDataTypeIn
from fastapi import Depends
from auth.auth_config import pwd_context
from tortoise.transactions import atomic
from project.shared.necessities import AppStaffPermissions
from fastapi.exceptions import HTTPException
import datetime

router = APIRouter()

@router.post("/createOrRetrieveNewAppLevelDesignationForAppStaff")
async def create_new_app_level_designation_or_get_already_existing_for_the_designation_for_app_staff(app_level_designation_data: NewAppLevelDesignationIn, token_data: AppStaffPermissionReturnDataType=Depends(can_create_designation)):
    if app_level_designation_data.role != 'appstaff':
        raise HTTPException(406, "Role must be appstaff for this api.")
    
    if not token_data.permissions_json.all_auth and (not token_data.permissions_json.can_create_designation or "appstaff" not in token_data.permissions_json.permitted_roles_for_designation.create_designation_in_roles or "app_level" not in token_data.permissions_json.permitted_roles_for_designation.create_permission_levels):
        raise HTTPException(406, "You are not authorized to create the designation for this role and at this level.")
    validate_app_staff_permissions(app_level_designation_data.permissions_json, token_data.permissions_json)

    permission_json = app_level_designation_data.permissions_json
    designation_data = await Permission.get_or_create(
        designation=app_level_designation_data.designation,
        permission_level = "app_level",
        role = app_level_designation_data.role,
        defaults = {"permissions_json": permission_json.dict(), "created_by_id": token_data.user_id}
    )
    return designation_data[0]

@router.get("/getAllAppStaffDesignations")
async def get_all_app_staff_designations_with_permissions(token_data: AppStaffPermissionReturnDataType=Depends(can_add_new_staff)):
    return await Permission.filter(role = "appstaff", permission_level_instance_id = None).values()

@router.post("/createNewAppStaff")
async def create_new_staff(
    permission_id: int, #Id of permissions, which permissions should be given to him.
    userData: UserCreateDataTypeIn,
    profileData: appstaffDataTypeIn,
    designation_start_time: datetime.datetime | None = None,
    tokenData: AppStaffPermissionReturnDataType=Depends(can_add_new_staff)
    ):
        permissions = await Permission.filter(id=permission_id).values()
        if permissions[0]["role"] != "appstaff":
            raise HTTPException(406, "This is not correct permission id.")
        @atomic()
        async def createUserAndStaffAccount():
            
            user_instance = await UserDB.create(username=userData.username, password=pwd_context.hash(userData.password1))
            appstaff_data = profileData.dict()
            appstaff = await AppStaff.create(**appstaff_data, user_id = user_instance.user_id, updated_by_id = tokenData.user_id)
            designation = await Designation.create(
                user_id=user_instance.user_id,
                role="appstaff",
                designation = permissions[0]["designation"],
                permission_id = permission_id,
                from_time = designation_start_time,
                role_instance_id = appstaff.id
            )
            user_data = await UserDB.filter(user_id=user_instance.user_id).values()
            user_data[0].pop("password")
            designation = await Designation.filter(id=designation.id).values()
            appstaff = await AppStaff.filter(id=appstaff.id).values()
            return {
                "user_data": user_data[0],
                "designation_data": designation[0],
                "appstaff_data": appstaff[0]
            }

        return await createUserAndStaffAccount()