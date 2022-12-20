from db_management.models import SubjectGroupDepartment, Subject, SectionSubject, Class, ClassGroupDepartment, ClassSectionSemester, AcademicSessionAndSemester
from fastapi import APIRouter
from permission_management.icm_permissions import can_create_academic_session, can_view_academic_session, can_create_class, can_view_class, can_view_subject, can_create_class_group, can_view_class_group, can_view_subject, can_create_subject, can_create_subject_group_department, can_view_subject_group_department
from .icm_datatypes import AcademicSessionAndSemesterDataTypeInDB, AcademicSessionSemesterDataType, SubjectGroupDepartMentDataType, SubjectDataType, ClassGroupDataType, ClassDataType
from fastapi import Depends
from permission_management.base_permission import union_of_all_permission_types
from fastapi import Body

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
    data[admin_id] = admin_id
    created_obj = await SubjectGroupDepartment.create(**data)
    return {
        "group_id": created_obj.group_id,
        "group_name": created_obj.group_name,
        "active": created_obj.active
    }


@icm_router.get("/listAllSubjectGroups")
async def lists_all_active_subject_groups(
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(
        can_view_subject_group_department)
):
    return SubjectGroupDepartment.filter(admin_id=admin_id, active=True)


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
    data[admin_id] = admin_id
    await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id).update(**data)
    return await SubjectGroupDepartment.filter(group_id=group_id, admin_id=admin_id).values()[0]


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
    createdobj = await Subject.create(**subject_data_dict)
    return {
        "subject_name": createdobj.subject_name,
        "subject_id": createdobj.subject_id,
        "active": createdobj.active
    }


@icm_router.get("/listAllActiveSubjectsForInsitiute")
async def get_all_active_subjects_for_institute(admin_id: int, token_data: union_of_all_permission_types = Depends(can_view_subject)):
    return await Subject.filter(admin_id=admin_id, active=True, subject_group__active=True).values(
        subject_id="subject_id",
        group_id="subject_group_id",
        admin_id="admin_id",
        head_id="head_id",
        vice_head_id="vice_head_id"
    )


@icm_router.get("/listAllSubjectsInSubjectGroup")
async def get_all_active_subjects_in_group(admin_id: int, group_id: int, token_data: union_of_all_permission_types = Depends(can_view_subject)):
    subjects = await Subject.filter(subject_group_id=group_id, admin_id=admin_id, active=True, subject_group__active=True).values(
        subject_id="subject_id",
        group_id="subject_group_id",
        admin_id="admin_id",
        head_id="head_id",
        vice_head_id="vice_head_id"
    )
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
    await Subject.filter(subject_id=subject_id).update(**subject_data_dict)
    return await Subject.filter(subject_id=subject_id).values()


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
    createdobj = await ClassGroupDepartment.create(**data)
    return {
        "group_id": createdobj.group_id,
        "group_name": createdobj.group_name,
        "active": createdobj.active
    }


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
    await ClassGroupDepartment.filter(admin_id=admin_id, group_id=group_id, active=True).update(**data)
    return await ClassGroupDepartment.get(admin_id=admin_id, group_id=group_id, active=True).values(
        admin="admin_id",
        group_id="group_id",
        group_name="group_name",
        head_id="head_id",
        vice_head_id="vice_id"
    )


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
    createdobj = await Class.create(**data)
    await createdobj.subjects.add(await Subject.filter(subject_id__in=subject_ids, active=True))
    return {
        "class_id": createdobj.class_id,
        "class_name": createdobj.class_name,
        "subjects": await createdobj.subjects.all().values()
    }


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
        cls["subjects"] = await sub[0].subjects.all().values()
        cls["subjects"] = filter(lambda x: x["active"], cls["subjects"])
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
        cls["subjects"] = await sub[0].subjects.all().values()
        cls["subjects"] = filter(lambda x: x["active"], cls["subjects"])
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
        cls["subjects"] = await sub[0].subjects.all().values()
        cls["subjects"] = filter(lambda x: x["active"], cls["subjects"])
        classes_with_subjects.append(cls)
    return classes_with_subjects[0]


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
    createdobj = await AcademicSessionAndSemester.create(**data)
    return await AcademicSessionAndSemesterDataTypeInDB.from_queryset_single(await AcademicSessionAndSemester.get(semester_id=createdobj.semester_id))


@icm_router.get("/listAllAcademicSessionsOfInstitute")
async def list_all_academic_sessions_of_the_institute(
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(
        can_view_academic_session)
):
    return await AcademicSessionAndSemester.filter(admin_id=admin_id).values()


@icm_router.get("/getAcademicSession")
async def get_academic_session(
    semester_id: int,
    admin_id: int,
    token_data: union_of_all_permission_types = Depends(
        can_view_academic_session)
):
    return await AcademicSessionAndSemester.get(semester_id=semester_id, admin_id=admin_id).values()


@icm_router.delete("/disableAcademicSession")
async def disable_academic_session(
    semester_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(
        can_create_academic_session)
):
    await AcademicSessionAndSemester.filter(semester_id=semester_id, admin_id=admin_id).update(active=False, updated_by_id=token_data.user_id)
    return {"success": True}