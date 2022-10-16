from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi import Depends
from appstaff.onboarding.onboard_datatypes import SuperAdminDataTypeIn, AdminDataTypeIn
from tortoise.transactions import atomic
from auth.auth_config import pwd_context
from project.config import ALLOW_SELF_ONBOARDING
from permission_management.base_permission import PermissionReturnDataType

router = APIRouter()

# @router.post("/onboardSuperAdmin")
# async def create_superadmin(super_admin_permission_id: int, user_data:UserCreateDataTypeIn, super_admin_data: SuperAdminDataTypeIn, from_time_at_designation:Optional[datetime]=None, token_data: PermissionReturnDataType=Depends(can_onboard)):
#     created_by_id = token_data.user_id
#     from_time=None
#     if from_time_at_designation is not None:
#         from_time = from_time_at_designation.astimezone("utc")
#     @atomic()
#     async def on_board_atomically():
#         if token_data.user_id is None and not ALLOW_SELF_ONBOARDING:
#             active = False #If super admin is being onboarded by himself, he will not be activated untill some staff activates it or after payment complete, automatically will be done.
#         user = await UserDB.create(username=user_data.username, password=pwd_context.hash(user_data.password1), active=active)
#         super_admin_data_dict = super_admin_data.dict()
#         permission = await Permission.get(id=super_admin_permission_id)
#         #make active = false initially untill payment is not successful later.
#         superadmin = await SuperAdmin.create(**super_admin_data_dict, created_by_id=created_by_id, user=user)
#         designation = await Designation.create(
#             role = permission.role,
#             designation=permission.designation,
#             role_instance_id = superadmin.id,
#             user=user,
#             permission=permission,
#             from_time=from_time
#         )
#         user = await UserDB.filter(user_id=user.user_id).values(
#             username="username",
#             created_at="created_at",
#             updated_at="updated_at",
#             user_id = "user_id",
#             active = "active"
#         )
#         super_admin = await SuperAdmin.filter(id=superadmin.id).values()
#         designation_data = await Designation.filter(id=designation.id)
#         return {
#             "user": user[0],
#             "super_admin": super_admin[0],
#             "designation": designation_data[0]
#         }
#     return await on_board_atomically()

# @router.post("/onboardAdmin")
# async def create_admin(admin_permission_id: int, super_admin_id: int, user_data:UserCreateDataTypeIn, admin_data: AdminDataTypeIn, from_time_at_designation:Optional[datetime]=None, token_data: PermissionReturnDataType=Depends(can_onboard_admin)):
#     superadmindetails = await SuperAdmin.filter(id=super_admin_id)
#     if len(superadmindetails) == 0 or not superadmindetails[0].active or superadmindetails[0].blocked:
#         raise HTTPException(406, "This super admin does not exists")
#     created_by_id = token_data.user_id
#     from_time=None
#     if from_time_at_designation is not None:
#         from_time = from_time_at_designation.astimezone("utc")
#     @atomic()
#     async def on_board_atomically():
#         if (token_data.user_id is None or token_data.role == "superadmin") and not ALLOW_SELF_ONBOARDING:
#             active = False #If super admin is being onboarded by himself, he will not be activated untill some staff activates it or after payment complete, automatically will be done.
#         user = await UserDB.create(username=user_data.username, password=pwd_context.hash(user_data.password1), active=active)
#         super_admin_data_dict = admin_data.dict()
#         permission = await Permission.get(id=admin_permission_id)
#         #Make active = False untill paid later.
#         admin = await Admin.create(**super_admin_data_dict, created_by_id=created_by_id, user=user, super_admin_id=super_admin_id)
#         designation = await Designation.create(
#             role = permission.role,
#             designation=permission.designation,
#             role_instance_id = admin.id,
#             user=user,
#             permission=permission,
#             from_time=from_time
#         )
#         user = await UserDB.filter(user_id=user.user_id).values(
#             username="username",
#             created_at="created_at",
#             updated_at="updated_at",
#             user_id = "user_id",
#             active = "active"
#         )
#         admin = await Admin.filter(id=admin.id).values()
#         designation_data = await Designation.filter(id=designation.id)
#         return {
#             "user": user[0],
#             "admin": admin[0],
#             "designation": designation_data[0]
#         }
#     return await on_board_atomically()

# @router.get("/activateSuperAdmin/{super_admin_id}")
# async def activate_super_admin_accout(super_admin_id: int, token_data: PermissionReturnDataType = Depends())