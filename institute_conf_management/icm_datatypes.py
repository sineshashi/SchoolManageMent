from pydantic import BaseModel, validator
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Optional
import datetime
from db_management.models import AcademicSessionAndSemester


class SubjectGroupDepartMentDataType(BaseModel):
    group_name: str
    head_id: int
    vice_head_id: int


class SubjectDataType(BaseModel):
    subject_name: str
    head_id: int
    vice_head_id: int


class ClassGroupDataType(BaseModel):
    group_name: str
    head_id: int
    vice_head_id: int


class ClassDataType(BaseModel):
    class_name: str
    head_id: int
    vice_head_id: int
    subject_ids: List[int] = []


class AcademicSessionSemesterDataType(BaseModel):
    '''
    semester_number = 0 means semester is not applicable in the school.
    '''
    academic_session_start_year: int
    academic_session_end_year: int
    academic_session_start_date: Optional[datetime.date] = None
    semester_number: Optional[int] = 0
    semester_start_date: Optional[datetime.date] = None
    semester_end_date: Optional[datetime.date] = None

    @validator('semester_start_date')
    def validate_semester_date(cls, v, values, **kwargs):
        assert not (v is not None and (
            'semester_number' not in values or values['semester_number'] == 0))
        return v

    @validator('semester_end_date')
    def validate_semester_end_date(cls, v, values, **kwargs):
        assert not (v is not None and (
            'semester_number' not in values or values['semester_number'] == 0 or 'semester_start_date' not in values or values['semester_start_date'] is None))
        return v

AcademicSessionAndSemesterDataTypeInDB = pydantic_model_creator(AcademicSessionAndSemester)