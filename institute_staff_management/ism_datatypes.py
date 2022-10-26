from typing import List, Optional
from tortoise.contrib.pydantic import pydantic_model_creator
from db_management.db_enums import EducationLevelEnum, EducationStatusEnum
from db_management.designations import DesignationManager
from db_management.models import InstituteStaff, RolesEnum
from pydantic import BaseModel
from pydantic import validator
from fastapi import HTTPException

from permission_management.base_permission import InstituteStaffPermissionReturnType

institute_staff_data_type = pydantic_model_creator(InstituteStaff, exclude_readonly=True)
institute_staff_data_type_out = pydantic_model_creator(InstituteStaff)

class DesignationDataTypeForInstituteStaff(BaseModel):
    designation: DesignationManager.role_designation_map[RolesEnum.institutestaff]
    permissions_json: InstituteStaffPermissionReturnType

class EducationDetailDataType(BaseModel):
    level: EducationLevelEnum
    course: str
    semester_or_year: int
    year: int
    institute_name: str
    board_or_university: str
    status: EducationStatusEnum
    subjects: List[str]
    grade: Optional[str] = None
    maximum_marks: Optional[int] = None
    obtained_marks: Optional[int] = None    
    docurl: Optional[str] = None
    roll_number: Optional[int] = None
    active: bool = True

    @validator('obtained_marks')
    def validate_status_marks_grade(cls, v, values, **kwargs):
        if values["status"] == EducationStatusEnum.passed and ((v is not None and values["maximum_marks"] is not None) or values["grade"] is not None):
            return v
        if values["status"] == EducationStatusEnum.appearing and (v is None and values["maximum_marks"] is None and values["grade"] is None):
            return v
        raise HTTPException(406, "If status is passed, pass at least grade or marks. If status is failed, grade and marks must be null.")

    @validator('obtained_marks')
    def validate_marks(cls, v, values, **kwargs):
        if v is None and values["maximum_marks"] is not None:
            raise HTTPException(406, "Either both obtained and maximum marks should be null or not null.")
        if v is not None and values["maximum_marks"] is None:
            raise HTTPException(406, "Either both obtained and maximum marks should be null or not null.")
        if v is not None and v > values["maximum_marks"]:
            raise HTTPException(406, "Invalid Obtained or maximum marks.")
        return v

    @validator('subjects')
    def validate_subjects(cls, v, values):
        if len(v) == 0:
            raise HTTPException(406, "Please pass the subjects.")
        return v

    @validator('roll_number')
    def validate_roll_number(cls, v, values):
        if v is None and values["status"] != EducationStatusEnum.appearing:
            raise HTTPException(406, "Please fill the roll number.")
        return v

    @validator('semester_or_year')
    def validate_sem_or_year(cls, v, values):
        if v < 0:
            raise HTTPException(406, "Please fill the valid semester or year.")
        return v

    @validator('year')
    def validate_year(cls, v, values):
        if v < 1950:
            raise HTTPException(406, "Please fill the valid semester or year.")
        return v