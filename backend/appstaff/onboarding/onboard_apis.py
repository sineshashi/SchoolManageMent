from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi import Depends
from appstaff.onboarding.onboard_datatypes import CreateSuperAdminDesignationTypeIN, CreategAdminDesignationTypeIn
from appstaff.asm_dependencies import can_create_designation, AppStaffPermissionReturnDataType
from appstaff.asm_dependencies import can_onboard
from project.models import Designation
from project.models import Permission, PermissionLevelEnum, RolesEnum, UserDB, SuperAdmin, Admin
from project.shared.common_datatypes import SuperAdminDataTypeIn, AdminDataTypeIn, UserCreateDataTypeIn
from tortoise.transactions import atomic
from auth.auth_config import pwd_context

router = APIRouter()

@router.post("/createAdminAndSuperAdminLevelDesignation")
async def create_admin_level_and_super_admin_level_designation(super_admin_designation: Optional[CreateSuperAdminDesignationTypeIN]=None, admin_designation: Optional[CreategAdminDesignationTypeIn]=None, token_data: AppStaffPermissionReturnDataType = Depends(can_create_designation)):
    superadmindes = [None]
    admindes = [None]
    if super_admin_designation is not None:
        if not token_data.permissions_json.all_auth and "superadmin" not in token_data.permissions_json.permitted_roles_for_designation.create_designation_in_roles:
            raise HTTPException(
                406, "YOu are not authorized to create designation for super admin.")
        superadmindes = await Permission.get_or_create(
            designation=super_admin_designation.designation,
            permission_level=PermissionLevelEnum.super_admin_level,
            role=RolesEnum.superadmin,
            defaults={
                "permissions_json": super_admin_designation.permissions_json.dict(),
                "created_by_id": token_data.user_id
                }
        )
    if admin_designation is not None:
        if not token_data.permissions_json.all_auth and "admin" not in token_data.permissions_json.permitted_roles_for_designation.create_designation_in_roles:
            raise HTTPException(
                406, "YOu are not authorized to create designation for admin.")
        admindes = await Permission.get_or_create(
            designation=admin_designation.designation,
            permission_level=PermissionLevelEnum.admin_level,
            role=RolesEnum.admin,
            defaults={
                "permissions_json": admin_designation.permissions_json.dict(),
                "created_by_id": token_data.user_id
                }
        )
    return {"super_admin_designation": superadmindes[0], "admin_designation": admindes[0]}

@router.get("/getAllPermissionsAndDesignationsForAdminsAndSuperAdmins")
async def get_all_designations_for_admin_and_super_admin_role():
    return {
        "super_admin_designations": await Permission.filter(role = RolesEnum.superadmin, permission_level_instance_id=None).values(),
        "admin_designation": await Permission.filter(role = RolesEnum.admin, permission_level_instance_id=None).values()
    }

@router.post("/onboardSuperAdmin")
async def create_superadmin(super_admin_permission_id: int, user_data:UserCreateDataTypeIn, super_admin_data: SuperAdminDataTypeIn, from_time_at_designation:Optional[datetime]=None, token_data: AppStaffPermissionReturnDataType=Depends(can_onboard)):
    created_by_id = token_data.user_id
    from_time=None
    if from_time_at_designation is not None:
        from_time = from_time_at_designation.astimezone("utc")
    @atomic()
    async def on_board_atomically():
        user = await UserDB.create(username=user_data.username, password=pwd_context.hash(user_data.password1))
        super_admin_data_dict = super_admin_data.dict()
        permission = await Permission.get(id=super_admin_permission_id)
        #make active = false initially untill payment is not successful later.
        superadmin = await SuperAdmin.create(**super_admin_data_dict, created_by_id=created_by_id, user=user)
        designation = await Designation.create(
            role = permission.role,
            designation=permission.designation,
            role_instance_id = superadmin.id,
            user=user,
            permission=permission,
            from_time=from_time
        )
        user = await UserDB.filter(user_id=user.user_id).values(
            username="username",
            created_at="created_at",
            updated_at="updated_at",
            user_id = "user_id",
            active = "active"
        )
        super_admin = await SuperAdmin.filter(id=superadmin.id).values()
        designation_data = await Designation.filter(id=designation.id)
        return {
            "user": user[0],
            "super_admin": super_admin[0],
            "designation": designation_data[0]
        }
    return await on_board_atomically()

@router.post("/onboardAdmin")
async def create_admin(admin_permission_id: int, super_admin_id: int, user_data:UserCreateDataTypeIn, admin_data: AdminDataTypeIn, from_time_at_designation:Optional[datetime]=None, token_data: AppStaffPermissionReturnDataType=Depends(can_onboard)):
    superadmindetails = await SuperAdmin.filter(id=super_admin_id)
    if len(superadmindetails) == 0 or not superadmindetails[0].active or superadmindetails[0].blocked:
        raise HTTPException(406, "This super admin does not exists")
    created_by_id = token_data.user_id
    from_time=None
    if from_time_at_designation is not None:
        from_time = from_time_at_designation.astimezone("utc")
    @atomic()
    async def on_board_atomically():
        user = await UserDB.create(username=user_data.username, password=pwd_context.hash(user_data.password1))
        super_admin_data_dict = admin_data.dict()
        permission = await Permission.get(id=admin_permission_id)
        #Make active = False untill paid later.
        admin = await Admin.create(**super_admin_data_dict, created_by_id=created_by_id, user=user, super_admin_id=super_admin_id)
        designation = await Designation.create(
            role = permission.role,
            designation=permission.designation,
            role_instance_id = admin.id,
            user=user,
            permission=permission,
            from_time=from_time
        )
        user = await UserDB.filter(user_id=user.user_id).values(
            username="username",
            created_at="created_at",
            updated_at="updated_at",
            user_id = "user_id",
            active = "active"
        )
        admin = await Admin.filter(id=admin.id).values()
        designation_data = await Designation.filter(id=designation.id)
        return {
            "user": user[0],
            "admin": admin[0],
            "designation": designation_data[0]
        }
    return await on_board_atomically()