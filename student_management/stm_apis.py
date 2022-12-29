from fastapi import APIRouter, Body, Depends
from permission_management.base_permission import union_of_all_permission_types, StudentPermissionJsonType
from db_management.designations import DesignationManager
from db_management import models
from .stm_datatypes import StudentDataType, CreateStudentOutDataType, StudentDataTypeOut, StudentClassSectionDataType
from permission_management.student_permissions import can_add_student, can_view_list_of_students, can_view_student
from typing import List, Optional
from fastapi.exceptions import HTTPException
from db_management.designations import DesignationManager
import datetime
from tortoise.transactions import atomic
from auth.auth_logic import create_password_from_dob
from typing import List
from project.shared.common_datatypes import SuccessReponse

router = APIRouter()

@router.post("/addNewStudent", response_model=CreateStudentOutDataType)
async def add_new_student(
    student_data: StudentDataType,
    username: str=Body(embed=True),
    admin_id: int = Body(embed=True),
    section_id: int = Body(embed=True),
    subject_ids: List[int]=Body(default=[], embed=True, description="Subject IDs of subjects available in class section."),
    designation: DesignationManager.role_designation_map["student"]=Body(embed=True),
    designation_start_time: Optional[datetime.datetime]=Body(default=None, embed=True),
    token_data: union_of_all_permission_types=Depends(can_add_student)
):
    available_subjects = set(await models.SectionSubject.filter(
        section_id=section_id,
        admin_id=admin_id,
        active=True).values_list("subject_id", flat=True))
    set_subject_ids = set(subject_ids)
    if len(set_subject_ids.difference(available_subjects))>0:
        raise HTTPException(406, {"detail": "Invalid Subject IDs.", "subject_ids": set_subject_ids.difference(available_subjects)})
    
    if await models.UserDB.exists(username=username):
        raise HTTPException(406, "User already exists.")

    @atomic()
    async def do():
        dob = student_data.date_of_birth
        password, hashed_password = create_password_from_dob(dob)
        user = await models.UserDB.create(username=username, password=hashed_password)
        student = await models.Student.create(
            user_id=user.user_id, **student_data.dict(), updated_by_id = token_data.user_id, admin_id=admin_id
        )
        designationobj = await models.Designation.create(
            designation=designation,
            user_id=user.user_id,
            role = models.RolesEnum.student,
            role_instance_id = student.id,
            from_time = designation_start_time,
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
    current: Optional[bool]=True,
    semester_id: Optional[int]=None,
    token_data: union_of_all_permission_types = Depends(can_view_list_of_students)
):
    '''
    If current is True, it will fetch all students of section of current semester. Else given semester id will be used.
    '''
    if not current and not semester_id:
        raise HTTPException(406, "current and semester id both can not be negative.")
    if current:
        student_class = await models.ClassSectionSemester.get(
            section_id=section_id, admin_id=admin_id, active=True, semester__current=True
            ).prefetch_related('students_of_class')
    else:
        student_class = await models.ClassSectionSemester.get(
            section_id=section_id, admin_id=admin_id, active=True, semester_id = semester_id
            ).prefetch_related('students_of_class')

    student_ids = await student_class.students_of_class.filter(active=True).values_list('student_id', flat=True)
    return await models.Student.filter(id__in=list(student_ids), active=True).values()

@router.get("/getStudentData", response_model=StudentDataTypeOut)
async def get_student_data(
    student_id: int,
    token_data: union_of_all_permission_types=Depends(can_view_student)
):
    return await models.Student.get(id=student_id, active=True, blocked=False).values()

@router.put("/updateStudentProfileData", response_model=StudentDataTypeOut)
async def update_student_profile_data(
    student_data: StudentDataType,
    student_id: int=Body(embed=True),
    admin_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_add_student)
):
    await models.Student.filter(id=student_id, admin_id=admin_id, active=True, blocked=False).update(
        **student_data.dict(),
        updated_by_id=token_data.user_id
    )
    return await models.Student.filter(id=student_id, admin_id=admin_id, active=True, blocked=False).values()

@router.delete("/disableStudent", response_model=SuccessReponse)
async def disable_student(
    student_id: int=Body(embed=True),
    admin_id: int=Body(embed=True),
    token_data: union_of_all_permission_types=Depends(can_add_student)
):
    await models.Student.filter(id=student_id, admin_id=admin_id).update(
        active=False,
        updated_by_id = token_data.user_id
    )

# @router.post("/changeClassOrSectionOfStudent")
# async def change_class_or_section_of_student(
#     section_data: StudentClassSectionDataType,
#     student_id: int = Body(embed=True),
#     admin_id: int = Body(embed=True),
#     token_data: union_of_all_permission_types=Depends(can_add_student)
# ):
#     '''
#     This API will have different effects in different scenarios.
#     1) Switching classes or sections within semesters will just update and old record will not be saved.
#     2) Switch classes or sections across semesters or academic sessions will hold old data in db and create new one.
#     '''
#     #Change monitor or vice monitor status to false.
#     #Check if academic sessions changed.