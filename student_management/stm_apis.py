from fastapi import APIRouter, Body, Depends
from permission_management.base_permission import (union_of_all_permission_types,
                                                   StudentPermissionJsonType, ParentGaurdianPermissionJsonType)
from db_management.designations import DesignationManager
from db_management import models
from .stm_datatypes import (ParentGaurdianCreateDataTypeOut, ParentGaurdianGetDataTypeOut,
                            ParentGaurdianDatatype, StudentDataType, CreateStudentOutDataType,
                            StudentDataTypeOut, StudentClassSectionDataType, StudentWithParentDataTypeOut)
from permission_management.student_permissions import (can_add_student, can_view_list_of_students,
                                                       can_view_student)
from typing import List, Optional
from fastapi.exceptions import HTTPException
from db_management.designations import DesignationManager
import datetime
from tortoise.transactions import atomic
from auth.auth_logic import create_password_from_dob
from typing import List
from project.shared.common_datatypes import SuccessReponse
from permission_management.base_permission import StudentPermissionJsonType
from db_management.db_enums import GaurdianTypeEnum

router = APIRouter()


@router.post("/addNewStudent", response_model=CreateStudentOutDataType)
async def add_new_student(
    student_data: StudentDataType,
    username: str = Body(embed=True),
    admin_id: int = Body(embed=True),
    section_id: int = Body(embed=True),
    subject_ids: List[int] = Body(default=[], embed=True, description="Subject IDs of subjects available in class section."),
    designation: DesignationManager.role_designation_map["student"] = Body(embed=True),
    designation_start_time: Optional[datetime.datetime] = Body(default=None, embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_student)
):
    available_subjects = set(await models.SectionSubject.filter(
        section_id=section_id,
        admin_id=admin_id,
        active=True).values_list("subject_id", flat=True))
    set_subject_ids = set(subject_ids)
    if len(set_subject_ids.difference(available_subjects)) > 0:
        raise HTTPException(406, {"detail": "Invalid Subject IDs.",
                            "subject_ids": set_subject_ids.difference(available_subjects)})

    if await models.UserDB.exists(username=username):
        raise HTTPException(406, "User already exists.")

    @atomic()
    async def do():
        dob = student_data.date_of_birth
        password, hashed_password = create_password_from_dob(dob)
        user = await models.UserDB.create(username=username, password=hashed_password)
        student = await models.Student.create(
            user_id=user.user_id, **student_data.dict(), updated_by_id=token_data.user_id, admin_id=admin_id
        )
        designationobj = await models.Designation.create(
            designation=designation,
            user_id=user.user_id,
            role=models.RolesEnum.student,
            role_instance_id=student.id,
            from_time=designation_start_time,
            permissions_json=StudentPermissionJsonType().dict()
        )

        subjects = await models.SectionSubject.filter(subject_id__in=set_subject_ids, section_id=section_id)
        student_sem_details = await models.StudentSememster.create(
            student_id=student.id,
            section_id=section_id,
            admin_id=admin_id
        )
        for subject in subjects:
            await student_sem_details.subjects.add(subject)
        return {
            "login_credentials": {"username": user.username, "password": password},
            "student_data": student.__dict__,
            "section_id": section_id,
            "subjects": list(set_subject_ids),
            "designation_data": designationobj.__dict__
        }
    return await do()


@router.get("/listAllStudentsOfClassSection", response_model=List[StudentDataTypeOut])
async def list_all_students_studying_in_given_section(
    admin_id: int,
    section_id: int,
    current: Optional[bool] = True,
    semester_id: Optional[int] = None,
    token_data: union_of_all_permission_types = Depends(
        can_view_list_of_students)
):
    '''
    If current is True, it will fetch all students of section of current semester. Else given semester id will be used.
    '''
    if not current and not semester_id:
        raise HTTPException(
            406, "current and semester id both can not be negative.")
    if current:
        student_class = await models.ClassSectionSemester.get(
            section_id=section_id, admin_id=admin_id, active=True, semester__current=True
        ).prefetch_related('students_of_class')
    else:
        student_class = await models.ClassSectionSemester.get(
            section_id=section_id, admin_id=admin_id, active=True, semester_id=semester_id
        ).prefetch_related('students_of_class')

    student_ids = await student_class.students_of_class.filter(active=True).values_list('student_id', flat=True)
    return await models.Student.filter(id__in=list(student_ids), active=True).values()


@router.get("/getStudentData", response_model=StudentDataTypeOut)
async def get_student_data(
    student_id: int,
    token_data: union_of_all_permission_types = Depends(can_view_student)
):
    return await models.Student.get(id=student_id, active=True, blocked=False).values()


@router.put("/updateStudentProfileData", response_model=StudentDataTypeOut)
async def update_student_profile_data(
    student_data: StudentDataType,
    student_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_student)
):
    await models.Student.filter(id=student_id, admin_id=admin_id, active=True, blocked=False).update(
        **student_data.dict(),
        updated_by_id=token_data.user_id
    )
    return await models.Student.filter(id=student_id, admin_id=admin_id, active=True, blocked=False).values()


@router.delete("/disableStudent", response_model=SuccessReponse)
async def disable_student(
    student_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_student)
):
    await models.Student.filter(id=student_id, admin_id=admin_id).update(
        active=False,
        updated_by_id=token_data.user_id
    )


@router.post("/changeClassOrSectionOfStudent", response_model=StudentClassSectionDataType)
async def change_class_or_section_of_student(
    section_data: StudentClassSectionDataType,
    student_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_student)
):
    '''
    This API will have different effects in different scenarios.
    1) Switching classes or sections within semesters will just update and old record will not be saved.
    2) Switch classes or sections across semesters or academic sessions will hold old data in db and create new one.

    It will replace the old subjects by new one. So pass all the subjects which student need to have.
    '''
    current_sem = await models.ClassSectionSemester.filter(
        section_id=section_data.section_id, active=True).values(semester_id="semester_id")
    to_be_sem = await models.StudentSememster.filter(
        student_id=student_id,
        section_id=section_data.section_id, active=True
    ).values(
        semester_id="section__semester_id"
    )
    if len(to_be_sem) == 0:
        raise HTTPException(406, "Wrong section id given.")

    session_change = False
    if len(current_sem) > 0 and current_sem[0]["semeter_id"] != to_be_sem[0]["semester_id"]:
        session_change = True

    @atomic()
    async def do():
        if session_change:
            await models.StudentSememster.filter(
                section_id=section_data.section_id,
                student_id=student_id,
                active=True
            ).update(active=False, updated_by_id=token_data.user_id)
            student_sem = await models.StudentSememster.create(
                student_id=student_id,
                section_id=section_data.section_id,
                admin_id=admin_id
            )
        else:
            student_sem = await models.StudentSememster.get(
                student_id=student_id,
                section_id=section_data.section_id,
                admin_id=admin_id,
                active=True)
            student_sem.update_from_dict(
                {"section_id": section_data.section_id, "updated_by_id": token_data.user_id})
            await student_sem.save()
            await student_sem.subjects.clear()

        # Fetching all the objects from
        subjects = await models.SectionSubject.filter(
            section_id=section_data.section_id, subject_id__in=section_data.subject_ids, active=True
        ).prefetch_related("subject")
        await student_sem.subjects.add(*subjects)

        designation_data = await models.Designation.get(
            role_instance_id=student_id, role=models.RolesEnum.student, active=True)

        permission_json = StudentPermissionJsonType(
            **designation_data.permissions_json)
        permission_json.is_class_monitor = False
        permission_json.is_vice_class_monitor = False
        designation_data.permissions_json = permission_json.dict()
        await designation_data.save()
        return {"section_id": section_data.section_id, "subject_ids": [x.subject.subject_id for x in subjects]}

    return await do()


@router.post("/addOrRemoveSubjectForStudent", response_model=StudentClassSectionDataType)
async def add_or_remove_subject_for_student(
    student_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    add_subject_ids: List[int] = Body(default=[], embed=True),
    remove_subject_ids: List[int] = Body(default=[], embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_student)
):
    student_sem = await models.StudentSememster.get(
        student_id=student_id,
        admin_id=admin_id,
        active=True,
        section__semester__current=True
    ).prefetch_related("section")
    section_id = student_sem.section.section_id
    to_add_subs = await models.SectionSubject.filter(
        section_id=section_id, subject_id__in=add_subject_ids, active=True)
    to_remove_subs = await models.SectionSubject.filter(
        section_id=section_id, subject_id__in=remove_subject_ids, active=True)
    if to_remove_subs != []:
        await student_sem.subjects.remove(*to_remove_subs)
    if to_add_subs != []:
        await student_sem.subjects.add(*to_add_subs)
    return {
        "section_id": student_sem.section.section_id,
        "subject_ids": (await models.SectionSubject.filter(
            section_id=section_id, active=True).values_list("subject_id", flat=True))
    }


@router.post("/addParentOrGaurdian", response_model=ParentGaurdianCreateDataTypeOut)
async def add_parent_of_gaurdian_data(
    parent_data: ParentGaurdianDatatype,
    gaurdian_type: GaurdianTypeEnum = Body(embed=True),
    student_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    relation_with_kid: Optional[str] = Body(default=None, embed=True),
    token_data: union_of_all_permission_types = Depends(can_add_student)
):
    '''
    In case of other gaurdian type, pass relation_with_kid i.e. brother, uncle etc.
    In case of adding new gaurdian, it will replace the old gaurdian.
    prename: Mr., Mrs., Ms., Late
    '''
    if gaurdian_type == GaurdianTypeEnum.other and (relation_with_kid is None or not parent_data.is_gaurdian):
        raise HTTPException(406, "Please pass relation_with_kid")
    student_obj = await models.Student.get(id=student_id, admin_id=admin_id, active=True).prefetch_related(
        "father", "mother", "gaurdian"
    )
    if await student_obj.father is not None and gaurdian_type == GaurdianTypeEnum.father:
        raise HTTPException(406, "Father Data has already been added.")
    if await student_obj.mother is not None and gaurdian_type == GaurdianTypeEnum.mother:
        raise HTTPException(406, "Mother Data has already been added.")

    @atomic()
    async def do():
        password = None
        username = None
        parent_obj = await models.ParentGaurdian.create(**parent_data.dict(), updated_by_id=token_data.user_id)
        if await student_obj.gaurdian is not None and parent_data.is_gaurdian:
            try:
                old_designation = await models.Designation.get(
                    role_instance_id = await student_obj.gaurdian.id,
                    role = models.RolesEnum.parentgaurdian,
                    active=True
                )
                permissions_json_old:ParentGaurdianPermissionJsonType = old_designation.permissions_json
                gaurdee_students = []
                for i, stdt in enumerate(permissions_json_old.gaurdee_students):
                    if stdt.student_id!=i:
                        gaurdee_students.append(stdt)
                permissions_json_old.gaurdee_students = gaurdee_students
                old_designation.permissions_json=permissions_json_old.dict()
                await old_designation.save()
                gaurdian = await student_obj.gaurdian
                gaurdian.is_gaurdian=False
                await gaurdian.save()
            except:
                pass

        if parent_data.is_gaurdian:
            users = await models.UserDB.filter(username=parent_data.phone_number.strip(), active=True)
            if len(users) == 0:
                dob = parent_data.date_of_birth
                password, hashed_password= create_password_from_dob(dob)
                username = parent_data.phone_number.strip()
                user = await models.UserDB.create(username=username, password=hashed_password)
                permission_json=ParentGaurdianPermissionJsonType()
                student_data = await models.Student.filter(id=student_id, admin_id=admin_id, active=True).values(
                    admin_id="admin_id",
                    super_admin_id="admin__super_admin_id",
                    student_id="id",
                    first_name="first_name",
                    middle_name="middle_name",
                    last_name="last_name"
                )
                permission_json.gaurdee_students.append(student_data[0])
                await models.Designation.create(
                    user_id=user.user_id,
                    role=models.RolesEnum.parentgaurdian,
                    role_instance_id=parent_obj.id,
                    designation=DesignationManager.role_designation_map[models.RolesEnum.parentgaurdian].gaurdian,
                    permissions_json=permission_json.dict()
                )
            else:
                user = users[0]
                designation_data=await models.Designation.get(
                    user_id=user.id,
                    role=models.RolesEnum.parentgaurdian,
                    active=True
                )
                student_data = await models.Student.filter(id=student_id, admin_id=admin_id, active=True).values(
                    admin_id="admin_id",
                    super_admin_id="admin__super_admin_id",
                    student_id="id",
                    first_name="first_name",
                    middle_name="middle_name",
                    last_name="last_name"
                )
                designation_data.permissions_json["gaurdee_students"].append(student_data[0])
                await designation_data.save()

            parent_obj.user = user
            await parent_obj.save()
        update_dict = {}
        if gaurdian_type == GaurdianTypeEnum.father:
            update_dict["father_id"] = parent_obj.id
        if gaurdian_type == GaurdianTypeEnum.mother:
            update_dict["mother_id"] = parent_obj.id
        if parent_data.is_gaurdian:
            update_dict["gaurdian_id"] = parent_obj.id
            update_dict["gaurdian_relation"] = relation_with_kid if relation_with_kid is not None else gaurdian_type
        student_obj.update_from_dict(update_dict)
        await student_obj.save()
        if username is None:
            return {"parent_data": parent_obj.__dict__}
        else:
            return {
                "parent_data": parent_obj.__dict__,
                "login_credentials": {"username": username, "password": password}
            }
    return await do()

@router.get("/listParentAndGaurdianDetails", response_model=StudentWithParentDataTypeOut)
async def list_all_students_of_gaurdian(
    student_id: int,
    admin_id: int,
    token_data: union_of_all_permission_types=Depends(can_view_student)
):
    student = await models.Student.get(id=student_id, admin_id=admin_id, active=True).prefetch_related(
        "father", "mother", "gaurdian"
    )
    data = {"student_data": student.__dict__, "parent_and_gaurdians": []}
    father = await student.father
    if father is not None:
        data["parent_and_gaurdians"].append(father.__dict__)
        data["parent_and_gaurdians"][-1]["relation_with_kid"]="father"

    mother = await student.mother
    if father is not None:
        data["parent_and_gaurdians"].append(mother.__dict__)
        data["parent_and_gaurdians"][-1]["relation_with_kid"]="mother"

    gaurdian = await student.gaurdian
    if father is not None:
        data["parent_and_gaurdians"].append(gaurdian.__dict__)
        data["parent_and_gaurdians"][-1]["relation_with_kid"]="gaurdian"
    return data

@router.put("/editParentGaurdian", response_model=ParentGaurdianCreateDataTypeOut)
async def edit_parent_gaurdian_details(
    gaurdian_data: ParentGaurdianDatatype,
    parent_id: int = Body(embed=True, description="Gaurdian Id or ParentID"),
    student_id: int = Body(embed=True),
    admin_id: int = Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_add_student)
):
    '''
    If new gaurdian is added, it will replace the old gaurdian.
    '''
    data = gaurdian_data.dict()
    data["updated_by_id"]=token_data.user_id
    @atomic()
    async def do():
        parentobj = await models.ParentGaurdian.get(id=parent_id, active=True).prefetch_related("user")
        studentobj = await models.Student.get(id=student_id, admin_id=admin_id, active=True).prefetch_related(
            "gaurdian"
        )

        username=None
        password=None
        if gaurdian_data.is_gaurdian and not parentobj.is_gaurdian:
            gaurdianobj = await studentobj.gaurdian
            if gaurdianobj is not None:
                try:
                    old_designation = await models.Designation.get(
                        role_instance_id = await studentobj.gaurdian.id,
                        role = models.RolesEnum.parentgaurdian,
                        active=True
                    )
                    permissions_json_old:ParentGaurdianPermissionJsonType = old_designation.permissions_json
                    gaurdee_students = []
                    for i, stdt in enumerate(permissions_json_old.gaurdee_students):
                        if stdt.student_id!=i:
                            gaurdee_students.append(stdt)
                    permissions_json_old.gaurdee_students = gaurdee_students
                    old_designation.permissions_json=permissions_json_old.dict()
                    await old_designation.save()
                    gaurdian = await studentobj.gaurdian
                    gaurdian.is_gaurdian=False
                    await gaurdian.save()
                except:
                    pass

            if await parentobj.user is None:
                dob = parentobj.date_of_birth
                password, hashed_password= create_password_from_dob(dob)
                username = parentobj.phone_number.strip()
                user = await models.UserDB.create(username=username, password=hashed_password)
                permission_json=ParentGaurdianPermissionJsonType()
                student_data = await models.Student.filter(id=student_id, admin_id=admin_id, active=True).values(
                    admin_id="admin_id",
                    super_admin_id="admin__super_admin_id",
                    student_id="id",
                    first_name="first_name",
                    middle_name="middle_name",
                    last_name="last_name"
                )
                permission_json.gaurdee_students.append(student_data[0])
                await models.Designation.create(
                    user_id=user.user_id,
                    role=models.RolesEnum.parentgaurdian,
                    role_instance_id=parentobj.id,
                    designation=DesignationManager.role_designation_map[models.RolesEnum.parentgaurdian].gaurdian,
                    permissions_json=permission_json.dict()
                )
                data["user_id"]=user.user_id
            else:
                designation_data=await models.Designation.get(
                    user_id=await parentobj.user.id,
                    role=models.RolesEnum.parentgaurdian,
                    active=True
                )
                student_data = await models.Student.filter(id=student_id, admin_id=admin_id, active=True).values(
                    admin_id="admin_id",
                    super_admin_id="admin__super_admin_id",
                    student_id="id",
                    first_name="first_name",
                    middle_name="middle_name",
                    last_name="last_name"
                )
                designation_data.permissions_json["gaurdee_students"].append(student_data[0])
                await designation_data.save()
                
        parentobj.update_from_dict(data)
        if parentobj.is_gaurdian:
            studentobj.gaurdian=parentobj
        await studentobj.save()
        await parentobj.save()
        if username is None:
            return {"parent_data": parentobj.__dict__}
        else:
            return {
                "parent_data": parentobj.__dict__,
                "login_credentials": {"username": username, "password": password}
            }
    return await do()