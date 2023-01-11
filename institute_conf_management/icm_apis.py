from db_management.models import AcademicSession, RolesEnum, Designation, SubjectGroupDepartment, Subject, SectionSubject, Class, ClassGroupDepartment, ClassSectionSemester, AcademicSessionAndSemester
from fastapi import APIRouter
from permission_management.icm_permissions import can_create_section,can_view_section,can_create_academic_session, can_view_academic_session, can_create_class, can_view_class, can_view_subject, can_create_class_group, can_view_class_group, can_view_subject, can_create_subject, can_create_subject_group_department, can_view_subject_group_department
from .icm_datatypes import SectionGetDataType, SubjectAdditionDataType, SubjectAdditionOutDataType,ClassSectionSemeseterDataType, ClassSectionSemesterOutDataType,ClassUpdateDataType, AcademicSessionAndSemesterDataTypeInDB, AcademicSessionSemesterDataType, SubjectGroupDepartMentDataType, SubjectDataType, ClassGroupDataType, ClassDataType
from fastapi import Depends
from permission_management.base_permission import union_of_all_permission_types
from fastapi import Body
from tortoise.transactions import atomic
from permission_management.base_permission import InstituteStaffPermissionJsonType, StudentPermissionJsonType
from typing import List
from fastapi.exceptions import HTTPException

icm_router = APIRouter()


@icm_router.post("/createNewSubjectDepartMent")
async def create_new_subject_department(
    group_data: SubjectGroupDepartMentDataType,
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(
        can_create_subject_group_department)
):
    updated_by_id = token_data.user_id
    data = group_data.dict()
    data["updated_by_id"] = updated_by_id
    data["admin_id"] = admin_id

    @atomic()
    async def do():
        created_obj = await SubjectGroupDepartment.create(**data)
        if group_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_subject_groupids.append(created_obj.group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if group_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_subject_groupids.append(created_obj.group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()

        return {
            "group_id": created_obj.group_id,
            "group_name": created_obj.group_name,
            "active": created_obj.active
        }
    return await do()


@icm_router.get("/listAllSubjectGroups")
async def lists_all_active_subject_groups(
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(
        can_view_subject_group_department)
):
    return await SubjectGroupDepartment.filter(admin_id=admin_id, active=True).values()


@icm_router.delete("/disableSubjectGroupDepartment")
async def disable_subject_group_department(
    group_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(
        can_create_subject_group_department)
):
    await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id).update(active=False, updated_by_id=token_data.user_id)
    return {"success": True}


@icm_router.post("/editSubjectGroup")
async def edit_subject_group_data(
    group_data: SubjectGroupDepartMentDataType,
    group_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(
        can_create_subject_group_department)
):
    updated_by_id = token_data.user_id
    data = group_data.dict()
    data["updated_by_id"] = updated_by_id
    data["admin_id"] = admin_id

    @atomic()
    async def do():
        subject_group=await SubjectGroupDepartment.get(
            group_id=group_id, admin_id=admin_id,active=True
            ).values(
                head_id="head_id",
                vice_head_id="vice_head_id"
            )
        cnt_head = subject_group["head_id"]
        if cnt_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if group_id in permissions_json.head_of_subject_groupids:
                permissions_json.head_of_subject_groupids.remove(group_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()
        cnt_vice_head = subject_group["vice_head_id"]
        if cnt_vice_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_vice_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if group_id in permissions_json.vice_head_of_subject_groupids:
                permissions_json.vice_head_of_subject_groupids.remove(group_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()

        await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id,active=True).update(**data)
        if group_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_subject_groupids.append(group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if group_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_subject_groupids.append(group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        return await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id,active=True).values()
    return await do()

@icm_router.post("/createNewSubject")
async def add_new_subject_to_given_subject_group(
    subject_data: SubjectDataType,
    group_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_subject)
):
    subject_data_dict = subject_data.dict()
    subject_data_dict["subject_group_id"] = group_id
    subject_data_dict["admin_id"] = admin_id
    subject_data_dict["updated_by_id"] = token_data.user_id

    @atomic()
    async def do():
        createdobj = await Subject.create(**subject_data_dict)
        if subject_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=subject_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_subject_ids.append(createdobj.subject_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if subject_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=subject_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_subject_ids.append(createdobj.subject_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()

        return {
        "subject_name": createdobj.subject_name,
        "subject_id": createdobj.subject_id,
        "active": createdobj.active
    }
    return await do()


@icm_router.get("/listAllActiveSubjectsForInsitiute")
async def get_all_active_subjects_for_institute(admin_id: int, token_data: union_of_all_permission_types = Depends(can_view_subject)):
    return await Subject.filter(admin_id=admin_id, active=True, subject_group__active=True).values()


@icm_router.get("/listAllSubjectsInSubjectGroup")
async def get_all_active_subjects_in_group(admin_id: int, group_id: int, token_data: union_of_all_permission_types = Depends(can_view_subject)):
    subjects = await Subject.filter(subject_group_id=group_id, admin_id=admin_id, active=True, subject_group__active=True).values()
    return subjects


@icm_router.post("/updateSubject")
async def update_subject_in_given_subject_group(
    subject_data: SubjectDataType,
    subject_id: int = Body(embed=True),
    group_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_subject)
):
    subject_data_dict = subject_data.dict()
    subject_data_dict["subject_group_id"] = group_id
    subject_data_dict["admin_id"] = admin_id
    subject_data_dict["updated_by_id"] = token_data.user_id

    @atomic()
    async def do():
        subject=await Subject.get(
            subject_id=subject_id,admin_id=admin_id,active=True
            ).values(
                head_id="head_id",
                vice_head_id="vice_head_id"
            )
        cnt_head = subject["head_id"]
        if cnt_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if subject_id in permissions_json.head_of_subject_ids:
                permissions_json.head_of_subject_ids.remove(subject_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()
        cnt_vice_head = subject["vice_head_id"]
        if cnt_vice_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_vice_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if subject_id in permissions_json.vice_head_of_subject_ids:
                permissions_json.vice_head_of_subject_ids.remove(subject_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()

        await Subject.filter(subject_id=subject_id, admin_id=admin_id,active=True).update(**subject_data_dict)
        if subject_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=subject_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_subject_ids.append(subject_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if subject_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=subject_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_subject_ids.append(subject_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        return await Subject.filter(subject_id=subject_id, admin_id=admin_id,active=True).values()
    return await do()


@icm_router.delete("/disableSubject")
async def disable_subject_in_given_subject_group(
    subject_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_subject)
):
    await Subject.filter(subject_id=subject_id).update(active=False, updated_by_id=token_data.user_id)
    return {"success": True}


@icm_router.post("/createNewClassGroup")
async def create_new_class_group(
    group_data: ClassGroupDataType,
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_class_group)
):
    data = group_data.dict()
    data["admin_id"] = admin_id
    data["updated_by_id"] = token_data.user_id


    @atomic()
    async def do():
        created_obj = await ClassGroupDepartment.create(**data)
        if group_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_class_groupids.append(created_obj.group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if group_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_class_groupids.append(created_obj.group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()

        return {
            "group_id": created_obj.group_id,
            "group_name": created_obj.group_name,
            "active": created_obj.active
        }
    return await do()


@icm_router.get("/listAllClassGroupDepartments")
async def list_all_active_class_group_departments(
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_class_group)
):
    await ClassGroupDepartment.filter(admin_id=admin_id).values()


@icm_router.post("/editClassGroupDepartment")
async def edit_class_group_department(
    group_data: ClassGroupDataType,
    admin_id: int = Body(embed=True),
    group_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_view_class_group)
):
    data = group_data.dict()
    data["updated_by_id"] = token_data.user_id

    @atomic()
    async def do():
        subject_group=await ClassGroupDepartment.get(
            group_id=group_id, admin_id=admin_id,active=True
            ).values(
                head_id="head_id",
                vice_head_id="vice_head_id"
            )
        cnt_head = subject_group["head_id"]
        if cnt_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if group_id in permissions_json.head_of_class_groupids:
                permissions_json.head_of_class_groupids.remove(group_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()
        cnt_vice_head = subject_group["vice_head_id"]
        if cnt_vice_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_vice_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if group_id in permissions_json.vice_head_of_class_groupids:
                permissions_json.vice_head_of_class_groupids.remove(group_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()

        await ClassGroupDepartment.filter(group_id=group_id, admin_id=admin_id,active=True).update(**data)
        if group_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_class_groupids.append(group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if group_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=group_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_class_groupids.append(group_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        return await ClassGroupDepartment.filter(group_id=group_id, admin_id=admin_id,active=True).values(
            admin="admin_id",
            group_id="group_id",
            group_name="group_name",
            head_id="head_id",
            vice_head_id="vice_id"
        )
    return await do()

@icm_router.delete("/disableClassGroupDepartment")
async def disable_class_group_department(
    admin_id: int = Body(embed=True),
    group_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_class_group)
):
    await ClassGroupDepartment.filter(admin_id=admin_id, group_id=group_id).update(active=False, updated_by_id=token_data.user_id)
    return {"success": True}


@icm_router.post("/createNewClass")
async def create_new_class(
    class_data: ClassDataType,
    class_group_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_class)
):
    data = class_data.dict()
    subject_ids = data["subject_ids"]
    del data["subject_ids"]
    data["class_group_id"] = class_group_id
    data["admin_id"] = admin_id
    data["updated_by_id"] = token_data.user_id
    @atomic()
    async def do():
        createdobj = await Class.create(**data)
        subjects = await Subject.filter(subject_id__in=subject_ids, active=True)
        for subject in subjects:
            await createdobj.subjects.add(subject)
        if class_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=class_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_class_ids.append(createdobj.class_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if class_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=class_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_class_ids.append(createdobj.class_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()

        return {
        "class_name": createdobj.class_name,
        "class_id": createdobj.class_id,
        "active": createdobj.active
    }
    return await do()

@icm_router.get("/listAllClassesInInstitute")
async def list_all_classes_of_institute(
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_class)
):
    classes = await Class.filter(admin_id=admin_id, active=True).values(
        class_id="class_id",
        class_name="class_name",
        class_group_id="class_group_id",
        head_id="head_id",
        vice_head_id="vice_head_id",
        admin_id="admin_id"
    )
    classes_with_subjects = []
    for cls in classes:
        class_id = cls["class_id"]
        sub = await Class.filter(class_id=class_id)
        cls["subjects"] = await sub[0].subjects.filter(active=True).values()
        classes_with_subjects.append(cls)
    return classes_with_subjects


@icm_router.get("/listAllClassesInClassGroup")
async def list_all_classes_of_class_group(
    admin_id: int,
    class_group_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_class)
):
    classes = await Class.filter(admin_id=admin_id, class_group_id=class_group_id, active=True).values(
        class_id="class_id",
        class_name="class_name",
        class_group_id="class_group_id",
        head_id="head_id",
        vice_head_id="vice_head_id",
        admin_id="admin_id"
    )
    classes_with_subjects = []
    for cls in classes:
        class_id = cls["class_id"]
        sub = await Class.filter(class_id=class_id)
        cls["subjects"] = await sub[0].subjects.all(active=True).values()
        classes_with_subjects.append(cls)
    return classes_with_subjects


@icm_router.get("/getClassData")
async def get_class_data(
    admin_id: int,
    class_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_class)
):
    classes = await Class.filter(admin_id=admin_id, class_id=class_id, active=True).values(
        class_id="class_id",
        class_name="class_name",
        class_group_id="class_group_id",
        head_id="head_id",
        vice_head_id="vice_head_id",
        admin_id="admin_id"
    )
    classes_with_subjects = []
    for cls in classes:
        class_id = cls["class_id"]
        sub = await Class.filter(class_id=class_id)
        cls["subjects"] = await sub[0].subjects.filter(active=True).values()
        classes_with_subjects.append(cls)
    return classes_with_subjects[0]

@icm_router.post("/updateClassData")
async def update_subject_in_given_class_data(
    subject_data: ClassUpdateDataType,
    class_id: int = Body(embed=True),
    group_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_class)
):
    data = subject_data.dict()
    data["group_id"] = group_id
    data["admin_id"] = admin_id
    data["updated_by_id"] = token_data.user_id

    @atomic()
    async def do():
        subject=await Class.get(
            class_id=class_id,admin_id=admin_id,active=True
            ).values(
                head_id="head_id",
                vice_head_id="vice_head_id"
            )
        cnt_head = subject["head_id"]
        if cnt_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if class_id in permissions_json.head_of_class_ids:
                permissions_json.head_of_class_ids.remove(class_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()
        cnt_vice_head = subject["vice_head_id"]
        if cnt_vice_head is not None:
            cnt_designation = await Designation.get(role_instance_id=cnt_vice_head,role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**cnt_designation.permissions_json)
            if class_id in permissions_json.vice_head_of_class_ids:
                permissions_json.vice_head_of_class_ids.remove(class_id)
            cnt_designation.permissions_json=permissions_json.dict()
            await cnt_designation.save()

        await Class.filter(subject_id=class_id, admin_id=admin_id,active=True).update(**data)
        if subject_data.head_id is not None:
            head_designation = await Designation.get(role_instance_id=subject_data.head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.head_of_subject_ids.append(class_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if subject_data.vice_head_id is not None:
            head_designation = await Designation.get(role_instance_id=subject_data.vice_head_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_head_of_subject_ids.append(class_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        return await Class.filter(class_id=class_id, admin_id=admin_id,active=True).values()
    return await do()

@icm_router.post("addNewSubjectsInClass")
async def add_subjects_in_a_particular_class(
    subject_ids: List[int]=Body(embed=True,default=[]),
    class_id: int=Body(embed=True),
    admin_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_create_class)
):
    classobj = await Class.get(class_id=class_id, admin_id=admin_id,active=True)
    subjects = await Subject.filter(subject_id__in=subject_ids, active=True)
    for subject in subjects:
        await classobj.subjects.add(subject)
    return {"subjects": await classobj.subjects.all().values()}

@icm_router.post("/removeSubjectsFromClass")
async def remove_subjects_from_class(
    subject_ids: List[int]=Body(embed=True, default=[]),
    class_id: int=Body(embed=True),
    admin_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_create_class)
):
    classobj = await Class.get(class_id=class_id, admin_id=admin_id,active=True)
    subjects = await Subject.filter(subject_id__in=subject_ids, active=True)
    for subject in subjects:
        await classobj.subjects.remove(subjects)
    return {"subjects": await classobj.subjects.all().values()}

@icm_router.delete("/disableClass")
async def disable_class_for_given_id(
    class_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_class)
):
    await Class.filter(class_id=class_id, admin_id=admin_id).update(active=False, updated_by_id=token_data.user_id)
    return {"success": True}


@icm_router.post("/addNewAcademicSessionAndSemester")
async def add_new_academic_session_and_semester(
    session_data: AcademicSessionSemesterDataType,
    admin_id: int = Body(embed=True, description="Admin ID which should be positive integer."),
    token_data: union_of_all_permission_types = Depends(
        can_create_academic_session)
):
    data = session_data.dict()
    data["admin_id"] = admin_id
    data["updated_by_id"] = token_data.user_id
    data1 = {**data}
    del data1["semester_start_date"]
    del data1["semester_end_data"]
    del data1["semester_number"]
    del data["academic_session_start_year"]
    del data["academic_session_end_year"]
    @atomic()
    async def do():
        session_obj = await AcademicSession.create(**data1)
        semesterobj = await AcademicSessionAndSemester.create(**data, session_id=session_obj.session_id)
        return {
            "session_details": {
                "session_id": session_obj.session_id,
                "academic_session_start_year": session_obj.academic_session_start_year,
                "academic_session_end_year": session_obj.academic_session_end_year,
                "current": session_obj.current
            },
            "semester_details": {
                "semester_id": semesterobj.semester_id,
                "semester_number": semesterobj.semester_number,
                "semester_start_date": semesterobj.semester_start_date,
                "semester_end_date": semesterobj.semester_end_date,
                "current": semesterobj.current
            }
        }
    return await do()

import datetime
from typing import Optional

@icm_router.post("/createNewSemester")
async def create_new_semester(
    session_id: int=Body(embed=True),
    admin_id: int=Body(embed=True),
    semester_number: int=Body(embed=True),
    semster_start_date: Optional[datetime.datetime]=Body(embed=True, default=None),
    semester_end_date: Optional[datetime.datetime]=Body(embed=True, default=None),
    token_data: union_of_all_permission_types=Depends(can_create_academic_session)
):
    @atomic()
    async def do():
        await AcademicSessionAndSemester.filter(
            session_id=session_id, admin_id=admin_id).update(
                current=False,
                updated_by_id=token_data.user_id
            )
        semesterobj = await AcademicSessionAndSemester.create(
            session_id=session_id,
            admin_id=admin_id,
            semester_end_date=semester_end_date,
            semester_number=semester_number,
            semster_start_date=semster_start_date,
            current=True
        )
        return {
            "semester_id": semesterobj.semester_id,
            "semester_number": semesterobj.semester_number,
            "semester_start_date": semesterobj.semester_start_date,
            "semester_end_date": semesterobj.semester_end_date,
            "current": semesterobj.current
        }
    return await do()

@icm_router.get("/listAllAcademicSessionsOfInstitute")
async def list_all_academic_sessions_of_the_institute(
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(
        can_view_academic_session)
):
    return await AcademicSessionAndSemester.filter(admin_id=admin_id).values()


@icm_router.get("/getAcademicSession")
async def get_academic_session(
    session_id: int,
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(
        can_view_academic_session)
):
    session_obj = await AcademicSession.get(
        session_id=session_id, admin_id=admin_id, active=True).prefetch_related("semesters")
    semesters = await session_obj.semester.filter(active=True).values()
    return {
        "session": {
                "session_id": session_obj.session_id,
                "academic_session_start_year": session_obj.academic_session_start_year,
                "academic_session_end_year": session_obj.academic_session_end_year,
                "current": session_obj.current
            },
        "semesters": semesters
    }

@icm_router.delete("/disableAcademicSession")
async def disable_academic_session(
    session_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(
        can_create_academic_session)
):
    await AcademicSession.filter(session_id=session_id, admin_id=admin_id).update(
        active=False, updated_by_id=token_data.user_id)
    await AcademicSessionAndSemester.filter(session_id=session_id, admin_id=admin_id).update(
        active=False, updated_by_id=token_data.user_id)
    return {"success": True}

@icm_router.post("/addNewClassSection", response_model=ClassSectionSemesterOutDataType)
async def add_new_class_section(
    section_data: ClassSectionSemeseterDataType,
    school_class_id: int=Body(embed=True),
    admin_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_create_section)
):
    data = section_data.dict()
    data["admin_id"]=admin_id
    data["school_class_id"]=school_class_id
    data["updated_by_id"]=token_data.user_id
    if await ClassSectionSemester.exists(
        school_class_id=school_class_id,
        section_name=section_data.section_name,
        active=True,
        semester_id=section_data.semester_id
        ):
        raise HTTPException(409, "Section Already Exists.")
    @atomic()
    async def do():
        createdobj = await ClassSectionSemester.create(**data)
        if section_data.class_teacher_id is not None:
            head_designation = await Designation.get(role_instance_id=section_data.class_teacher_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.class_teacher_of_section_ids.append(createdobj.section_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if section_data.vice_class_teacher_id is not None:
            head_designation = await Designation.get(role_instance_id=section_data.vice_class_teacher_id, role=RolesEnum.institutestaff)
            permissions_json = InstituteStaffPermissionJsonType(**head_designation.permissions_json)
            permissions_json.vice_class_teacher_of_section_ids.append(section_data.vice_class_teacher_id)
            head_designation.permissions_json=permissions_json.dict()
            await head_designation.save()
        if section_data.class_monitor_id is not None:
            designation = await Designation.get(role_instance_id=section_data.class_monitor_id, role=RolesEnum.student, active=True)
            permissions_json = StudentPermissionJsonType(**designation.permissions_json)
            permissions_json.is_class_monitor=True
            designation.permissions_json = permissions_json.dict()
            await designation.save()
        if section_data.vice_class_monitor_id is not None:
            designation = await Designation.get(role_instance_id=section_data.vice_class_monitor_id, role=RolesEnum.student, active=True)
            permissions_json = StudentPermissionJsonType(**designation.permissions_json)
            permissions_json.is_vice_class_monitor=True
            designation.permissions_json = permissions_json.dict()
            await designation.save()
        createdobjdata = await ClassSectionSemester.filter(section_id=createdobj.section_id).values()
        return createdobjdata[0]
    return do()

@icm_router.get("/listAllSectionsOfClass", response_model=List[ClassSectionSemesterOutDataType])
async def list_all_sections_of_a_class(
    school_class_id: int,
    admin_id: int,
    token_data: union_of_all_permission_types= Depends(can_view_section)
):
    return await ClassSectionSemester.filter(
        school_class_id=school_class_id, admin_id=admin_id, active=True
    ).values()

@icm_router.put("/editClassSection", response_model=ClassSectionSemesterOutDataType)
async def edit_class_section_data(
    section_data: ClassSectionSemeseterDataType,
    section_id: int=Body(embed=True),
    admin_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_create_section)
):  
    data = section_data.dict()
    data["updated_by_id"]=token_data.user_id
    @atomic()
    async def do():
        olddata = await ClassSectionSemester.get(section_id=section_id, admin_id=admin_id, active=True).values()
        if section_data.class_teacher_id != olddata["class_teacher_id"]:
            if olddata["class_teacher_id"] is not None:
                olddesignation = await Designation.get(role_instance_id=olddata["class_teacher_id"], role=RolesEnum.institutestaff)
                oldpermissions = InstituteStaffPermissionJsonType(**olddesignation.permissions_json)
                if section_id in oldpermissions.class_teacher_of_section_ids:
                    oldpermissions.class_teacher_of_section_ids.remove(section_id)
                olddesignation.permissions_json = oldpermissions.dict()
                await olddesignation.save()
            if section_data.class_teacher_id is not None:
                designation = await Designation.get(role_instance_id=section_data.class_teacher_id, role=RolesEnum.institutestaff)
                permissions = InstituteStaffPermissionJsonType(**designation.permissions_json)
                permissions.class_teacher_of_section_ids.append(section_id)
                designation.permissions_json = permissions.dict()
                await designation.save()
        if section_data.vice_class_teacher_id != olddata["vice_class_teacher_id"]:
            if olddata["vice_class_teacher_id"] is not None:
                olddesignation = await Designation.get(role_instance_id=olddata["vice_class_teacher_id"], role=RolesEnum.institutestaff)
                oldpermissions = InstituteStaffPermissionJsonType(**olddesignation.permissions_json)
                if section_id in oldpermissions.vice_class_teacher_of_section_ids:
                    oldpermissions.vice_class_teacher_of_section_ids.remove(section_id)
                olddesignation.permissions_json = oldpermissions.dict()
                await olddesignation.save()
            if section_data.vice_class_teacher_id is not None:
                designation = await Designation.get(role_instance_id=section_data.vice_class_teacher_id, role=RolesEnum.institutestaff)
                permissions = InstituteStaffPermissionJsonType(**designation.permissions_json)
                permissions.vice_class_teacher_of_section_ids.append(section_id)
                designation.permissions_json = permissions.dict()
                await designation.save()
        if section_data.class_monitor_id != olddata["class_monitor_id"]:
            if olddata["class_monitor_id"] is not None:
                olddesignation = await Designation.get(role_instance_id=olddata["class_monitor_id"], role=RolesEnum.student)
                oldpermissions = StudentPermissionJsonType(**olddesignation.permissions_json)
                oldpermissions.is_class_monitor=False
                olddesignation.permissions_json = oldpermissions.dict()
                await olddesignation.save()
            if section_data.class_monitor_id is not None:
                designation = await Designation.get(role_instance_id=section_data.class_monitor_id, role=RolesEnum.student)
                permissions = StudentPermissionJsonType(**designation.permissions_json)
                permissions.is_class_monitor=True
                designation.permissions_json = permissions.dict()
                await designation.save()
        if section_data.vice_class_monitor_id != olddata["vice_class_monitor_id"]:
            if olddata["vice_class_monitor_id"] is not None:
                olddesignation = await Designation.get(role_instance_id=olddata["vice_class_monitor_id"], role=RolesEnum.student)
                oldpermissions = StudentPermissionJsonType(**olddesignation.permissions_json)
                oldpermissions.is_vice_class_monitor=False
                olddesignation.permissions_json = oldpermissions.dict()
                await olddesignation.save()
            if section_data.vice_class_monitor_id is not None:
                designation = await Designation.get(role_instance_id=section_data.vice_class_monitor_id, role=RolesEnum.student)
                permissions = StudentPermissionJsonType(**designation.permissions_json)
                permissions.is_vice_class_monitor=True
                designation.permissions_json = permissions.dict()
                await designation.save()
        await ClassSectionSemester.filter(section_id=section_id, admin_id=admin_id, active=True).update(**data)
        updateddata = await ClassSectionSemester.filter(section_id=section_id, admin_id=admin_id, active=True).values()
        if len(updateddata)==0:
            raise HTTPException(406, "section_id is not valid.")
        return updateddata[0]
    return await do()

@icm_router.post("/addSubjectTeachersToClassSection", response_model=SubjectAdditionOutDataType)
async def add_subjects_to_class_section(
    subject_data: List[SubjectAdditionDataType],
    admin_id: int = Body(embed=True),
    section_id: int=Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_create_section)
):
    for sub in subject_data:
        data = sub.dict()
        data["updated_by_id"]=token_data.user_id
        subject_id = sub.subject_id
        del data["subject_id"]
        data["active"]=True
        await SectionSubject.update_or_create(
            defaults=data,
            subject_id=subject_id,
            section_id=section_id
        )
    allsubjects = await SectionSubject.filter(section_id=section_id, active=True).values()
    return {"section_id": section_id, "subjects": allsubjects}

@icm_router.get("/getSectionData", response_model=SectionGetDataType)
async def get_class_section_data(
    section_id: int,
    admin_id: int,
    token_data: union_of_all_permission_types=Depends(can_view_section)
):
    class_section_data = await ClassSectionSemester.get(
        section_id=section_id,
        admin_id=admin_id,
        active=True
    ).prefetch_related("subjects")
    subjects = await class_section_data.subjects.filter(active=True).values()
    return {
        **class_section_data.__dict__,
        "subjects": subjects
    }