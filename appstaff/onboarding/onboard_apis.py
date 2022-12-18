from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi import Depends
from appstaff.onboarding.onboard_datatypes import SuperAdminDataTypeIn, AdminDataTypeIn
from tortoise.transactions import atomic
from db_management.designations import DesignationManager
from db_management.models import Admin, Designation, RolesEnum, SuperAdmin, UserDB
from permission_management.base_permission import is_app_staff_or_admin_under_super_admin, union_of_all_permission_types, is_app_staff, is_app_staff_or_admin, is_app_staff_or_super_admin, is_fresh_appstaff

router = APIRouter()

@router.post("/onboardSuperAdmin")
async def create_superadmin(username: str, super_admin_data: SuperAdminDataTypeIn, designation: DesignationManager.role_designation_map["superadmin"], from_time_at_designation:Optional[datetime]=None, token_data: union_of_all_permission_types=Depends(is_app_staff)):
    created_by_id = token_data.user_id
    from_time=None
    if from_time_at_designation is not None:
        from_time = from_time_at_designation.astimezone("utc")
    @atomic()
    async def on_board_atomically():
        user = await UserDB.filter(username=username).values(
            username="username",
            created_at="created_at",
            updated_at="updated_at",
            user_id = "user_id",
            active = "active"
        )
        if len(user) != 1:
            raise HTTPException(406, "No user with this username exists.")

        if await Designation.exists(user_id = user[0]["user_id"], active = True):
            raise HTTPException(406, "User already assigned to some other role or designation.")
        
        super_admin_data_dict = super_admin_data.dict()
        superadmin = await SuperAdmin.create(**super_admin_data_dict, created_by_id=created_by_id, user_id=user[0]["user_id"])
        designation_instance = await Designation.create(
            role = RolesEnum.superadmin,
            designation=designation,
            role_instance_id = superadmin.id,
            user_id=user[0]["user_id"],
            from_time=from_time
        )
        
        super_admin = await SuperAdmin.filter(id=superadmin.id).values()
        designation_data = await Designation.filter(id=designation_instance.id).values()
        return {
            "user": user[0],
            "super_admin": super_admin[0],
            "designation": designation_data[0]
        }
    return await on_board_atomically()

@router.post("/onboardAdmin")
async def create_admin(super_admin_id: int, designation: DesignationManager.role_designation_map["admin"], username: str, admin_data: AdminDataTypeIn, from_time_at_designation:Optional[datetime]=None, token_data: union_of_all_permission_types=Depends(is_app_staff_or_super_admin)):
    superadmindetails = await SuperAdmin.filter(id=super_admin_id)
    if len(superadmindetails) == 0 or not superadmindetails[0].active or superadmindetails[0].blocked:
        raise HTTPException(406, "This super admin does not exists")
    created_by_id = token_data.user_id
    from_time=None
    if from_time_at_designation is not None:
        from_time = from_time_at_designation.astimezone("utc")

    user = await UserDB.filter(username=username).values(
            username="username",
            created_at="created_at",
            updated_at="updated_at",
            user_id = "user_id",
            active = "active"
        )
    if len(user) == 0:
        raise HTTPException(406, "No user with username exists.")

    @atomic()
    async def on_board_atomically():
        admin_data_dict = admin_data.dict()
        admin = await Admin.create(**admin_data_dict, created_by_id=created_by_id, user_id=user[0]["user_id"], super_admin_id=super_admin_id)
        designation_instance = await Designation.create(
            role = RolesEnum.admin,
            designation=designation,
            role_instance_id = admin.id,
            user_id=user[0]["user_id"],
            from_time=from_time
        )

        admin = await Admin.filter(id=admin.id).values()
        designation_data = await Designation.filter(id=designation_instance.id).values()
        return {
            "user": user[0],
            "admin": admin[0],
            "designation": designation_data[0]
        }
    return await on_board_atomically()

@router.get("/editSuperAdminData")
async def edit_super_admin_data(super_admin_id: int, super_admin_data: SuperAdminDataTypeIn, token_data: union_of_all_permission_types=Depends(is_app_staff_or_super_admin)):
    if token_data.role == RolesEnum.superadmin and token_data.role_instance_id != super_admin_id:
        raise HTTPException(401, "You are not authorized for the action.")

    updated_by = token_data.user_id
    await SuperAdmin.filter(id = token_data.role_instance_id).update(**super_admin_data.dict(), updated_by_id = updated_by)
    return await SuperAdmin.filter(id = token_data.role_instance_id).values()[0]

@router.get("/editAdminData")
async def edit_admin_data(admin_id: int, admin_data: AdminDataTypeIn, token_data: union_of_all_permission_types=Depends(is_app_staff_or_super_admin)):
    if token_data.role == RolesEnum.admin and token_data.role_instance_id != admin_id:
        raise HTTPException(401, "You are not authorized for the action.")

    await Admin.filter(id = token_data.role_instance_id).update(**admin_data.dict())
    return await Admin.filter(id = token_data.role_instance_id).values()[0]

@router.delete("/disableSuperAdmin")
async def disable_super_admin(super_admin_id: int, token_data: union_of_all_permission_types = Depends(is_fresh_appstaff)):
    await Designation.filter(role=RolesEnum.superadmin, role_instance_id = super_admin_id).update(active=False)
    await SuperAdmin.filter(id = super_admin_id).update(active=False)
    return {"success": True}

@router.delete("/disableAdmin")
async def disable_super_admin(admin_id: int, token_data: union_of_all_permission_types = Depends(is_fresh_appstaff)):
    await Designation.filter(role=RolesEnum.admin, role_instance_id = admin_id).update(active=False)
    await Admin.filter(id = admin_id).update(active=False)
    return {"success": True}

@router.get("/listAllSuperAdmins")
async def fetch_all_active_super_admins(token_data: union_of_all_permission_types = Depends(is_app_staff)):
    return await SuperAdmin.filter(active=True, blocked=False).values()

@router.get("/listAllAdmins")
async def fetch_all_active_admins(token_data: union_of_all_permission_types = Depends(is_app_staff)):
    return await Admin.filter(active=True, blocked=False).values()

@router.get("/getSuperAdminData")
async def get_super_admin_data_active_or_not_active(super_admin_id: int, token_data: union_of_all_permission_types = Depends(is_app_staff_or_super_admin)):
    return {
        "super_admin_data": await SuperAdmin.get(id=super_admin_id).values(),
        "designation_data": await Designation.filter(role=RolesEnum.superadmin, role_instance_id = super_admin_id)
    }

@router.get("/getAdminData")
async def get_super_admin_data_active_or_not_active(admin_id: int, token_data: union_of_all_permission_types = Depends(is_app_staff_or_admin_under_super_admin)):
    return {
        "super_admin_data": await Admin.get(id=admin_id).values(),
        "designation_data": await Designation.filter(role=RolesEnum.admin, role_instance_id = admin_id)
    }