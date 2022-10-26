from venv import create
from fastapi import APIRouter, Depends
from db_management.db_sql_and_functions import get_list_of_all_staffs_with_designation
from db_management.designations import DesignationManager
from db_management.models import Designation, EducationDetail, InstituteStaff, RolesEnum, UserDB
from permission_management.institute_staff_permissions import can_add_education_details_for_staff, can_add_insititute_staff, can_delete_institute_staff, can_disable_education_details_for_staff, can_view_education_details_of_institute_staff, can_view_institute_staff
from .ism_datatypes import DesignationDataTypeForInstituteStaff, EducationDetailDataType, institute_staff_data_type
from permission_management.base_permission import InstituteStaffPermissionJsonType, union_of_all_permission_types
from datetime import datetime
from typing import List, Optional
from tortoise.transactions import atomic
from fastapi.exceptions import HTTPException

router = APIRouter()


@router.post("/addInstituteStaff")
async def add_institute_staff_at_any_level(admin_id: int, username: str, designation: DesignationManager.role_designation_map[RolesEnum.institutestaff], staff_data: institute_staff_data_type, permission_json: InstituteStaffPermissionJsonType, from_time_at_designation: Optional[datetime] = None, token_data: union_of_all_permission_types = Depends(can_add_insititute_staff)):
    created_by_id = token_data.user_id
    from_time = None
    if from_time_at_designation is not None:
        from_time = from_time_at_designation.astimezone("utc")

    @atomic()
    async def add_institute_staff():
        user = await UserDB.filter(username=username).values(
            username="username",
            created_at="created_at",
            updated_at="updated_at",
            user_id="user_id",
            active="active"
        )
        if len(user) != 1:
            raise HTTPException(406, "No user with this username exists.")

        if await Designation.exists(user_id=user[0]["user_id"], active=True):
            raise HTTPException(
                406, "User already assigned to some other role or designation.")

        staff_data_dict = staff_data.dict()
        staff_instance = await InstituteStaff.create(**staff_data_dict, created_by_id=created_by_id, user_id=user[0]["user_id"], admin_id = admin_id)
        designation_instance = await Designation.create(
            role=RolesEnum.institutestaff,
            designation=designation,
            role_instance_id=staff_instance.id,
            user_id=user[0]["user_id"],
            from_time=from_time,
            permissions_json=permission_json.dict()
        )

        designation_data = await Designation.get(id=designation_instance.id).values()
        staff_new_data = await InstituteStaff.get(id=staff_instance.id).values()
        return {
            "user": user[0],
            "staff": staff_new_data,
            "designation": designation_data
        }
    return await add_institute_staff()

@router.get("/allStaffsInInstitute")
async def list_all_active_staffs_of_institute(admin_id: int, token_data: union_of_all_permission_types = Depends(can_view_institute_staff)):
    return await get_list_of_all_staffs_with_designation(admin_id, True)

@router.get("/getStaffData")
async def get_info_about_the_staff(staff_id: int, token_data: union_of_all_permission_types = Depends(can_view_institute_staff)):
    try:
        staff_data = await InstituteStaff.get(id=staff_id).values()
    except:
        raise HTTPException(406, "Institute staff not found for the id.")
    if staff_data["blocked"] or not staff_data["active"]:
        raise HTTPException(406, "Staff has been blocked.")
    try:
        designation = await Designation.get(user_id = staff_data["user_id"], active=True).values()
    except:
        raise HTTPException(406, "No designation found for the user.")
    return {
        "user_personal_data": staff_data,
        "designation_data": designation
    }

@router.put("/editStaffData")
async def edit_staff_data(staff_id: int, admin_id: int, staff_data_in: institute_staff_data_type, token_data: union_of_all_permission_types=Depends(can_add_insititute_staff)):
    await InstituteStaff.filter(id=staff_id).update(**staff_data_in.dict(), created_by_id = token_data.user_id)
    return await InstituteStaff.get(id=staff_id).values()

@router.put("/editDesignationAndPermissionForStaff")
async def edit_designation_data_permission_data_for_staff(designation_id:int, admin_id:int, designation_data: DesignationDataTypeForInstituteStaff, token_data: union_of_all_permission_types = Depends(can_add_insititute_staff)):
    await Designation.filter(id=designation_id).update(
        designation = designation_data.designation,
        permissions_json = designation_data.permissions_json.dict()
    )
    return Designation.filter(id=designation_id)

@router.delete("/disableInstituteStaff")
async def disable_institute_staff_of_given_ids(staff_ids: List[int], admin_id:int, deactivation_reason: Optional[str]=None, token_data: union_of_all_permission_types=Depends(can_delete_institute_staff)):
    await Designation.filter(role=RolesEnum.institutestaff, role_instance_id__in=staff_ids).update(active=False, deactivated_at = datetime.now(), deactivation_reason=deactivation_reason)
    await InstituteStaff.filter(id__in=staff_ids).update(active=False, created_by_id = token_data.user_id)
    return {"success": True}

@router.post("/addEducationDetails")
async def add_education_detail_for_staff(staff_id: int, admin_id: int, education_data: EducationDetailDataType, token_data: union_of_all_permission_types=Depends(can_add_education_details_for_staff)):
    created_education_details_instance = await EducationDetail.create(
        **education_data.dict(),
        institute_staff_id = staff_id,
        updated_by_id = token_data.user_id
    )
    return await EducationDetail.get(id=created_education_details_instance.id).values()

@router.get("/getAllEducationDetailsOfStaff")
async def get_all_educational_qualifications_of_staff(staff_id: int, admin_id: int, token_data: union_of_all_permission_types=Depends(can_view_education_details_of_institute_staff)):
    return await EducationDetail.filter(institute_staff_id = staff_id, active=True).values()

@router.put("/editEducationalDetails")
async def edit_education_details(education_detail_id: int, admin_id: int, education_data: EducationDetailDataType, token_data: union_of_all_permission_types=Depends(can_add_education_details_for_staff)):
    await EducationDetail.filter(id=education_detail_id).update(
        **education_data.dict(),
        updated_by_id = token_data.user_id
    )
    return await EducationDetail.get(id=education_detail_id).values()

@router.delete("/disableEducationDetails")
async def delete_education_details(education_detail_id: int, admin_id: int, token_data: union_of_all_permission_types=Depends(can_disable_education_details_for_staff)):
    await EducationDetail.filter(id=education_detail_id).update(
        active=False,
        updated_by_id = token_data.user_id
    )
    return {"success": True}