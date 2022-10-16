from lib2to3.pgen2 import token
from fastapi.routing import APIRouter
from db_management.designations import DesignationManager
from db_management.models import RolesEnum, UserDB, Designation, AppStaff
from permission_management.base_permission import PermissionReturnDataType, is_app_admin, is_app_staff
from .asm_datatypes import appstaffDataTypeIn, designationDataTypeOut, appstaffDataTypeOut
from fastapi import Depends
from tortoise.transactions import atomic
from fastapi.exceptions import HTTPException
import datetime
from typing import Optional

router = APIRouter()

@router.get("/allDesignations")
async def get_all_designations_for_role(role: RolesEnum):
    return DesignationManager.get_all_designations_for_role(role)

@router.post("/createNewAppStaff")
async def create_new_staff(
    username: str,
    profileData: appstaffDataTypeIn,
    designation: str,
    designation_start_time: Optional[datetime.datetime] = None,
    tokenData: PermissionReturnDataType=Depends(is_app_admin)
    ):
        if designation_start_time is not None:
            designation_start_time.astimezone("utc")
        user = await UserDB.get_or_none(username=username).values()
        if user is None or not user["active"]:
            raise HTTPException(status_code=404, detail="No data found")

        @atomic()
        async def create_staff():
            if await Designation.exists(user_id=user["user_id"], active=True):
                raise HTTPException(405, "This user has already a different role.")
            if not DesignationManager.validate_designation("appstaff", designation):
                raise HTTPException(405, "Not a valid designation.")
            appstaff = await AppStaff.create(**profileData.dict(), user_id = user["user_id"], update_by_id = tokenData.user_id)
            designation_instance = await Designation.create(role="appstaff", role_instance_id = appstaff.id, user_id = user["user_id"], designation=designation, from_time=designation_start_time)
            return appstaff, designation_instance
        appstaff, designation_instance = await create_staff()
        return {"appstaff":await appstaffDataTypeOut.from_queryset_single(AppStaff.get(id = appstaff.id)), "designation": await designationDataTypeOut.from_queryset_single(Designation.get(id=designation_instance.id))}

@router.get("/getProfileAndDesignationData")
async def get_all_data_for_user(token_data: PermissionReturnDataType=Depends(is_app_staff)):
    user_id = token_data.user_id
    app_staff_data = await AppStaff.filter(user_id=user_id, active=True, blocked=False).values()
    if len(app_staff_data) != 1:
        raise HTTPException(404, "Either no staff with this user_id exists or more than one are active.")
    designation_data = await Designation.filter(role_instance_id=app_staff_data[0]["id"], active=True).values(
        username = "user__username",
        designation = "designation",
        permission_json = "permissions_json",
        from_time = "from_time"
    )
    if len(designation_data) != 1:
        raise HTTPException(404, "The designation of user is blocked or does not exist or more than one.")

    return {"app_staff_data": app_staff_data[0], "designation_data": designation_data[0]}
    
@router.get("/getAllAppStaffData")
async def get_all_appstaff_data(token_data: PermissionReturnDataType = Depends(is_app_staff)):
    return await AppStaff.filter(active=True, blocked=False).values()