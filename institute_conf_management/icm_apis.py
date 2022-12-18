from db_management.models import SubjectGroupDepartment, Subject, SectionSubject, Class, ClassGroupDepartment, ClassSectionSemester, AcademicSessionAndSemester
from fastapi import APIRouter
from permission_management.icm_permissions import can_create_class_group, can_view_class_group, can_view_subject, can_create_subject, can_create_subject_group_department, can_view_subject_group_department
from .icm_datatypes import SubjectGroupDepartMentDataType, SubjectDataType, ClassGroupDataType
from fastapi import Depends
from permission_management.base_permission import union_of_all_permission_types

icm_router = APIRouter()

@icm_router.post("/createNewSubjectDepartMent")
async def create_new_subject_department(
    admin_id: int,
    group_data: SubjectGroupDepartMentDataType,
    token_data: union_of_all_permission_types = Depends(can_create_subject_group_department)
    ):
    updated_by_id = token_data.user_id
    data = group_data.dict()
    data["updated_by_id"]=updated_by_id
    data[admin_id]=admin_id
    created_obj = await SubjectGroupDepartment.create(**data)
    return {
        "group_id": created_obj.group_id,
        "group_name": created_obj.group_name,
        "active": created_obj.active
    }

@icm_router.get("/listAllSubjectGroups")
async def lists_all_active_subject_groups(
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_subject_group_department)
    ):
    return SubjectGroupDepartment.filter(admin_id=admin_id, active=True)

@icm_router.delete("/disableSubjectGroupDepartment")
async def disable_subject_group_department(
    group_id:int,
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(can_create_subject_group_department)
    ):
    await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id).update(active=False, updated_by_id=token_data.user_id)
    return await SubjectGroupDepartment.get(group_id=group_id, admin_id=admin_id).values()

@icm_router.post("/editSubjectGroup")
async def edit_subject_group_data(
    group_id:int,
    admin_id: int,
    group_data: SubjectGroupDepartMentDataType,
    token_data: union_of_all_permission_types = Depends(can_create_subject_group_department)
    ):
    updated_by_id = token_data.user_id
    data = group_data.dict()
    data["updated_by_id"]=updated_by_id
    data[admin_id]=admin_id
    await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id).update(**data)
    return await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id).values()[0]

@icm_router.post("/createNewSubject")
async def add_new_subject_to_given_subject_group(
    group_id: int,
    admin_id: int,
    subject_data: SubjectDataType,
    token_data: union_of_all_permission_types = Depends(can_create_subject)
    ):
    subject_data_dict = subject_data.dict()
    subject_data_dict["subject_group_id"]=group_id
    subject_data_dict["admin_id"]=admin_id
    subject_data_dict["updated_by_id"]=token_data.user_id
    createdobj = await Subject.create(**subject_data_dict)
    return {
        "subject_name": createdobj.subject_name,
        "subject_id": createdobj.subject_id,
        "active": createdobj.active
    }

@icm_router.get("/listAllActiveSubjectsForInsitiute")
async def get_all_active_subjects_for_institute(admin_id:int, token_data: union_of_all_permission_types=Depends(can_view_subject)):
    return await Subject.filter(admin_id=admin_id, active=True, subject_group__active=True).values(
        subject_id="subject_id",
        group_id = "subject_group_id",
        admin_id="admin_id",
        head_id="head_id",
        vice_head_id="vice_head_id"
    )

@icm_router.get("/listAllSubjectsInSubjectGroup")
async def get_all_active_subjects_in_group(admin_id: int, group_id: int, token_data: union_of_all_permission_types=Depends(can_view_subject)):
    subjects = await Subject.filter(subject_group_id=group_id, admin_id=admin_id, active=True, subject_group__active=True).values(
        subject_id="subject_id",
        group_id = "subject_group_id",
        admin_id="admin_id",
        head_id="head_id",
        vice_head_id="vice_head_id"
    )
    return subjects

@icm_router.post("/updateSubject")
async def update_subject_in_given_subject_group(
    subject_id:int,
    group_id: int,
    admin_id: int,
    subject_data: SubjectDataType,
    token_data: union_of_all_permission_types = Depends(can_create_subject)
    ):
    subject_data_dict = subject_data.dict()
    subject_data_dict["subject_group_id"]=group_id
    subject_data_dict["admin_id"]=admin_id
    subject_data_dict["updated_by_id"]=token_data.user_id
    await Subject.filter(subject_id=subject_id).update(**subject_data_dict)
    return await Subject.filter(subject_id=subject_id).values()

@icm_router.delete("/disableSubject")
async def disable_subject_in_given_subject_group(
    subject_id:int,
    token_data: union_of_all_permission_types = Depends(can_create_subject)
    ):
    await Subject.filter(subject_id=subject_id).update(active=False, updated_by_id=token_data.user_id)
    return await Subject.filter(subject_id=subject_id).values()

@icm_router.post("/createNewClassGroup")
async def create_new_class_group(
    admin_id: int,
    group_data: ClassGroupDataType,
    token_data: union_of_all_permission_types = Depends(can_create_class_group)
    ):
    group_data = group_data.dict()
    group_data["admin_id"]=admin_id
    group_data["updated_by_id"]=token_data.user_id
    createdobj = await ClassGroupDepartment.create(**group_data)
    return {
        # "group_name": createdobj.g
    }